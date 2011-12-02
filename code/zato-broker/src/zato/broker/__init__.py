# -*- coding: utf-8 -*-

"""
Copyright (C) 2011 Dariusz Suchojad <dsuch at gefira.pl>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General pushlic License as pushlished by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General pushlic License for more details.

You should have received a copy of the GNU General pushlic License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

""" 
A base ZeroMQ message broker. Written without any dependecies on Zato code base 
so it can be re-used outside of the Zato project.
"""

# stdlib
import logging
from traceback import format_exc

# Bunch
from bunch import Bunch

# ZeroMQ
import zmq

logger = logging.getLogger(__name__)

class SocketData(object):
    def __init__(self, name=None, broker_push_client_pull=None, client_push_broker_pull=None, broker_pub_client_sub=None):
        self.name = name
        self.broker_push_client_pull = broker_push_client_pull
        self.client_push_broker_pull = client_push_broker_pull
        self.broker_pub_client_sub = broker_pub_client_sub
        
    def __repr__(self):
        return '<[{0}] at [{1}], name [{2}], broker_push_client_pull [{3}], client_push_broker_pull [{4}], broker_pub_client_sub [{5}]>'.format(
            self.__class__.__name__, hex(id(self)), self.name, self.broker_push_client_pull, 
            self.client_push_broker_pull, self.broker_pub_client_sub)

class BaseBroker(object):
    def __init__(self, *socket_data):
        self.socket_data = socket_data
        self.context = zmq.Context()
        self.keep_running = True
        self.sockets = Bunch()
        self.pull_sockets = []
        self.poller = zmq.Poller()
        
    def pre_run(self):
        """ Initialize all objects first.
        """
        
        for item in self.socket_data:
            logger.debug('Item [{0}]'.format(item))
            self.sockets[item.name] = Bunch()
            
            if item.broker_push_client_pull:
                sock = self.context.socket(zmq.PUSH)
                sock.bind(item.broker_push_client_pull)
                self.sockets[item.name].push = sock
                logger.debug('Binding [{0}] on behalf of [{1}] (broker_push_client_pull)'.format(sock, item.name))
                
            if item.client_push_broker_pull:
                sock = self.context.socket(zmq.PULL)
                sock.setsockopt(zmq.LINGER, 0)
                sock.bind(item.client_push_broker_pull)
                self.sockets[item.name].pull = sock

                self.pull_sockets.append(sock)
                self.poller.register(sock, zmq.POLLIN)                
                logger.debug('Binding [{0}] on behalf of [{1}] (client_push_broker_pull)'.format(sock, item.name))
            
            if item.broker_pub_client_sub:
                sock = self.context.socket(zmq.PUB)
                sock.bind(item.broker_pub_client_sub)
                self.sockets[item.name].pub = sock
                logger.debug('Binding [{0}] on behalf of [{1}] (broker_pub_client_sub)'.format(sock, item.name))
                
                
    def serve_forever(self):
        self.pre_run()
        while self.keep_running:
            try:
                socks = dict(self.poller.poll())
                for sock in self.pull_sockets:
                    if socks.get(sock) == zmq.POLLIN:
                        msg = sock.recv()
                        self.on_message(msg)
            except Exception, e:
                msg = 'Exception caught [{0}]'.format(format_exc(e))
                logger.error(msg)
                
        # Sockets ..
        for item in self.sockets.values():
            item.pull.close()
            item.push.close()
            if 'pub' in item:
                item.pub.close()
            
        # .. and the context.
        self.context.term()
        
        msg = 'Closed ZMQ sockets and terminated the context'
        logger.info(msg)
        
    def on_message(self, msg):
        raise NotImplementedError()