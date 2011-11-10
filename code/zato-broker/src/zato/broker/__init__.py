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
    def __init__(self, name=None, pull=None, push=None, pub=None):
        self.name = name
        self.pull = pull
        self.push = push
        self.pub = pub
        
    def __repr__(self):
        return '<[{0}] at [{1}], name [{2}], pull [{3}], push [{4}], pub [{5}]>'.format(
            self.__class__.__name__, hex(id(self)), self.name, self.pull, 
            self.push, self.pub)

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
            
            if item.push:
                sock_push = self.context.socket(zmq.PUSH)
                sock_push.bind(item.push)
                self.sockets[item.name].push = sock_push
            
            if item.pull:
                sock_pull = self.context.socket(zmq.PULL)
                sock_pull.setsockopt(zmq.LINGER, 0)
                sock_pull.bind(item.pull)
                self.sockets[item.name].pull = sock_pull

                self.pull_sockets.append(sock_pull)
                self.poller.register(sock_pull, zmq.POLLIN)                
            
            if item.pub:
                sock_pub = self.context.socket(zmq.PUB)
                sock_pub.bind(item.pub)
                self.sockets[item.name].pub = sock_pub
                
    def run(self):
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