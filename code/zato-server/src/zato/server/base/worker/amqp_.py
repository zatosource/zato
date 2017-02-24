# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from logging import getLogger
from traceback import format_exc

# Bunch
from bunch import bunchify

# gevent
from gevent import spawn

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

    def amqp_connection_create_edit(self, name, msg, action, lock_timeout, start):
        '''
        with self.server.zato_lock_manager(msg.config_cid, ttl=10, block=lock_timeout):
            func = getattr(self.amqp_api, action)
            func(name, msg, self.on_message_invoke_service, self.request_dispatcher.url_data.authenticate_web_socket)
            '''

# ################################################################################################################################

    def amqp_connection_create(self, msg):
        logger.warn('111 %s', msg)
        '''
        self.amqp_connection_create_edit(msg.name, msg, 'create', 0, True)
        self.amqp_api.start(msg.name)
        '''

# ################################################################################################################################

    def on_broker_msg_DEFINITION_AMQP_CREATE(self, msg):
        if self.server.zato_lock_manager.acquire(msg.config_cid, ttl=10, block=False):
            msg.pool_size = self.amqp_pool_size
            start_connectors(self, 'zato.connector.amqp_.start', msg)

# ################################################################################################################################

    def on_broker_msg_DEFINITION_AMQP_EDIT(self, msg):
        logger.warn('222 %s', msg)
        '''
        # Each worker uses a unique bind port
        msg = bunchify(msg)
        update_bind_port(msg, self.worker_idx)

        self.amqp_connection_create_edit(msg.old_name, msg, 'edit', 5, False)
        '''

# ################################################################################################################################

    def on_broker_msg_DEFINITION_AMQP_DELETE(self, msg):
        logger.warn('333 %s', msg)
        '''
        with self.server.zato_lock_manager(msg.config_cid, ttl=10, block=5):
            self.amqp_api.delete(msg.name)
            '''

# ################################################################################################################################

    def on_broker_msg_DEFINITION_AMQP_CHANGE_PASSWORD(self, msg):
        logger.warn('444 %s', msg)
        '''
        with self.server.zato_lock_manager(msg.config_cid, ttl=10, block=5):
            self.amqp_api.delete(msg.name)
            '''

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

    def amqp_invoke(self, msg, out_name, exchange='/', routing_key=None, properties=None, headers=None):
        """ Invokes a remote AMQP broker sending it a message with the specified routing key to an exchange through
        a named outgoing connection. Optionally, lower-level details can be provided in properties and they will be
        provided directly to the underlying AMQP library (kombu). Headers are AMQP headers attached to each message.
        """
        with self.update_lock:
            def_name = self.amqp_out_name_to_def[out_name]

        return self.amqp_api.invoke(def_name, out_name, msg, exchange, routing_key, properties, headers)

    def _amqp_invoke_async(self, *args, **kwargs):
        try:
            self.amqp_invoke(*args, **kwargs)
        except Exception, e:
            logger.warn(format_exc(e))

    def amqp_invoke_async(self, *args, **kwargs):
        spawn_greenlet(self._amqp_invoke_async, *args, **kwargs)

# ################################################################################################################################
