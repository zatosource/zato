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
from zato.broker.zato_client import BrokerClient
from zato.common.broker_message import code_to_name, MESSAGE

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
        
        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug('Got message [{0}]'.format(msg))
            
        msg_type = msg[:MESSAGE.MESSAGE_TYPE_LENGTH]
        msg = loads(msg[MESSAGE.PAYLOAD_START:])
        msg = Bunch(msg)
        
        if self.filter(msg):
            action = code_to_name[msg['action']]
            handler = 'on_broker_pull_msg_{0}'.format(action)
            handler = getattr(self, handler)
            if args:
                handler(msg, args)
            else:
                handler(msg)
        else:
            if self.logger.isEnabledFor(logging.DEBUG):
                self.logger.debug('Filtered out message [{0}]'.format(msg))
            
    def filter(self, msg):
        """ Subclasses may override the method in order to filter the messages
        prior to invoking the actual message handler. Default implementation 
        always returns False.
        """
        return False
            
class BaseWorker(BrokerMessageReceiver):
        
    def _init(self):
        """ Initializes the instance, sets up the broker client.
        """
        self._setup_broker_client()

    def _setup_broker_client(self):
        """ Connects to the broker and sets up all the sockets.
        """
        self.broker_client = BrokerClient()
        self.broker_client.name = self.worker_config.broker_config.name
        self.broker_client.token = self.worker_config.broker_config.broker_token
        self.broker_client.zmq_context = self.worker_config.broker_config.zmq_context
        self.broker_client.broker_push_client_pull = self.worker_config.broker_config.broker_push_client_pull
        self.broker_client.client_push_broker_pull = self.worker_config.broker_config.client_push_broker_pull
        self.broker_client.broker_pub_client_sub = self.worker_config.broker_config.broker_pub_client_sub
        self.broker_client.on_pull_handler = self.on_broker_msg
        self.broker_client.on_sub_handler = self.on_broker_msg
        self.broker_client.init()
        self.broker_client.start()
