# -*- coding: utf-8 -*-

"""
Copyright (C) 2011 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

"""
Objects useful when implementing ZeroMQ clients. Written without any dependecies
on other partf of Zato code base so they can be re-used outside of the Zato project.
"""

# stdlib
import errno
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
    
    def __init__(self, name, zmq_context, broker_push_client_pull, broker_pub_client_sub,
                 on_pull_handler=None, pull_handler_args=None,
                 on_sub_handler=None, sub_handler_args=None, sub_key=b'', keep_running=True):
        self.name = name
        self.zmq_context = zmq_context
        self.broker_push_client_pull = broker_push_client_pull
        self.broker_pub_client_sub = broker_pub_client_sub
        self.keep_running = keep_running
        self.on_pull_handler = on_pull_handler
        self.pull_handler_args = pull_handler_args
        self.on_sub_handler = on_sub_handler
        self.sub_handler_args = sub_handler_args
        self.sub_key = sub_key
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
        ss = sub_socket if sub_socket else self.sub_socket
        
        if ps:
            ps.close()
        if ss:
            ss.close()
    
    def listen(self):
        
        _socks = []
        poller = zmq.Poller()
        
        if self.broker_push_client_pull:
            self.pull_socket = self.zmq_context.socket(zmq.PULL)
            self.pull_socket.setsockopt(zmq.LINGER, 0)
            self.pull_socket.connect(self.broker_push_client_pull)
            poller.register(self.pull_socket, zmq.POLLIN)
            _socks.append(('pull', self.pull_socket))
            
            logger.info('Starting PULL [{0}/{1}]'.format(
                self.name, self.broker_push_client_pull))
            
        if self.broker_pub_client_sub:
            self.sub_socket = self.zmq_context.socket(zmq.SUB)
            self.sub_socket.setsockopt(zmq.LINGER, 0)
            self.sub_socket.connect(self.broker_pub_client_sub)
            self.sub_socket.setsockopt(zmq.SUBSCRIBE, self.sub_key)
            poller.register(self.sub_socket, zmq.POLLIN)
            _socks.append(('sub', self.sub_socket))
            
            logger.info('Starting SUB [{0}/{1}]'.format(
                self.name, self.broker_pub_client_sub))
            
        _handlers_args = {}
        if self.pull_socket:
            _handlers_args[self.pull_socket] = (self.on_pull_handler, self.pull_handler_args)
        if self.sub_socket:
            _handlers_args[self.sub_socket] = (self.on_sub_handler, self.sub_handler_args)
            
        while self.keep_running:
            try:
                poll_socks = dict(poller.poll())
                for sock_name, sock in _socks:
                    if poll_socks.get(sock) == zmq.POLLIN:
                        msg = sock.recv()
                        try:
                            
                            e = None
                            args = None
                            
                            # A pre-hook, if any..
                            self.on_before_msg_handler(msg, self.pull_handler_args)
                            
                            # .. the actual handler ..
                            handler, args = _handlers_args[sock]
                            args = (args, sock_name)
                            handler(msg, args)
                        except Exception, e:
                            msg = '[{0}] Could not invoke the message handler, msg [{1}] sock_name [{2}] e [{3}]'
                            logger.error(msg.format(self.name, msg, sock_name, format_exc(e)))
                        finally:
                            # .. an after-hook, if any..
                            self.on_after_msg_handler(msg, args, e)
                        
            except Exception, e:
                # It's OK and needs not to disturb the user so log it only
                # in the DEBUG level.
                if isinstance(e, zmq.ZMQError) and(e.errno == zmq.ETERM or e.errno == errno.ENOTSOCK):
                    if e.errno == zmq.ETERM:
                        caught = 'zmq.ETERM'
                    elif e.errno == errno.ENOTSOCK:
                        caught = 'errno.ENOTSOCK'
                    msg = '[{0}] Caught [{1}] [{2}], quitting'.format(self.name, caught, format_exc(e))
                    log_func = logger.debug
                else:
                    e_errno = getattr(e, 'errno', None)
                    msg = '[{0}] Caught an exception [{1}], errno [{2}], quitting.'.format(
                        self.name, e_errno, format_exc(e))
                    log_func = logger.error
                    
                log_func(msg)
                self.close()
                    
class ZMQPush(object):
    """ Sends messages to ZeroMQ using a PUSH socket.
    """
    def __init__(self, name, zmq_context, address):
        self.name = name
        self.zmq_context = zmq_context
        self.address = address
        self.socket_type = zmq.PUSH
        
        logger.debug('Starting PUSH [{0}/{1}]'.format(self.name, self.address))

        self.socket = self.zmq_context.socket(self.socket_type)
        self.socket.setsockopt(zmq.LINGER, 0)
        self.socket.connect(self.address)
        
    def send(self, msg):
        try:
            self.socket.send_unicode(msg)
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug('Sent PUSH msg:[{}] to {}'.format(msg, self.address))
        except zmq.ZMQError, e:
            msg = '[{0}] Caught ZMQError [{1}], continuing anyway.'.format(
                self.name, e.strerror)
            logger.warn(msg)
        
    def close(self):
        msg = 'Stopping [[{0}/{1}/{2}]'.format(self.name, self.address, self.socket_type)
        logger.info(msg)
        self.socket.close()
        
class ZMQClient(object):
    """ A ZeroMQ broker client which knows how to subscribe to messages and push
    the messages onto the broker.
    """
    def __init__(self, init=False, **kwargs):
        self._push = None
        self._pull_sub = None
        self.zmq_context = kwargs.get('zmq_context')
        self.name = kwargs.get('name')
        self.broker_push_client_pull = kwargs.get('broker_push_client_pull')
        self.client_push_broker_pull = kwargs.get('client_push_broker_pull')
        self.broker_pub_client_sub = kwargs.get('broker_pub_client_sub')
        self.on_pull_handler = kwargs.get('on_pull_handler')
        self.pull_handler_args = kwargs.get('pull_handler_args')
        self.on_sub_handler = kwargs.get('on_sub_handler')
        self.sub_handler_args = kwargs.get('sub_handler_args')
        self.sub_key = kwargs.get('sub_key', b'')

        if init:
            self.init()
            
    def __repr__(self):
        return '<{0} at {1} name:[{2}] broker_push_client_pull:[{3}] '\
               'client_push_broker_pull:[{4}] broker_pub_client_sub:[{5}] '\
               'on_pull_handler:[{6}] pull_handler_args:[{7}] on_sub_handler:[{8}] '\
               'sub_handler_args:[{9}] sub_key:[{10}]'.format(
                   self.__class__.__name__,
                   hex(id(self)), self.name, self.broker_push_client_pull,
                   self.client_push_broker_pull, self.broker_pub_client_sub,
                   self.on_pull_handler, self.pull_handler_args,
                   self.on_sub_handler, self.sub_handler_args, self.sub_key)
            
    def init(self):
        if self.broker_pub_client_sub or self.broker_push_client_pull:
            self._pull_sub = ZMQPullSub(
                self.name, self.zmq_context, self.broker_push_client_pull,
                self.broker_pub_client_sub, self.on_pull_handler, self.pull_handler_args,
                self.on_sub_handler, self.sub_handler_args, self.sub_key)
        
        if self.client_push_broker_pull:
            self._push = ZMQPush(self.name, self.zmq_context, self.client_push_broker_pull)
        else:
            logger.debug('Client [{0}] has no [client_push_broker_pull] address defined'.format(self.name))
        
    def set_pull_handler(self, handler):
        self._pull_sub.on_pull_handler = handler
        
    def set_pull_handler_args(self, args):
        self._pull_sub.pull_handler_args = args
        
    def set_sub_handler(self, handler):
        self._pull_sub.on_sub_handler = handler
        
    def set_sub_handler_args(self, args):
        self._pull_sub.sub_handler_args = args
    
    def start(self):
        if self._pull_sub:
            self._pull_sub.start()
    
    def send(self, msg):
        return self._push.send(msg)
    
    def close(self):
        if self._push:
            self._push.close()
        if self._pull_sub:
            self._pull_sub.close()
            
        logger.info('Closed [{0}]'.format(self.get_connection_info()))
            
    def get_connection_info(self):
        return 'name:[{0}] client_pull:[{1}] client_push:[{2}] client_sub:[{3}] sub_key:[{4}]'.format(
            self.name, self.broker_push_client_pull, self.client_push_broker_pull, self.broker_pub_client_sub,
            self.sub_key)
