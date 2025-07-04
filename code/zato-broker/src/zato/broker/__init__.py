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
from zato.common.util.api import new_cid
from zato.common.util.config import resolve_env_variables
from zato.broker.message_handler import BrokerMessageHandler

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
    def __init__(self):
        self.broker_client_id = '{}-{}'.format(ZATO_NONE, new_cid())
        self.broker_callbacks = {}
        self.broker_messages = []

# ################################################################################################################################

    def on_broker_msg(self, msg):
        """ Receives a configuration message, parses its JSON contents and invokes an appropriate handler, the one indicated
        by the msg's 'action' key so if the action is '1000' then self.on_config_SCHEDULER_CREATE will be invoked
        (because in this case '1000' is the code for creating a new scheduler's job, see zato.common.broker_message for the list
        of all actions).
        """
        # Use the shared BrokerMessageHandler with our own context and functions
        result = BrokerMessageHandler.handle_message(
            msg=msg,
            context=self.worker_store,
            preprocess_func=self.preprocess_msg,
            filter_func=self.filter
        )

        # If message was handled and it's a service invocation that needs a reply
        if result.was_handled and result.action_code == service_invoke:
            if reply_to := msg.get('reply_to'):
                correlation_id = msg.get('cid', '')
                self.broker_client.publish_to_queue(reply_to, result.response, correlation_id=correlation_id)

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
