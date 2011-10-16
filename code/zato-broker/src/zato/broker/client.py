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

logger = logging.getLogger(__name__)

class ZMQPullSub(object):
    """ A ZeroMQ client which pulls and subscribe to messages. Runs in a background 
    thread and invokes the handler on each incoming message.
    """
    
    def __init__(self, name, zmq_context, pull_addr, sub_addr, 
                 on_pull_sub_handler=None,  pull_handler_args=None,
                 on_sub_handler=None,  sub_handler_args=None, keep_running=True):
        self.name = name
        self.zmq_context = zmq_context
        self.pull_addr = pull_addr
        self.sub_addr = sub_addr
        self.keep_running = keep_running
        self.on_pull_sub_handler = on_pull_sub_handler
        self.pull_handler_args = pull_handler_args
        self.on_sub_handler = on_sub_handler
        self.sub_handler_args = sub_handler_args
        self.pull_socket = None
        self.sub_socket = None

    # Custom subclasses may wish to override the two hooks below.
    def on_before_msg_handler(self, msg, args):
        pass

    def on_after_msg_handler(self, msg, e=None, args=None):
        pass
    
    def start(self):
        Thread(target=self.listen).start()
        
    def close(self, pull_socket=None, sub_socket=None):
        self.keep_running = False
        ps = pull_socket if pull_socket else self.pull_socket
        ss = pull_socket if sub_socket else self.sub_socket
        
        if ps:
            ps.close()
        if ss:
            ss.close()
    
    def listen(self):
        
        poller = zmq.Poller()
        
        if self.pull_addr:
            self.pull_socket = self.zmq_context.socket(zmq.PULL)
            self.pull_socket.setsockopt(zmq.LINGER, 0)
            self.pull_socket.connect(self.pull_addr)
            poller.register(self.pull_socket, zmq.POLLIN)
            
            logger.debug('Starting PULL [{0}/{1}]'.format(
                self.name, self.pull_addr))
            
        if self.sub_addr:
            self.sub_socket = self.zmq_context.socket(zmq.SUB)
            self.sub_socket.setsockopt(zmq.LINGER, 0)
            self.sub_socket.connect(self.sub_addr)
            self.sub_socket.setsockopt(zmq.SUBSCRIBE, b'')
            poller.register(self.sub_socket, zmq.POLLIN)
            
            logger.debug('Starting SUB [{0}/{1}]'.format(
                self.name, self.sub_addr))
            
        _socks = [(name, sock) for (name, sock) in 
                  [('pull', self.pull_socket), ('sub', self.sub_socket)] if sock]
        del sock
        
        _handlers_args = {
            self.pull_socket: (self.on_pull_sub_handler, self.pull_handler_args),
            self.sub_socket: (self.on_sub_handler, self.sub_handler_args)}
        
        while self.keep_running:
            try:
                poll_socks = dict(poller.poll())
                for sock_name, sock in _socks:
                    if poll_socks.get(sock) == zmq.POLLIN:
                        msg = sock.recv()
            except Exception, e:
                # It's OK and needs not to disturb the user so log it only
                # in the DEBUG level.
                if isinstance(e, zmq.ZMQError) and e.errno == zmq.ETERM:
                    msg = '[{0}] Caught a zmq.ETERM [{1}], quitting'.format(
                        self.name, format_exc(e))
                    meth = logger.debug
                else:
                    msg = '[{0}] Caught an exception [{1}], quitting.'.format(
                        self.name, format_exc(e))
                    meth = logger.error
                    
                meth(msg)
                self.close()
            else:
                self.on_before_msg_handler(msg, self.pull_handler_args)
                try:
                    e = None
                    handler, args = _handlers_args[sock]
                    handler(msg, args)
                except Exception, e:
                    msg = '[{0}] Could not invoke the message handler, msg [{1}] sock_name [{2}] e [{3}]'
                    logger.error(msg.format(self.name, msg, sock_name, format_exc(e)))
                    
                self.on_after_msg_handler(msg, e, self.pull_handler_args)
                
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
    def __init__(self, init=False, **kwargs):
        self.zmq_context = kwargs.get('zmq_context')
        self.name = kwargs.get('name')
        self.push_addr = kwargs.get('push_addr')
        self.pull_addr = kwargs.get('pull_addr')
        self.sub_addr = kwargs.get('sub_addr')
        self.on_pull_handler = kwargs.get('on_pull_handler')
        self.pull_handler_args = kwargs.get('pull_handler_args')
        self.on_sub_handler = kwargs.get('on_sub_handler')
        self.sub_handler_args = kwargs.get('sub_handler_args')

        if init:
            self.init()
            
    def init(self):
        self._pull_sub = ZMQPullSub(self.name, self.zmq_context, self.pull_addr, 
            self.sub_addr, self.on_pull_handler, self.pull_handler_args,
            self.on_sub_handler, self.sub_handler_args)
        
        self._push = ZMQPush(self.name, self.zmq_context, self.push_addr)
        
    def set_pull_handler(self, handler):
        self._pull_sub.on_pull_handler = handler
        
    def set_pull_handler_args(self, args):
        self._pull_sub.pull_handler_args = args
        
    def set_sub_handler(self, handler):
        self._pull_sub.on_sub_handler = handler
        
    def set_sub_handler_args(self, args):
        self._pull_sub.sub_handler_args = args
    
    def start(self):
        self._pull_sub.start()
    
    def send(self, msg):
        return self._push.send(msg)
    
    def close(self):
        self._push.close()
        self._pull_sub.close()