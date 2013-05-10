# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at gefira.pl>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
from traceback import format_exc

# Zato
from zato.broker.client import BrokerClient
from zato.common import ZATO_NONE
from zato.common.broker_message import code_to_name, TOPICS
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
