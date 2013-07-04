# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at zato.io>

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

logger = logging.getLogger(__name__)

class BrokerMessageReceiver(object):
    """ A class that knows how to handle messages received from the broker.
    It doesn't really belong to the zato-broker's namespace because it is free
    to handle the messages in a Zato-specific way.
    """
    def __init__(self):
        self.broker_client_id = '{}-{}'.format(ZATO_NONE, new_cid())
        self.broker_callbacks = {}
        self.broker_messages = []
    
    def on_broker_msg(self, msg):
        """ Receives a configuration message, parses its JSON contents and invokes
        an appropriate handler, the one indicated by the msg's 'action' key so
        if the action is '1000' then self.on_config_SCHEDULER_CREATE
        will be invoked (because '1000' happens to be the code for creating
        a new scheduler's job, see zato.common.broker_message for the list
        of all actions).
        """
        try:
            if self.logger.isEnabledFor(logging.DEBUG):
                self.logger.debug('Got message [{!r}]'.format(msg))
    
            if self.filter(msg):
                action = code_to_name[msg['action']]
                handler = 'on_broker_msg_{0}'.format(action)
                getattr(self, handler)(msg)
            else:
                if self.logger.isEnabledFor(logging.DEBUG):
                    self.logger.debug('Rejecting broker message [{!r}]'.format(msg))
        except Exception, e:
            msg = 'Could not handle broker msg:[{!r}], e:[{}]'.format(msg, format_exc(e))
            logger.error(msg)
            
    def filter(self, msg):
        """ Subclasses may override the method in order to filter the messages
        prior to invoking the actual message handler. Default implementation 
        always returns False which rejects all the incoming messages.
        """
        return False
