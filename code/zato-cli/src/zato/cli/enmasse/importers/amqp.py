# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.cli.enmasse.util import preprocess_item
from zato.common.api import AMQP, AMQP_Subtype
from zato.common.crypto.api import CryptoManager
from zato.common.json_internal import dumps
from zato.common.odb.model import ChannelAMQP, OutgoingAMQP, Service, to_json
from zato.common.odb.query import channel_amqp_list, out_amqp_list

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

# The ODB stores delivery modes as AMQP integers, the YAML configuration uses these string names
_delivery_mode_by_name = {
    'non_persistent': 1,
    'persistent': 2,
}

_default_delivery_mode = _delivery_mode_by_name['persistent']
_default_frame_max = 131072
_default_heartbeat = 30

# ################################################################################################################################
# ################################################################################################################################

class ChannelAMQPImporter:
    """ One importer serves every subtype of the AMQP implementation - the importer is registered
    once per subtype, e.g. under the channel_amqp key and under the channel_azure_service_bus key.
    """

    def __init__(self, importer:'EnmasseYAMLImporter', subtype:'str') -> 'None':
        self.importer = importer
        self.subtype_key = subtype
        self.subtype = AMQP_Subtype[subtype]

# ################################################################################################################################

    def get_channels_from_db(self, session:'SASession', cluster_id:'int') -> 'anydict':
        out = {}

        label = self.subtype['label']
        logger.info('Retrieving %s channel definitions from database for cluster_id=%s', label, cluster_id)

        # Only channels of this importer's subtype are taken into account
        query_result = channel_amqp_list(session, cluster_id, self.subtype_key, False)
        definitions = to_json(query_result, return_as_dict=True)

        for item in definitions:
            name = item['name']
            logger.info('Processing %s channel definition: %s (id=%s)', label, name, item['id'])
            out[name] = item

        logger.info('Total %s channel definitions from DB: %d', label, len(out))

        return out

# ################################################################################################################################

    def compare_channels(self, yaml_defs:'anylist', db_defs:'anydict') -> 'tuple':

        # Find items to create and update
        to_create = []
        to_update = []

        for yaml_def in yaml_defs:
            yaml_def = preprocess_item(yaml_def)
            name = yaml_def['name']

            # Update an existing definition ..
            if name in db_defs:
                update_def = yaml_def.copy()
                update_def['id'] = db_defs[name]['id']
                to_update.append(update_def)

            # .. or create a new one.
            else:
                to_create.append(yaml_def)

        return to_create, to_update

# ################################################################################################################################

    def _get_service(self, channel_def:'anydict', session:'SASession') -> 'any_':
        """ Resolves the service that the channel invokes for each message received.
        """
        service_name = channel_def['service']
        service = session.query(Service).filter(Service.name == service_name).first()

        if not service:
            raise Exception('Service `{}` does not exist (channel `{}`)'.format(service_name, channel_def['name']))

        return service

# ################################################################################################################################

    def create_channel_definition(self, channel_def:'anydict', session:'SASession') -> 'any_':

        # The channel always invokes an existing service
        service = self._get_service(channel_def, session)

        channel = ChannelAMQP()
        channel.name = channel_def['name']
        channel.is_active = channel_def.get('is_active', True)
        channel.address = channel_def['address']
        channel.username = channel_def.get('username', '')
        channel.queue = channel_def['queue']
        channel.consumer_tag_prefix = channel_def.get('consumer_tag_prefix', '')
        channel.service = service
        channel.pool_size = channel_def.get('pool_size', AMQP.DEFAULT.POOL_SIZE)
        channel.ack_mode = channel_def.get('ack_mode', AMQP.ACK_MODE.ACK.id)
        channel.prefetch_count = channel_def.get('prefetch_count', AMQP.DEFAULT.PREFETCH_COUNT)
        channel.data_format = channel_def.get('data_format')
        channel.frame_max = _default_frame_max
        channel.heartbeat = _default_heartbeat

        # Set the password if provided, otherwise generate one
        if 'password' in channel_def:
            channel.password = channel_def['password']
        else:
            channel.password = CryptoManager.generate_password(to_str=True)

        # The subtype, e.g. Azure Service Bus, is kept in the opaque attributes
        channel.opaque1 = dumps({'subtype': self.subtype_key})

        # Add to session and flush to get the ID
        session.add(channel)
        session.flush()

        return channel

# ################################################################################################################################

    def update_channel_definition(self, channel_def:'anydict', session:'SASession') -> 'any_':

        channel_id = channel_def['id']
        channel = session.query(ChannelAMQP).filter_by(id=channel_id).one()

        # The channel always invokes an existing service
        if 'service' in channel_def:
            channel.service = self._get_service(channel_def, session)

        # Update all the attributes provided in YAML ..
        for key, value in channel_def.items():

            # .. skipping the fields that must not be set directly ..
            if key in ('id', 'type', 'service'):
                continue

            # .. the password is updated only if it was provided ..
            if key == 'password':
                if not value:
                    continue

            # .. and everything else is set as-is.
            setattr(channel, key, value)

        # The subtype, e.g. Azure Service Bus, is kept in the opaque attributes
        channel.opaque1 = dumps({'subtype': self.subtype_key})

        session.add(channel)
        return channel

# ################################################################################################################################

    def sync_channel_definitions(self, channel_list:'anylist', session:'SASession') -> 'listtuple':

        label = self.subtype['label']
        logger.info('Processing %d %s channel definitions from YAML', len(channel_list), label)

        db_defs = self.get_channels_from_db(session, self.importer.cluster_id)
        to_create, to_update = self.compare_channels(channel_list, db_defs)

        out_created = []
        out_updated = []

        try:
            for item in to_create:
                instance = self.create_channel_definition(item, session)
                logger.info('Created %s channel definition: name=%s id=%s', label, instance.name, instance.id)
                out_created.append(instance)

            for item in to_update:
                instance = self.update_channel_definition(item, session)
                logger.info('Updated %s channel definition: name=%s id=%s', label, instance.name, instance.id)
                out_updated.append(instance)

            session.commit()

        except Exception as e:
            logger.error('Error syncing %s channel definitions: %s', label, e)
            session.rollback()
            raise

        return out_created, out_updated

# ################################################################################################################################
# ################################################################################################################################

class OutgoingAMQPImporter:
    """ One importer serves every subtype of the AMQP implementation - the importer is registered
    once per subtype, e.g. under the outgoing_amqp key and under the outgoing_azure_service_bus key.
    """

    def __init__(self, importer:'EnmasseYAMLImporter', subtype:'str') -> 'None':
        self.importer = importer
        self.subtype_key = subtype
        self.subtype = AMQP_Subtype[subtype]

# ################################################################################################################################

    def get_connections_from_db(self, session:'SASession', cluster_id:'int') -> 'anydict':
        out = {}

        label = self.subtype['label']
        logger.info('Retrieving outgoing %s connection definitions from database for cluster_id=%s', label, cluster_id)

        # Only connections of this importer's subtype are taken into account
        query_result = out_amqp_list(session, cluster_id, self.subtype_key, False)
        definitions = to_json(query_result, return_as_dict=True)

        for item in definitions:
            name = item['name']
            logger.info('Processing outgoing %s connection definition: %s (id=%s)', label, name, item['id'])
            out[name] = item

        logger.info('Total outgoing %s connection definitions from DB: %d', label, len(out))

        return out

# ################################################################################################################################

    def compare_connections(self, yaml_defs:'anylist', db_defs:'anydict') -> 'tuple':

        # Find items to create and update
        to_create = []
        to_update = []

        for yaml_def in yaml_defs:
            yaml_def = preprocess_item(yaml_def)
            name = yaml_def['name']

            # Update an existing definition ..
            if name in db_defs:
                update_def = yaml_def.copy()
                update_def['id'] = db_defs[name]['id']
                to_update.append(update_def)

            # .. or create a new one.
            else:
                to_create.append(yaml_def)

        return to_create, to_update

# ################################################################################################################################

    def _resolve_delivery_mode(self, connection_def:'anydict') -> 'int':
        """ Turns the YAML delivery mode name into the integer that the ODB stores.
        """
        delivery_mode = connection_def.get('delivery_mode')

        if delivery_mode is None:
            out = _default_delivery_mode
        else:
            out = _delivery_mode_by_name[delivery_mode]

        return out

# ################################################################################################################################

    def create_connection_definition(self, connection_def:'anydict', session:'SASession') -> 'any_':

        connection = OutgoingAMQP()
        connection.name = connection_def['name']
        connection.is_active = connection_def.get('is_active', True)
        connection.address = connection_def['address']
        connection.username = connection_def.get('username', '')
        connection.delivery_mode = self._resolve_delivery_mode(connection_def)
        connection.priority = connection_def.get('priority', AMQP.DEFAULT.PRIORITY)
        connection.content_type = connection_def.get('content_type')
        connection.content_encoding = connection_def.get('content_encoding')
        connection.expiration = connection_def.get('expiration')
        connection.pool_size = connection_def.get('pool_size', AMQP.DEFAULT.POOL_SIZE)
        connection.user_id = connection_def.get('user_id')
        connection.app_id = connection_def.get('app_id')
        connection.frame_max = _default_frame_max
        connection.heartbeat = _default_heartbeat

        # Set the password if provided, otherwise generate one
        if 'password' in connection_def:
            connection.password = connection_def['password']
        else:
            connection.password = CryptoManager.generate_password(to_str=True)

        # The subtype, e.g. Azure Service Bus, is kept in the opaque attributes
        connection.opaque1 = dumps({'subtype': self.subtype_key})

        # Add to session and flush to get the ID
        session.add(connection)
        session.flush()

        return connection

# ################################################################################################################################

    def update_connection_definition(self, connection_def:'anydict', session:'SASession') -> 'any_':

        connection_id = connection_def['id']
        connection = session.query(OutgoingAMQP).filter_by(id=connection_id).one()

        # The delivery mode arrives as a string name and the ODB stores an integer
        if 'delivery_mode' in connection_def:
            connection.delivery_mode = self._resolve_delivery_mode(connection_def)

        # Update all the attributes provided in YAML ..
        for key, value in connection_def.items():

            # .. skipping the fields that must not be set directly ..
            if key in ('id', 'type', 'delivery_mode'):
                continue

            # .. the password is updated only if it was provided ..
            if key == 'password':
                if not value:
                    continue

            # .. and everything else is set as-is.
            setattr(connection, key, value)

        # The subtype, e.g. Azure Service Bus, is kept in the opaque attributes
        connection.opaque1 = dumps({'subtype': self.subtype_key})

        session.add(connection)
        return connection

# ################################################################################################################################

    def sync_connection_definitions(self, connection_list:'anylist', session:'SASession') -> 'listtuple':

        label = self.subtype['label']
        logger.info('Processing %d outgoing %s connection definitions from YAML', len(connection_list), label)

        db_defs = self.get_connections_from_db(session, self.importer.cluster_id)
        to_create, to_update = self.compare_connections(connection_list, db_defs)

        out_created = []
        out_updated = []

        try:
            for item in to_create:
                instance = self.create_connection_definition(item, session)
                logger.info('Created outgoing %s connection definition: name=%s id=%s', label, instance.name, instance.id)
                out_created.append(instance)

            for item in to_update:
                instance = self.update_connection_definition(item, session)
                logger.info('Updated outgoing %s connection definition: name=%s id=%s', label, instance.name, instance.id)
                out_updated.append(instance)

            session.commit()

        except Exception as e:
            logger.error('Error syncing outgoing %s connection definitions: %s', label, e)
            session.rollback()
            raise

        return out_created, out_updated

# ################################################################################################################################
# ################################################################################################################################
