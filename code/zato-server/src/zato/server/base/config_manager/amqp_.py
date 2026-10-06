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
from zato.server.base.config_manager.common import ConfigManagerImpl

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

        self.amqp_api.create(msg.name, connector_config, self.invoke, needs_start=True)

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
