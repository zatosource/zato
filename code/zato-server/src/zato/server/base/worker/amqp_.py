# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from traceback import format_exc

# Zato
from zato.common.util.api import spawn_greenlet
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
        msg:'Bunch',
    ) -> 'None':
        msg.is_active = True
        self.amqp_api.create(msg.name, msg, self.invoke, needs_start=True)

# ################################################################################################################################

    def on_broker_msg_OUTGOING_AMQP_CREATE(
        self:'WorkerStore', # type: ignore
        msg:'Bunch',
    ) -> 'None':
        with self.update_lock:
            self.amqp_out_name_to_def[msg.name] = msg.name
            self.amqp_api.create_outconn(msg.name, msg)

# ################################################################################################################################

    def on_broker_msg_OUTGOING_AMQP_EDIT(
        self:'WorkerStore', # type: ignore
        msg:'Bunch',
    ) -> 'None':
        with self.update_lock:
            del self.amqp_out_name_to_def[msg.old_name]
            self.amqp_out_name_to_def[msg.name] = msg.name
            self.amqp_api.edit_outconn(msg.name, msg)

# ################################################################################################################################

    def on_broker_msg_OUTGOING_AMQP_DELETE(
        self:'WorkerStore', # type: ignore
        msg:'Bunch',
    ) -> 'None':
        with self.update_lock:
            del self.amqp_out_name_to_def[msg.name]
            self.amqp_api.delete_outconn(msg.name, msg)

# ################################################################################################################################

    def on_broker_msg_CHANNEL_AMQP_CREATE(
        self:'WorkerStore', # type: ignore
        msg:'Bunch',
    ) -> 'None':
        with self.update_lock:
            self.amqp_connection_create(msg)
            # self.amqp_api.create_channel(msg.name, msg)

# ################################################################################################################################

    def on_broker_msg_CHANNEL_AMQP_EDIT(
        self:'WorkerStore', # type: ignore
        msg:'Bunch',
    ) -> 'None':
        with self.update_lock:
            self.amqp_api.edit_channel(msg.name, msg)

# ################################################################################################################################

    def on_broker_msg_CHANNEL_AMQP_DELETE(
        self:'WorkerStore', # type: ignore
        msg:'Bunch',
    ) -> 'None':
        with self.update_lock:
            self.amqp_api.delete_channel(msg.name, msg)

# ################################################################################################################################

    def amqp_invoke(
        self:'WorkerStore', # type: ignore
        msg:'Bunch',
        out_name:'str',
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
        with self.update_lock:
            def_name = self.amqp_out_name_to_def[out_name]

        return self.amqp_api.invoke(def_name, out_name, msg, exchange, routing_key, properties, headers, **kwargs)

    def _amqp_invoke_async(
        self:'WorkerStore', # type: ignore
        *args:'any_',
        **kwargs:'any_',
    ) -> 'None':
        try:
            self.amqp_invoke(*args, **kwargs)
        except Exception:
            logger.warning(format_exc())

    def amqp_invoke_async(
        self:'WorkerStore', # type: ignore
        *args:'any_',
        **kwargs:'any_',
    ) -> 'None':
        spawn_greenlet(self._amqp_invoke_async, *args, **kwargs)

# ################################################################################################################################
# ################################################################################################################################
