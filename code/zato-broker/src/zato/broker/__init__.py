# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
from traceback import format_exc

# Zato
from zato.common import ZATO_NONE
from zato.common.broker_message import code_to_name
from zato.common.util import new_cid
from zato.common.util.config import resolve_env_variables

logger = logging.getLogger('zato')
has_debug = logger.isEnabledFor(logging.DEBUG)

# ################################################################################################################################

class BrokerMessageReceiver(object):
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
        try:
            if has_debug:
                logger.debug('Got message `%r`', msg)

            # Apply pre-processing
            msg = self.preprocess_msg(msg)

            if self.filter(msg):
                action = code_to_name[msg['action']]
                handler = 'on_broker_msg_{0}'.format(action)
                getattr(self, handler)(msg)
            else:
                if has_debug:
                    logger.debug('Rejecting broker message `%r`', msg)
        except Exception:
            logger.error('Could not handle broker msg:`%r`, e:`%s`', msg, format_exc())

# ################################################################################################################################

    def preprocess_msg(self, msg):
        """ Pre-processes a given message before it is handed over to its recipient by resolving all environment variables.
        """
        return resolve_env_variables(msg)

# ################################################################################################################################

    def filter(self, msg):
        """ Subclasses may override the method in order to filter the messages prior to invoking the actual message handler.
        Default implementation always returns False which rejects all the incoming messages.
        """
        return False

# ################################################################################################################################
