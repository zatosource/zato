# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from logging import getLogger
from traceback import format_exc

# Zato
from zato.common.util import spawn_greenlet, start_connectors
from zato.server.base.worker.common import WorkerImpl

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################

class AMQP(WorkerImpl):
    """ AMQP-related functionality for worker objects.
    """

# ################################################################################################################################

    def amqp_connection_create(self, msg):
        msg.is_active = True
        with self.update_lock:
            self.amqp_api.create(msg.name, msg, self.invoke, needs_start=True)

    def on_broker_msg_DEFINITION_AMQP_CREATE(self, msg):
        start_connectors(self, 'zato.connector.amqp_.start', msg)

# ################################################################################################################################

    def on_broker_msg_DEFINITION_AMQP_EDIT(self, msg):
        msg.is_active = True

        with self.update_lock:

            # Update outconn -> definition mappings
            for out_name, def_name in self.amqp_out_name_to_def.items():
                if def_name == msg.old_name:
                    self.amqp_out_name_to_def[out_name] = msg.name

            # Update definition itself
            self.amqp_api.edit(msg.old_name, msg)

# ################################################################################################################################

    def on_broker_msg_DEFINITION_AMQP_DELETE(self, msg):
        with self.update_lock:
            for out_name, def_name in self.amqp_out_name_to_def.items():
                if def_name == msg.name:
                    del self.amqp_out_name_to_def[out_name]

            self.amqp_api.delete(msg.name)

# ################################################################################################################################

    def on_broker_msg_DEFINITION_AMQP_CHANGE_PASSWORD(self, msg):
        with self.update_lock:
            self.amqp_api.change_password(msg.name, msg)

# ################################################################################################################################

    def on_broker_msg_OUTGOING_AMQP_CREATE(self, msg):
        with self.update_lock:
            self.amqp_out_name_to_def[msg.name] = msg.def_name
            self.amqp_api.create_outconn(msg.def_name, msg)

# ################################################################################################################################

    def on_broker_msg_OUTGOING_AMQP_EDIT(self, msg):
        with self.update_lock:
            del self.amqp_out_name_to_def[msg.old_name]
            self.amqp_out_name_to_def[msg.name] = msg.def_name
            self.amqp_api.edit_outconn(msg.def_name, msg)

# ################################################################################################################################

    def on_broker_msg_OUTGOING_AMQP_DELETE(self, msg):
        with self.update_lock:
            del self.amqp_out_name_to_def[msg.name]
            self.amqp_api.delete_outconn(msg.def_name, msg)

# ################################################################################################################################

    def on_broker_msg_CHANNEL_AMQP_CREATE(self, msg):
        with self.update_lock:
            self.amqp_api.create_channel(msg.def_name, msg)

# ################################################################################################################################

    def on_broker_msg_CHANNEL_AMQP_EDIT(self, msg):
        with self.update_lock:
            self.amqp_api.edit_channel(msg.def_name, msg)

# ################################################################################################################################

    def on_broker_msg_CHANNEL_AMQP_DELETE(self, msg):
        with self.update_lock:
            self.amqp_api.delete_channel(msg.def_name, msg)

# ################################################################################################################################

    def amqp_invoke(self, msg, out_name, exchange='/', routing_key=None, properties=None, headers=None, **kwargs):
        """ Invokes a remote AMQP broker sending it a message with the specified routing key to an exchange through
        a named outgoing connection. Optionally, lower-level details can be provided in properties and they will be
        provided directly to the underlying AMQP library (kombu). Headers are AMQP headers attached to each message.
        """
        with self.update_lock:
            def_name = self.amqp_out_name_to_def[out_name]

        return self.amqp_api.invoke(def_name, out_name, msg, exchange, routing_key, properties, headers, **kwargs)

    def _amqp_invoke_async(self, *args, **kwargs):
        try:
            self.amqp_invoke(*args, **kwargs)
        except Exception:
            logger.warn(format_exc())

    def amqp_invoke_async(self, *args, **kwargs):
        spawn_greenlet(self._amqp_invoke_async, *args, **kwargs)

# ################################################################################################################################
