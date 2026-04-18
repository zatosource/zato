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
    channel_def_list = list_[anydict]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class ChannelExporter:

    def __init__(self, exporter) -> 'None':
        self.exporter = exporter

    def export(self, items) -> 'channel_def_list':
        """ Exports REST Channel definitions.
        """
        logger.info('Exporting REST channel definitions')

        if not items:
            logger.info('No REST Channel definitions found')
            return []

        exported_channels = []
        logger.info('Processing %d REST Channel definitions', len(items))

        for channel_row in items:

            # Skip internal channels
            if channel_row.get('is_internal'):
                continue

            exported_channel = {
                'name': channel_row['name'],
                'service': channel_row.get('service_name') or channel_row.get('service', ''),
                'url_path': channel_row.get('url_path', ''),
            }

            if security_name := channel_row.get('security') or channel_row.get('security_name'):
                exported_channel['security'] = security_name

            data_format = channel_row.get('data_format')
            if data_format and data_format != 'json':
                exported_channel['data_format'] = data_format

            groups = channel_row.get('groups')
            if groups:
                if isinstance(groups, list) and groups:
                    exported_channel['groups'] = groups

            method = channel_row.get('method')
            if method and method != 'GET':
                exported_channel['method'] = method

            if channel_row.get('content_type'):
                exported_channel['content_type'] = channel_row['content_type']

            if channel_row.get('content_encoding'):
                exported_channel['content_encoding'] = channel_row['content_encoding']

            gateway_service_list = channel_row.get('gateway_service_list')
            if gateway_service_list:
                if isinstance(gateway_service_list, str) and gateway_service_list.strip():
                    exported_channel['gateway_service_list'] = gateway_service_list.strip().split('\n')
                elif isinstance(gateway_service_list, list) and gateway_service_list:
                    exported_channel['gateway_service_list'] = gateway_service_list

            exported_channels.append(exported_channel)

        logger.info('Successfully prepared %d REST Channel definitions for export', len(exported_channels))
        return exported_channels

# ################################################################################################################################
# ################################################################################################################################
