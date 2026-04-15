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
    confluence_def_list = list_[anydict]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class ConfluenceExporter:

    def __init__(self, exporter) -> 'None':
        self.exporter = exporter

    def export(self, items) -> 'confluence_def_list':
        """ Exports Confluence connection definitions.
        """
        logger.info('Exporting Confluence connection definitions')

        if not items:
            logger.info('No Confluence connection definitions found')
            return []

        logger.debug('Processing %d Confluence connection definitions', len(items))

        exported_confluence = []

        for row in items:

            item = {
                'name': row['name'],
                'username': row.get('username', ''),
                'address': row.get('address', ''),
                'api_version': row.get('api_version', ''),
                'is_active': row.get('is_active', True),
            }

            if site_url := row.get('site_url'):
                item['site_url'] = site_url

            if row.get('is_cloud') is True:
                item['is_cloud'] = True

            if (pool_size := row.get('pool_size')) and pool_size != 10:
                item['pool_size'] = pool_size

            if (timeout := row.get('timeout')) and timeout != 600:
                item['timeout'] = timeout

            exported_confluence.append(item)

        logger.info('Successfully prepared %d Confluence connection definitions for export', len(exported_confluence))
        return exported_confluence

# ################################################################################################################################
# ################################################################################################################################
