# -*- coding: utf-8 -*-
"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from contextlib import closing

# SQLAlchemy
from sqlalchemy import and_, select

# Zato
from zato.common.api import CONNECTION, Groups, MISC, URL_TYPE
from zato.common.odb.model import GenericObject, to_json
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
        self.group_id_to_name = {}

    def _load_security_groups(self, session:'SASession', cluster_id:'int') -> 'None':
        """Load security groups from the database and build an ID to name mapping.
        """
        # Clear existing mapping
        self.group_id_to_name = {}

        # Use a direct SQLAlchemy query to get all groups
        with closing(session) as session:
            # Build a query for all groups
            query = select([
                GenericObject.id,
                GenericObject.name
            ]).where(and_(
                GenericObject.type_ == Groups.Type.Group_Parent,
                GenericObject.subtype == Groups.Type.API_Clients,
                GenericObject.cluster_id == cluster_id,
            ))

            # Execute the query and get results
            groups = session.execute(query).fetchall()

            # Build ID to name mapping
            for group in groups:
                self.group_id_to_name[group['id']] = group['name']

        logger.info('Loaded %d security groups', len(self.group_id_to_name))

    def export(self, session: 'SASession', cluster_id: 'int') -> 'channel_def_list':
        """ Exports REST Channel definitions.
        """
        logger.info('Exporting REST channel definitions')

        # Load security groups for ID to name conversion
        self._load_security_groups(session, cluster_id)

        # Get channels from database
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

            logger.debug('Processing REST channel row %s', channel_row.toDict())

            exported_channel: 'anydict' = {
                'name': channel_row.name,
                'service': channel_row.service_name,
                'url_path': channel_row.url_path,
            }

            # Add security definition if present
            if channel_row.security_name:
                exported_channel['security'] = channel_row.security_name

            # Add data_format if not None and not json
            if channel_row.data_format and channel_row.data_format != 'json':
                exported_channel['data_format'] = channel_row.data_format

            # Export security groups directly assigned to the channel
            if security_groups := channel_row.get('security_groups'):
                # Convert group IDs to names
                group_names = []
                for group_id in security_groups:
                    if group_id in self.group_id_to_name:
                        group_names.append(self.group_id_to_name[group_id])
                    else:
                        logger.warning('Security group ID %s not found for channel %s', group_id, channel_row.name)

                # Only add groups if there are any
                if group_names:
                    exported_channel['groups'] = group_names

            if channel_row.method and channel_row.method != MISC.DEFAULT_HTTP_METHOD:
                exported_channel['method'] = channel_row.method

            if channel_row.timeout is not None and channel_row.timeout != MISC.DEFAULT_HTTP_TIMEOUT:
                exported_channel['timeout'] = channel_row.timeout

            if channel_row.content_type:
                exported_channel['content_type'] = channel_row.content_type

            if channel_row.content_encoding:
                exported_channel['content_encoding'] = channel_row.content_encoding

            exported_channels.append(exported_channel)

        logger.info('Successfully prepared %d REST Channel definitions for export', len(exported_channels))
        return exported_channels

# ################################################################################################################################
# ################################################################################################################################
