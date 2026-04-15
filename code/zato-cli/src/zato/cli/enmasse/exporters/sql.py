# -*- coding: utf-8 -*-
"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, list_
    sql_def_list = list_[anydict]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class SQLExporter:

    def __init__(self, exporter) -> 'None':
        self.exporter = exporter

    def export(self, items) -> 'sql_def_list':
        """ Exports SQL connection pool definitions.
        """
        logger.info('Exporting SQL connection pool definitions')

        if not items:
            logger.info('No SQL connection pool definitions found')
            return []

        logger.debug('Processing %d SQL connection pool definitions', len(items))

        exported_sql_connections = []

        for row in items:

            item = {
                'name': row['name'],
                'type': row.get('engine_type') or row.get('type') or row.get('engine', ''),
                'host': row.get('host', ''),
                'port': row.get('port', 0),
                'db_name': row.get('db_name', ''),
                'username': row.get('username', ''),
            }

            if extra := row.get('extra'):
                extra = extra.decode('utf8') if isinstance(extra, bytes) else extra
                if isinstance(extra, str) and extra.strip():
                    item['extra'] = extra.splitlines()
                elif isinstance(extra, list):
                    item['extra'] = extra

            if (pool_size := row.get('pool_size')) and pool_size != 10:
                item['pool_size'] = pool_size

            if timeout := row.get('timeout'):
                item['timeout'] = timeout

            exported_sql_connections.append(item)

        logger.info('Successfully prepared %d SQL connection pool definitions for export', len(exported_sql_connections))

        return exported_sql_connections

# ################################################################################################################################
# ################################################################################################################################
