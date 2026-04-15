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
    odoo_def_list = list_[anydict]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class OdooExporter:

    def __init__(self, exporter) -> 'None':
        self.exporter = exporter

    def export(self, items) -> 'odoo_def_list':
        """ Exports Odoo connection definitions.
        """
        logger.info('Exporting Odoo connection definitions')

        if not items:
            logger.info('No Odoo connection definitions found')
            return []

        logger.debug('Processing %d Odoo connection definitions', len(items))

        exported_odoo_connections = []

        for row in items:
            item = {
                'name': row['name'],
                'host': row.get('host', ''),
                'port': row.get('port', 0),
                'user': row.get('user', ''),
                'database': row.get('database', ''),
            }

            if protocol := row.get('protocol'):
                item['protocol'] = protocol

            if (pool_size := row.get('pool_size')) and pool_size != 10:
                item['pool_size'] = pool_size

            for field in ['timeout', 'api_client']:
                if field in row and row[field]:
                    item[field] = row[field]

            exported_odoo_connections.append(item)

        logger.info('Successfully prepared %d Odoo connection definitions for export', len(exported_odoo_connections))

        return exported_odoo_connections

# ################################################################################################################################
# ################################################################################################################################
