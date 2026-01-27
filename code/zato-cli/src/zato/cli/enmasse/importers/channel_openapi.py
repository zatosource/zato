# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.cli.enmasse.util import preprocess_item
from zato.common.api import CONNECTION, GENERIC, URL_TYPE
from zato.common.odb.model import GenericConn, HTTPSOAP, to_json
from zato.common.odb.query.generic import connection_list
from zato.common.util.sql import set_instance_opaque_attrs

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.cli.enmasse.importer import EnmasseYAMLImporter
    from zato.common.typing_ import any_, anydict, anylist, listtuple

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class ChannelOpenAPIImporter:

    connection_type = GENERIC.CONNECTION.TYPE.CHANNEL_OPENAPI

    connection_defaults = {
        'is_active': True,
        'type_': GENERIC.CONNECTION.TYPE.CHANNEL_OPENAPI,
        'is_internal': False,
        'is_channel': True,
        'is_outconn': False,
        'is_outgoing': False,
        'pool_size': 20,
        'recv_timeout': 250,
    }

    def __init__(self, importer:'EnmasseYAMLImporter') -> 'None':
        self.importer = importer
        self.channel_openapi_defs = {}

# ################################################################################################################################

    def _process_defs(self, query_result:'any_', out:'dict') -> 'None':
        definitions = to_json(query_result, return_as_dict=True)
        logger.info('Processing %d OpenAPI channel definitions', len(definitions))

        for item in definitions:
            name = item['name']
            logger.info('Processing OpenAPI channel definition: %s (id=%s)', name, item.get('id'))
            out[name] = item

# ################################################################################################################################

    def get_defs_from_db(self, session:'SASession', cluster_id:'int') -> 'anydict':
        out = {}

        logger.info('Retrieving OpenAPI channel definitions from database')
        connections = connection_list(session, cluster_id, self.connection_type, False)

        self._process_defs(connections, out)
        logger.info('Total OpenAPI channel definitions from DB: %d', len(out))

        return out

# ################################################################################################################################

    def _get_rest_channels_map(self, session:'SASession', cluster_id:'int') -> 'dict':
        result = session.query(HTTPSOAP).filter(
            HTTPSOAP.cluster_id == cluster_id,
            HTTPSOAP.connection == CONNECTION.CHANNEL,
            HTTPSOAP.transport == URL_TYPE.PLAIN_HTTP,
        ).all()

        return {item.name: item.id for item in result}

# ################################################################################################################################

    def compare_defs(self, yaml_defs:'anylist', db_defs:'anydict') -> 'tuple':
        to_create = []
        to_update = []

        for yaml_def in yaml_defs:
            yaml_def = preprocess_item(yaml_def)
            name = yaml_def['name']

            if name in db_defs:
                update_def = yaml_def.copy()
                update_def['id'] = db_defs[name]['id']
                logger.info('Adding to update: %s', update_def)
                to_update.append(update_def)
            else:
                logger.info('Adding to create: %s', yaml_def)
                to_create.append(yaml_def)

        return to_create, to_update

# ################################################################################################################################

    def create_definition(self, channel_def:'anydict', session:'SASession', rest_channels_map:'dict') -> 'any_':
        cluster = self.importer.get_cluster(session)

        connection = GenericConn()
        connection.cluster = cluster

        for key, default_value in self.connection_defaults.items():
            value = channel_def.get(key, default_value)
            setattr(connection, key, value)

        connection.name = channel_def['name']
        connection.is_active = channel_def.get('is_active', True)

        rest_channel_id_list = []
        rest_channel_list = channel_def.get('rest_channel_list') or []
        for channel_name in rest_channel_list:
            if channel_id := rest_channels_map.get(channel_name):
                rest_channel_id_list.append(channel_id)
            else:
                logger.warning('REST channel not found: %s', channel_name)

        extra_fields = {
            'url_path': channel_def.get('url_path', ''),
            'rest_channel_id_list': rest_channel_id_list,
        }

        merged_def = channel_def.copy()
        merged_def.update(extra_fields)

        set_instance_opaque_attrs(connection, merged_def)

        session.add(connection)
        session.flush()

        return connection

# ################################################################################################################################

    def update_definition(self, channel_def:'anydict', session:'SASession', rest_channels_map:'dict') -> 'any_':
        connection_id = channel_def['id']
        def_name = channel_def['name']

        logger.info('Updating OpenAPI channel definition: name=%s id=%s', def_name, connection_id)

        connection = session.query(GenericConn).filter_by(id=connection_id).one()

        connection.name = channel_def['name']
        if 'is_active' in channel_def:
            connection.is_active = channel_def['is_active']

        rest_channel_id_list = []
        rest_channel_list = channel_def.get('rest_channel_list') or []
        for channel_name in rest_channel_list:
            if channel_id := rest_channels_map.get(channel_name):
                rest_channel_id_list.append(channel_id)
            else:
                logger.warning('REST channel not found: %s', channel_name)

        extra_fields = {
            'url_path': channel_def.get('url_path', ''),
            'rest_channel_id_list': rest_channel_id_list,
        }

        merged_def = channel_def.copy()
        merged_def.update(extra_fields)

        set_instance_opaque_attrs(connection, merged_def)

        session.add(connection)
        return connection

# ################################################################################################################################

    def sync_channel_openapi(self, channel_list:'anylist', session:'SASession') -> 'listtuple':
        logger.info('Processing %d OpenAPI channel definitions from YAML', len(channel_list))

        db_defs = self.get_defs_from_db(session, self.importer.cluster_id)
        to_create, to_update = self.compare_defs(channel_list, db_defs)

        rest_channels_map = self._get_rest_channels_map(session, self.importer.cluster_id)

        out_created = []
        out_updated = []

        try:
            logger.info('Creating %d new OpenAPI channel definitions', len(to_create))
            for item in to_create:
                existing_conn = session.query(GenericConn).filter(
                    GenericConn.name == item.get('name'),
                    GenericConn.type_ == self.connection_type
                ).first()

                if existing_conn:
                    logger.info('OpenAPI channel with name %s already exists, skipping', item.get('name'))
                    continue

                instance = self.create_definition(item, session, rest_channels_map)
                logger.info('Created OpenAPI channel definition: name=%s id=%s', instance.name, instance.id)
                out_created.append(instance)

                self.channel_openapi_defs[instance.name] = {
                    'id': instance.id,
                    'name': instance.name,
                }

            logger.info('Updating %d existing OpenAPI channel definitions', len(to_update))
            for item in to_update:
                instance = self.update_definition(item, session, rest_channels_map)
                logger.info('Updated OpenAPI channel definition: name=%s id=%s', instance.name, instance.id)
                out_updated.append(instance)

            logger.info('Committing changes: created=%d updated=%d', len(out_created), len(out_updated))
            session.commit()
            logger.info('Successfully committed all changes')

        except Exception as e:
            logger.error('Error syncing OpenAPI channel definitions: %s', e)
            logger.exception('Full exception details:')
            session.rollback()
            raise

        return out_created, out_updated

# ################################################################################################################################
# ################################################################################################################################
