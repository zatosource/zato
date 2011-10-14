# -*- coding: utf-8 -*-

"""
Copyright (C) 2011 Dariusz Suchojad <dsuch at gefira.pl>

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

""" 
Objects useful when implementing ZeroMQ clients. Written without any dependecies
on Zato code base so they can be re-used outside of the Zato project.
"""

# stdlib
import logging
from threading import Thread
from traceback import format_exc

# ZeroMQ
import zmq

# Zato
from zato.common.broker_message import MESSAGE_TYPE

logger = logging.getLogger(__name__)

class ZMQPull(object):
    """ A ZeroMQ subscriber. Runs in a background thread and invokes the handler
    on each incoming message.
    """
    
    def __init__(self, name, zmq_context, address, on_message_handler, 
                 keep_running=True, message_handler_args=None):
        self.name = name
        self.zmq_context = zmq_context
        self.address = address
        self.on_message_handler = on_message_handler
        self.message_handler_args = message_handler_args
        self.keep_running = keep_running

    # Custom subclasses may wish to override the two hooks below.
    def on_before_msg_handler(self, msg, args):
        pass

    def on_after_msg_handler(self, msg, e=None, args=None):
        pass
    
    def start(self):
        Thread(target=self.listen).start()
        
    def close(self, socket=None):
        self.keep_running = False
        self.socket.close()
    
    def listen(self):
        logger.info('Starting [{0}]/[{1}]/[{2}]'.format(
            self.name, self.__class__.__name__, self.address))
        
        self.socket = self.zmq_context.socket(zmq.PULL)
        self.socket.setsockopt(zmq.LINGER, 0)
        self.socket.connect(self.address)
        
        poller = zmq.Poller()
        poller.register(self.socket, zmq.POLLIN)
        
        while self.keep_running:
            try:
                socks = dict(poller.poll())
                if socks.get(self.socket) == zmq.POLLIN:
                    msg = self.socket.recv()
            except Exception, e:
                
                # It's OK and needs not to disturb the user so log it only
                # in the DEBUG level.
                if isinstance(e, zmq.ZMQError) and e.errno == zmq.ETERM:
                    msg = '[{0}] Caught a zmq.ETERM {1}, quitting'.format(
                        self.name, format_exc(e))
                    meth = logger.debug
                else:
                    msg = '[{0}] Caught an exception [{1}], quitting.'.format(
                        self.name, format_exc(e))
                    meth = logger.error
                    
                meth(msg)
                self.close()
            else:
                self.on_before_msg_handler(msg, self.message_handler_args)
                try:
                    e = None
                    self.on_message_handler(msg, self.message_handler_args)
                except Exception, e:
                    msg = '[{0}] Could not invoke the message handler, msg [{1}] e [{2}]'
                    logger.error(msg.format(self.name, msg, format_exc(e)))
                    
                self.on_after_msg_handler(msg, e, self.message_handler_args)
                
class ZMQPush(object):
    """ Sends messages to ZeroMQ using a PUSH socket.
    """
    def __init__(self, name, zmq_context, address):
        self.name = name
        self.zmq_context = zmq_context
        self.address = address
        self.socket_type = zmq.PUSH 
        
        self.socket = self.zmq_context.socket(self.socket_type)
        self.socket.setsockopt(zmq.LINGER, 0)
        self.socket.connect(self.address)
        
    def send(self, msg):
        try:
            self.socket.send_unicode(msg)
        except zmq.ZMQError, e:
            msg = '[{0}] Caught ZMQError [{1}], continuing anyway.'.format(
                self.name, e.strerror)
            logger.warn(msg)
        
    def close(self):
        msg = 'Stopping [[{0}/{1}/{2}]'.format(self.name, self.address, self.socket_type)
        logger.info(msg)
        self.socket.close()
        
class BrokerClient(object):
    """ A ZeroMQ broker client which knows how to subscribe to messages and push
    the messages onto the broker.
    """
    def __init__(self, name, zmq_context, push_address, pull_address, 
                 on_message_handler=None, message_handler_args=None):
        self._push = ZMQPush(name, zmq_context, push_address)
        self._pull = ZMQPull(name, zmq_context, pull_address, on_message_handler,
                             True,  message_handler_args)
        
    def set_message_handler(self, handler):
        self._pull.on_message_handler = handler
        
    def set_message_handler_args(self, args):
        self._pull.message_handler_args = args
    
    def start_subscriber(self):
        self._pull.start()
    
    def send(self, msg):
        return self._push.send(msg)
    
    def close(self):
        self._push.close()
        self._pull.close()