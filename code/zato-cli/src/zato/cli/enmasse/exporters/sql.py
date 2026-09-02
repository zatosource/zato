# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.cli.enmasse.util import get_type_from_engine, SQL_Default_Pool_Size
from zato.common.odb.model import to_json
from zato.common.odb.query import out_sql_list
from zato.common.util.sql import parse_instance_opaque_attr

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.cli.enmasse.exporter import EnmasseYAMLExporter
    from zato.common.typing_ import anydict, list_

    sql_def_list = list_[anydict]

    # Add dummy assignments to satisfy type checkers
    SASession = SASession
    EnmasseYAMLExporter = EnmasseYAMLExporter

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# What the audit level of a connection that is not audited is stored as.
_audit_log_off = 'off'

# The SSL fields that travel along whenever SSL is enabled for a connection.
_ssl_fields = ('ssl_ca_file', 'ssl_cert_file', 'ssl_key_file', 'ssl_verify')

# ################################################################################################################################
# ################################################################################################################################

class SQLExporter:
    """ Exports SQL connection pool definitions to their enmasse form.
    """

    def __init__(self, exporter:'EnmasseYAMLExporter') -> 'None':
        self.exporter = exporter

# ################################################################################################################################

    def export(self, session:'SASession', cluster_id:'int') -> 'sql_def_list':
        """ Exports SQL connection pool definitions.
        """
        logger.info('Exporting SQL connection pool definitions')

        # Our response to produce
        out = []

        db_sql_connections = out_sql_list(session, cluster_id)

        if not db_sql_connections:
            logger.info('No SQL connection pool definitions found in DB')
            return out

        sql_connections = to_json(db_sql_connections, return_as_dict=True)
        logger.debug('Processing %d SQL connection pool definition(s)', len(sql_connections))

        for row in sql_connections:

            # The basic fields every connection carries ..
            engine = row['engine']
            connection_type = get_type_from_engine(engine)

            item = {
                'name': row['name'],
                'type': connection_type,
                'host': row['host'],
                'port': row['port'],
                'db_name': row['db_name'],
                'username': row['username']
            }

            # .. the extra options are stored as one newline-separated string
            # .. while YAML files carry them as a list ..
            extra = row['extra']

            if extra:
                extra = extra.decode('utf8')
                if extra.strip():
                    item['extra'] = extra.splitlines()

            # .. the pool size travels only if it differs from the default ..
            pool_size = row['pool_size']

            if pool_size:
                if pool_size != SQL_Default_Pool_Size:
                    item['pool_size'] = pool_size

            # .. the timeout, the SSL/TLS configuration and the audit level are kept in the opaque attributes ..
            opaque = parse_instance_opaque_attr(row)

            # .. the timeout travels only if the definition carries one ..
            if timeout := opaque.get('timeout'):
                item['timeout'] = timeout

            # .. a connection that is not audited says nothing about it in its YAML ..
            if audit_log := opaque.get('audit_log'):
                if audit_log != _audit_log_off:
                    item['audit_log'] = audit_log

            # .. the SSL fields travel only if SSL is enabled at all ..
            if ssl := opaque.get('ssl'):
                item['ssl'] = ssl

                for ssl_key in _ssl_fields:
                    if ssl_key in opaque:
                        item[ssl_key] = opaque[ssl_key]

            # .. and the definition is ready now.
            out.append(item)

        logger.info('Successfully prepared %d SQL connection pool definition(s) for export', len(out))

        return out

# ################################################################################################################################
# ################################################################################################################################
