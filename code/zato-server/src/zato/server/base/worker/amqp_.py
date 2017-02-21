# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from logging import getLogger

# Bunch
from bunch import bunchify

# Zato
from zato.common.util import start_connectors
from zato.server.base.worker.common import WorkerImpl

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################

class AMQP(WorkerImpl):
    """ AMQP-related functionality for worker objects.
    """
    def __init__(self):
        super(AMQP, self).__init__()
        self.amqp_api = None
        self.amqp_pool_size = -1 # Will be set in WorkerStore

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
