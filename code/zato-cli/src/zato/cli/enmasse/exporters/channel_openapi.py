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
    channel_openapi_def_list = list_[anydict]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class ChannelOpenAPIExporter:

    def __init__(self, exporter) -> 'None':
        self.exporter = exporter

    def export(self, items) -> 'channel_openapi_def_list':
        """ Exports OpenAPI channel definitions.
        """
        logger.info('Exporting OpenAPI channel definitions')

        if not items:
            logger.info('No OpenAPI channel definitions found')
            return []

        logger.debug('Processing %d OpenAPI channel definitions', len(items))

        exported = []

        for row in items:

            item = {
                'name': row['name'],
                'is_active': row.get('is_active', True),
                'url_path': row.get('url_path', ''),
            }

            rest_channel_list = row.get('rest_channel_list') or []
            if rest_channel_list:
                item['rest_channel_list'] = rest_channel_list

            exported.append(item)

        logger.info('Successfully prepared %d OpenAPI channel definitions for export', len(exported))
        return exported

# ################################################################################################################################
# ################################################################################################################################
