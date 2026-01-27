# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.api import CONNECTION, GENERIC, URL_TYPE
from zato.common.odb.model import HTTPSOAP, to_json
from zato.common.odb.query.generic import connection_list
from zato.common.util.sql import parse_instance_opaque_attr

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.cli.enmasse.exporter import EnmasseYAMLExporter
    from zato.common.typing_ import anydict, list_

    channel_openapi_def_list = list_[anydict]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class ChannelOpenAPIExporter:

    def __init__(self, exporter:'EnmasseYAMLExporter') -> 'None':
        self.exporter = exporter

    def export(self, session:'SASession', cluster_id:'int') -> 'channel_openapi_def_list':
        logger.info('Exporting OpenAPI channel definitions')

        db_channels = connection_list(session, cluster_id, GENERIC.CONNECTION.TYPE.CHANNEL_OPENAPI)

        if not db_channels:
            logger.info('No OpenAPI channel definitions found in DB')
            return []

        channels = to_json(db_channels, return_as_dict=True)
        logger.debug('Processing %d OpenAPI channel definitions', len(channels))

        rest_channels_by_id = self._get_rest_channels_map(session, cluster_id)

        exported = []

        for row in channels:
            if GENERIC.ATTR_NAME in row:
                opaque = parse_instance_opaque_attr(row)
                row.update(opaque)
                del row[GENERIC.ATTR_NAME]

            item = {
                'name': row['name'],
                'is_active': row['is_active'],
                'url_path': row.get('url_path', ''),
            }

            rest_channel_id_list = row.get('rest_channel_id_list') or []
            if rest_channel_id_list:
                rest_channel_list = []
                for channel_id in rest_channel_id_list:
                    if channel_name := rest_channels_by_id.get(channel_id):
                        rest_channel_list.append(channel_name)
                if rest_channel_list:
                    item['rest_channel_list'] = rest_channel_list

            exported.append(item)

        logger.info('Successfully prepared %d OpenAPI channel definitions for export', len(exported))
        return exported

    def _get_rest_channels_map(self, session:'SASession', cluster_id:'int') -> 'dict':
        result = session.query(HTTPSOAP).filter(
            HTTPSOAP.cluster_id == cluster_id,
            HTTPSOAP.connection == CONNECTION.CHANNEL,
            HTTPSOAP.transport == URL_TYPE.PLAIN_HTTP,
        ).all()

        return {item.id: item.name for item in result}

# ################################################################################################################################
# ################################################################################################################################
