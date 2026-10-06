# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from copy import deepcopy
from logging import getLogger
from traceback import format_exc

# Zato
from zato.common.util.api import spawn_greenlet
from zato.server.base.config_manager.common import _pubsub_amqp_bridge_service, ConfigManagerImpl
from zato.server.connection.amqp_queue import get_queue_depth

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.ext.bunch import Bunch
    from zato.common.typing_ import any_, dictnone, strnone
    from zato.server.base.config_manager import ConfigManager

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class AMQP(ConfigManagerImpl):
    """ AMQP-related functionality for config manager objects.
    """
    def amqp_connection_create(
        self:'ConfigManager', # type: ignore
        msg:'Bunch',
    ) -> 'None':
        msg.password = self.server.decrypt(msg.password)

        # The connector is always active, only the channel or outconn under it can be inactive,
        # so the connector gets its own copy of the config and the object's flag stays untouched.
        connector_config = deepcopy(msg)
        connector_config.is_active = True

        self.amqp_api.create(msg.name, connector_config, self.on_amqp_channel_message, needs_start=True)

# ################################################################################################################################

    def on_amqp_channel_message(
        self:'ConfigManager', # type: ignore
        service_name:'str',
        body:'any_',
        **kwargs:'any_',
    ) -> 'any_':
        """ What an AMQP channel's consumer invokes for each message it receives. A channel that a broker-backed topic
        reads its messages back through hands the message over to pub/sub, every other channel invokes its own service.
        The decision is made here, per message, so it is never stale - the channel's own configuration is not touched.
        """
        channel_name = kwargs['zato_ctx']['zato.channel_item']['name']

        if self.is_pubsub_amqp_channel(channel_name):
            service_name = _pubsub_amqp_bridge_service

        return self.invoke(service_name, body, **kwargs)

# ################################################################################################################################

    def amqp_stop_all(
        self:'ConfigManager', # type: ignore
    ) -> 'None':
        """ Stops every AMQP connector along with its consumers and producers, which is what has to happen before
        the connectors are built anew from the configuration, or the consumers that exist now would keep reading
        from their queues alongside the new ones.
        """
        connectors = list(self.amqp_api.connectors.values())

        # Every consumer is told to stop first, so they all wind down within one drain timeout ..
        for connector in connectors:
            connector.request_stop()

        # .. and only then is each connector stopped and removed, which is where the waiting happens.
        for connector in connectors:
            _ = self.amqp_api.delete(connector.name)

# ################################################################################################################################

    def amqp_get_channel_queue_depth(
        self:'ConfigManager', # type: ignore
        channel_name:'str',
    ) -> 'int':
        """ How many messages wait in the queue an AMQP channel reads from, asked of the broker itself, which is how
        the depth of a queue that lives in a broker is known before the channel's consumers start taking from it.
        """
        channels = self.config_store.channel_amqp.get_config_list()

        for item in channels:
            if item['name'] == channel_name:
                channel = item
                break
        else:
            raise ValueError(f'No such AMQP channel `{channel_name}`')

        # The connector decrypts the password in place when it is created, which has not happened yet for this channel
        password = self.server.decrypt(channel['password'])

        out = get_queue_depth(channel_name, channel['address'], channel['username'], password, channel['queue'])
        return out

# ################################################################################################################################

    def on_config_event_OUTGOING_AMQP_CREATE(
        self:'ConfigManager', # type: ignore
        msg:'Bunch',
    ) -> 'None':
        with self.update_lock:
            self.amqp_out_name_to_def[msg.name] = msg.name
            self.amqp_connection_create(msg)
            self.amqp_api.create_outconn(msg.name, msg)

# ################################################################################################################################

    def on_config_event_OUTGOING_AMQP_EDIT(
        self:'ConfigManager', # type: ignore
        msg:'Bunch',
    ) -> 'None':
        """ Replaces the connector of an outgoing connection with one built from the new configuration,
        which is what makes a new name, address or credentials take effect at runtime.
        """
        msg.password = self.server.decrypt(msg.password)
        with self.update_lock:
            del self.amqp_out_name_to_def[msg.old_name]
            self.amqp_out_name_to_def[msg.name] = msg.name

            # The connector may be absent if it could not be created at startup ..
            if msg.old_name in self.amqp_api.connectors:
                _ = self.amqp_api.delete(msg.old_name)

            # .. and the new one is built exactly the way a freshly created connection is.
            self.amqp_connection_create(msg)
            self.amqp_api.create_outconn(msg.name, msg)

# ################################################################################################################################

    def on_config_event_OUTGOING_AMQP_DELETE(
        self:'ConfigManager', # type: ignore
        msg:'Bunch',
    ) -> 'None':
        """ Removes an outgoing connection along with its connector.
        """
        with self.update_lock:
            del self.amqp_out_name_to_def[msg.name]

            # The connector may be absent if it could not be created at startup.
            if msg.name in self.amqp_api.connectors:
                self.amqp_api.delete_outconn(msg.name, msg)
                _ = self.amqp_api.delete(msg.name)

# ################################################################################################################################

    def on_config_event_CHANNEL_AMQP_CREATE(
        self:'ConfigManager', # type: ignore
        msg:'Bunch',
    ) -> 'None':
        with self.update_lock:
            self.amqp_connection_create(msg)
            self.amqp_api.create_channel(msg.name, msg)

# ################################################################################################################################

    def on_config_event_CHANNEL_AMQP_EDIT(
        self:'ConfigManager', # type: ignore
        msg:'Bunch',
    ) -> 'None':
        """ Replaces the connector of a channel with one built from the new configuration,
        which is what makes a new name, address or credentials take effect at runtime.
        """
        msg.password = self.server.decrypt(msg.password)
        with self.update_lock:

            # The connector may be absent if it could not be created at startup ..
            if msg.old_name in self.amqp_api.connectors:
                _ = self.amqp_api.delete(msg.old_name)

            # .. and the new one is built exactly the way a freshly created channel is.
            self.amqp_connection_create(msg)
            self.amqp_api.create_channel(msg.name, msg)

# ################################################################################################################################

    def on_config_event_CHANNEL_AMQP_DELETE(
        self:'ConfigManager', # type: ignore
        msg:'Bunch',
    ) -> 'None':
        """ Removes a channel along with its connector.
        """
        with self.update_lock:

            # The connector may be absent if it could not be created at startup.
            if msg.name in self.amqp_api.connectors:
                self.amqp_api.delete_channel(msg.name, msg)
                _ = self.amqp_api.delete(msg.name)

# ################################################################################################################################

    def amqp_invoke(
        self:'ConfigManager', # type: ignore
        out_name:'str',
        msg:'Bunch',
        exchange:'str'='/',
        routing_key:'strnone'=None,
        properties:'dictnone'=None,
        headers:'dictnone'=None,
        **kwargs:'any_',
    ) -> 'any_':
        """ Invokes a remote AMQP broker sending it a message with the specified routing key to an exchange through
        a named outgoing connection. Optionally, lower-level details can be provided in properties and they will be
        provided directly to the underlying AMQP library (kombu). Headers are AMQP headers attached to each message.
        """
        return self.amqp_api.invoke(out_name, msg, exchange, routing_key, properties, headers, **kwargs)

    def _amqp_invoke_async(
        self:'ConfigManager', # type: ignore
        *args:'any_',
        **kwargs:'any_',
    ) -> 'None':
        try:
            self.amqp_invoke(*args, **kwargs)
        except Exception:
            logger.warning(format_exc())

    def amqp_invoke_async(
        self:'ConfigManager', # type: ignore
        *args:'any_',
        **kwargs:'any_',
    ) -> 'None':
        _ = spawn_greenlet(self._amqp_invoke_async, *args, **kwargs)

# ################################################################################################################################
# ################################################################################################################################
