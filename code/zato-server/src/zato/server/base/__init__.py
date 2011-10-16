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

# anyjson
from anyjson import loads

# Bunch
from bunch import Bunch

# Zato
from zato.common.broker_message import code_to_name, MESSAGE

logger = logging.getLogger(__name__)

class BrokerMessageReceiver(object):
    """ A class that knows how to handle messages received from the broker.
    It doesn't really belong to the zato-broker's namespace because it is free
    to handle the messages in a Zato-specific way.
    """
    
    def on_broker_msg(self, msg, *args):
        """ Receives a configuration message, parses its JSON contents and invokes
        an appropriate handler, the one indicated by the msg's 'action' key so
        if the action is '1000' then self.on_config_SCHEDULER_CREATE
        will be invoked (because '1000' happens to be the code for creating
        a new scheduler's job, see zato.common.broker_message for the list
        of all actions).
        """
        
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug('Got message [{0}]'.format(msg))
            
        msg_type = msg[:MESSAGE.MESSAGE_TYPE_LENGTH]
        msg = loads(msg[MESSAGE.PAYLOAD_START:])
        msg = Bunch(msg)
        
        action = code_to_name[msg['action']]
        handler = 'on_broker_pull_msg_{0}'.format(action)
        handler = getattr(self, handler)
        if args:
            handler(msg, args)
        else:
            handler(msg)