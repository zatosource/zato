# -*- coding: utf-8 -*-
"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.cli.enmasse.util import get_type_from_engine
from zato.common.odb.model import to_json
from zato.common.odb.query import out_sql_list
from zato.common.util.sql import parse_instance_opaque_attr

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession

    from zato.cli.enmasse.exporter import EnmasseYAMLExporter
    from zato.common.odb.model import SQLConnectionPool
    from zato.common.typing_ import anydict, list_

    sql_def_list = list_[anydict]
    db_sql_list = list_[SQLConnectionPool]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class SQLExporter:

    def __init__(self, exporter:'EnmasseYAMLExporter') -> 'None':
        self.exporter = exporter

    def export(self, session:'SASession', cluster_id:'int') -> 'sql_def_list':
        """ Exports SQL connection pool definitions.
        """
        logger.info('Exporting SQL connection pool definitions')

        db_sql_connections = out_sql_list(session, cluster_id)

        if not db_sql_connections:
            logger.info('No SQL connection pool definitions found in DB')
            return []

        sql_connections = to_json(db_sql_connections, return_as_dict=True)
        logger.debug('Processing %d SQL connection pool definitions', len(sql_connections))

        exported_sql_connections = []

        for row in sql_connections:

            item = {
                'name': row['name'],
                'type': get_type_from_engine(row['engine']),
                'host': row['host'],
                'port': row['port'],
                'db_name': row['db_name'],
                'username': row['username']
            }

            if extra := row.get('extra'):
                extra = extra.decode('utf8') if isinstance(extra, bytes) else extra
                if extra.strip():
                    item['extra'] = extra.splitlines()

            if (pool_size := row.get('pool_size')) and pool_size != 10:
                item['pool_size'] = pool_size

            if timeout := row.get('timeout'):
                item['timeout'] = timeout

            exported_sql_connections.append(item)

        logger.info('Successfully prepared %d SQL connection pool definitions for export', len(exported_sql_connections))

        return exported_sql_connections

# ################################################################################################################################
# ################################################################################################################################
