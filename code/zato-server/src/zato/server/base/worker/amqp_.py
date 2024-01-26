# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from traceback import format_exc

# Zato
from zato.common.model.amqp_ import AMQPConnectorConfig
from zato.common.util.api import spawn_greenlet, start_connectors
from zato.server.base.worker.common import WorkerImpl

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from bunch import Bunch
    from zato.common.typing_ import any_, dictnone, strnone
    from zato.server.base.worker import WorkerStore

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class AMQP(WorkerImpl):
    """ AMQP-related functionality for worker objects.
    """
    def amqp_connection_create(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        msg.is_active = True
        with self.update_lock:
            self.amqp_api.create(msg.name, msg, self.invoke, needs_start=True)

# ################################################################################################################################

    def on_broker_msg_DEFINITION_AMQP_CREATE(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        start_connectors(self, 'zato.connector.amqp_.start', msg)

# ################################################################################################################################

    def on_broker_msg_DEFINITION_AMQP_EDIT(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':

        # Convert to a dataclass first
        msg = AMQPConnectorConfig.from_dict(msg) # type: ignore

        # Definitions are always active
        msg.is_active = True

        # Make sure connection passwords are always in clear text
        msg.password = self.server.decrypt(msg.password)

        with self.update_lock:

            # Update outconn -> definition mappings
            for out_name, def_name in self.amqp_out_name_to_def.items():
                if def_name == msg.old_name:
                    self.amqp_out_name_to_def[out_name] = msg.name

            # Update definition itself
            self.amqp_api.edit(msg.old_name, msg)

# ################################################################################################################################

    def on_broker_msg_DEFINITION_AMQP_DELETE(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        with self.update_lock:
            to_del = []
            for out_name, def_name in self.amqp_out_name_to_def.items():
                if def_name == msg.name:
                    to_del.append(out_name)

            for out_name in to_del:
                del self.amqp_out_name_to_def[out_name]

            self.amqp_api.delete(msg.name)

# ################################################################################################################################

    def on_broker_msg_DEFINITION_AMQP_CHANGE_PASSWORD(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        with self.update_lock:
            self.amqp_api.change_password(msg.name, msg)

# ################################################################################################################################

    def on_broker_msg_OUTGOING_AMQP_CREATE(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        with self.update_lock:
            self.amqp_out_name_to_def[msg.name] = msg.def_name
            self.amqp_api.create_outconn(msg.def_name, msg)

# ################################################################################################################################

    def on_broker_msg_OUTGOING_AMQP_EDIT(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        with self.update_lock:
            del self.amqp_out_name_to_def[msg.old_name]
            self.amqp_out_name_to_def[msg.name] = msg.def_name
            self.amqp_api.edit_outconn(msg.def_name, msg)

# ################################################################################################################################

    def on_broker_msg_OUTGOING_AMQP_DELETE(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        with self.update_lock:
            del self.amqp_out_name_to_def[msg.name]
            self.amqp_api.delete_outconn(msg.def_name, msg)

# ################################################################################################################################

    def on_broker_msg_CHANNEL_AMQP_CREATE(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        with self.update_lock:
            self.amqp_api.create_channel(msg.def_name, msg)

# ################################################################################################################################

    def on_broker_msg_CHANNEL_AMQP_EDIT(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        with self.update_lock:
            self.amqp_api.edit_channel(msg.def_name, msg)

# ################################################################################################################################

    def on_broker_msg_CHANNEL_AMQP_DELETE(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        with self.update_lock:
            self.amqp_api.delete_channel(msg.def_name, msg)

# ################################################################################################################################

    def amqp_invoke(
        self:'WorkerStore', # type: ignore
        msg,          # type: Bunch
        out_name,     # type: str
        exchange='/', # type: str
        routing_key=None, # type: strnone
        properties=None,  # type: dictnone
        headers=None,     # type: dictnone
        **kwargs          # type: any_
    ) -> 'any_':
        """ Invokes a remote AMQP broker sending it a message with the specified routing key to an exchange through
        a named outgoing connection. Optionally, lower-level details can be provided in properties and they will be
        provided directly to the underlying AMQP library (kombu). Headers are AMQP headers attached to each message.
        """
        with self.update_lock:
            def_name = self.amqp_out_name_to_def[out_name]

        return self.amqp_api.invoke(def_name, out_name, msg, exchange, routing_key, properties, headers, **kwargs)

    def _amqp_invoke_async(
        self:'WorkerStore', # type: ignore
        *args,   # type: any_
        **kwargs # type: any_
    ) -> 'None':
        try:
            self.amqp_invoke(*args, **kwargs)
        except Exception:
            logger.warning(format_exc())

    def amqp_invoke_async(
        self:'WorkerStore', # type: ignore
        *args,   # type: any_
        **kwargs # type: any_
    ) -> 'None':
        spawn_greenlet(self._amqp_invoke_async, *args, **kwargs)

# ################################################################################################################################
# ################################################################################################################################
