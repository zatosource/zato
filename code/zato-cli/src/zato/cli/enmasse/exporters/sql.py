# -*- coding: utf-8 -*-
"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
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
        logger.info('Processing %d SQL connection pool definitions', len(sql_connections))

        exported_sql_connections = []

        for row in sql_connections:
            item = {
                'name': row['name'],
                'type': row['engine'],
                'host': row['host'],
                'port': row['port'],
                'db_name': row['db_name'],
                'username': row['username']
            }

            # Add optional fields if they exist and aren't empty
            for field in ['is_active', 'pool_size', 'timeout']:
                if field in row and row[field] is not None:
                    item[field] = row[field]

            # Handle the extra field (connection options)
            if 'extra' in row and row['extra']:
                try:
                    # Extra field might be bytes or string
                    extra_str = row['extra'].decode('utf8') if isinstance(row['extra'], bytes) else row['extra']
                    if extra_str.strip():
                        item['extra'] = extra_str
                except (UnicodeDecodeError, AttributeError):
                    # Skip on errors
                    pass

            # Process any opaque attributes
            if 'opaque_attr' in row and row['opaque_attr']:
                opaque = parse_instance_opaque_attr(row)
                item.update(opaque)

            # Note: We deliberately do not export passwords for security reasons

            exported_sql_connections.append(item)

        logger.info('Successfully prepared %d SQL connection pool definitions for export', len(exported_sql_connections))

        return exported_sql_connections

# ################################################################################################################################
# ################################################################################################################################
