# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.api import ZATO_NONE
from zato.common.broker_message import SERVICE
from zato.common.util.api import new_cid_broker_client
from zato.common.util.config import resolve_env_variables
from zato.broker.message_handler import handle_broker_msg

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from kombu.transport.pyamqp import Message as KombuMessage
    from zato.broker.client import BrokerClient
    from zato.server.base.worker import WorkerStore
    BrokerClient = BrokerClient
    KombuMessage = KombuMessage
    WorkerStore = WorkerStore

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato')
has_debug = logger.isEnabledFor(logging.DEBUG)

# ################################################################################################################################
# ################################################################################################################################

service_invoke = SERVICE.INVOKE.value

# ################################################################################################################################
# ################################################################################################################################

class BrokerMessageReceiver:
    """ A class that knows how to handle messages received from other worker processes.
    """
    broker_client: 'BrokerClient'
    worker_store: 'WorkerStore'

    def __init__(self):
        self.broker_client_id = '{}-{}'.format(ZATO_NONE, new_cid_broker_client())
        self.broker_callbacks = {}
        self.broker_messages = []

# ################################################################################################################################

    def on_broker_msg(self, msg:'strdict') -> 'None':
        """ Receives a configuration message, parses its JSON contents and invokes an appropriate handler, the one indicated
        by the msg's 'action' key so if the action is '1000' then self.on_config_SCHEDULER_CREATE will be invoked
        (because in this case '1000' is the code for creating a new scheduler's job, see zato.common.broker_message for the list
        of all actions).
        """
        # Apply preprocessing first
        msg = self.preprocess_msg(msg)

        # Apply filtering
        if not self.filter(msg):
            return

        # Use the shared handler
        result = handle_broker_msg(msg, self.worker_store)

        # If message was handled and it's a service invocation that needs a reply
        if result.was_handled and result.action_code == service_invoke:
            if reply_to := msg.get('reply_to'):
                correlation_id = msg.get('cid', '')
                self.broker_client.publish_to_queue(reply_to, result.response, correlation_id=correlation_id)
            else:
                # Left empty for logging
                pass
        else:
            # Left empty for logging
            pass

# ################################################################################################################################

    def preprocess_msg(self, msg):
        """ Pre-processes a given message before it is handed over to its recipient by resolving all environment variables.
        """
        return resolve_env_variables(msg)

# ################################################################################################################################

    def filter(self, msg):
        """ Subclasses may override the method in order to filter the messages prior to invoking the actual message handler.
        """
        return True

# ################################################################################################################################
# ################################################################################################################################
