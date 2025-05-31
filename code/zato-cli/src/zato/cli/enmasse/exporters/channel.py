# -*- coding: utf-8 -*-
"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.api import CONNECTION, URL_TYPE
from zato.common.odb.model import to_json
from zato.common.odb.query import http_soap_list
from zato.common.util.sql import elems_with_opaque

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.cli.enmasse.exporter import EnmasseYAMLExporter
    from zato.common.typing_ import anydict, list_

    channel_def_list = list_[anydict]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class ChannelExporter:

    def __init__(self, exporter: 'EnmasseYAMLExporter') -> 'None':
        self.exporter = exporter

    def export(self, session: 'SASession', cluster_id: 'int') -> 'channel_def_list':
        """ Exports REST Channel definitions.
        """
        logger.info('Exporting REST channel definitions')

        db_channels = http_soap_list(
            session,
            cluster_id,
            connection=CONNECTION.CHANNEL,
            transport=URL_TYPE.PLAIN_HTTP,
            return_internal=False,
        )
        db_channels = to_json(db_channels)

        if not db_channels:
            logger.info('No REST Channel definitions found in DB')
            return []

        # Extract opaque elements including security groups
        db_channels = elems_with_opaque(db_channels)

        exported_channels: 'channel_def_list' = []
        logger.info('Processing %d REST Channel definitions', len(db_channels))

        for channel_row in db_channels:

            logger.info('Processing REST channel row %s', channel_row.toDict())

            exported_channel: 'anydict' = {
                'name': channel_row.name,
                'url_path': channel_row.url_path,
                'service': channel_row.service_name,
            }

            if channel_row.security_name:
                exported_channel['security'] = channel_row.security_name

            # Export security groups directly assigned to the channel
            if security_groups := channel_row.get('security_groups'):
                exported_channel['groups'] = security_groups

            optional_fields_from_row = {
                'data_format': channel_row.data_format,
                'is_active': channel_row.is_active,
                'timeout': channel_row.timeout,
                'method': channel_row.method,
                'content_type': channel_row.content_type,
                'content_encoding': channel_row.content_encoding,
            }

            for field_name, field_value in optional_fields_from_row.items():
                if field_value is not None:
                    exported_channel[field_name] = field_value

            exported_channels.append(exported_channel)

        logger.info('Successfully prepared %d REST Channel definitions for export', len(exported_channels))
        return exported_channels

# ################################################################################################################################
# ################################################################################################################################
