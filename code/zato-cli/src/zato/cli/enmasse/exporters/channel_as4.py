# -*- coding: utf-8 -*-
"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from json import loads

# Zato
from zato.common.api import AS4, CONNECTION, URL_TYPE
from zato.common.odb.model import to_json
from zato.common.odb.query import http_soap_list

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.cli.enmasse.exporter import EnmasseYAMLExporter
    from zato.common.typing_ import anydict, list_

    channel_as4_def_list = list_[anydict]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class ChannelAS4Exporter:

    def __init__(self, exporter: 'EnmasseYAMLExporter') -> 'None':
        self.exporter = exporter

    def export(self, session: 'SASession', cluster_id: 'int') -> 'channel_as4_def_list':
        """ Exports AS4 channel definitions.
        """
        logger.info('Exporting AS4 channel definitions')

        # Get AS4 channels from database
        db_channels = http_soap_list(
            session,
            cluster_id,
            connection=CONNECTION.CHANNEL,
            transport=URL_TYPE.AS4,
            return_internal=False,
        )
        db_channels = to_json(db_channels)

        if not db_channels:
            logger.info('No AS4 channel definitions found in DB')
            return []

        exported_channels: 'channel_as4_def_list' = []
        logger.info('Processing %d AS4 channel definitions', len(db_channels))

        for channel_row in db_channels:
            logger.debug('Processing AS4 channel row %s', channel_row)

            exported_channel: 'anydict' = {
                'name': channel_row['name'],
                'url_path': channel_row['url_path'],
            }

            # The routing service is optional - without one the channel routes to a topic.
            if service_name := channel_row.get('service_name'):
                exported_channel['service'] = service_name

            if security_name := channel_row.get('security_name'):
                exported_channel['security'] = security_name

            # Unpack the opaque attributes carrying the AS4 fields.
            opaque = {}
            if opaque1 := channel_row.get('opaque1'):
                opaque = loads(opaque1) or {}

            # Every AS4 field with a value is exported under its own name.
            for name in AS4.Common_Fields + AS4.Channel_Fields:
                if value := opaque.get(name):
                    exported_channel[name] = value

            exported_channels.append(exported_channel)

        logger.info('Successfully prepared %d AS4 channel definitions for export', len(exported_channels))
        return exported_channels

# ################################################################################################################################
# ################################################################################################################################
