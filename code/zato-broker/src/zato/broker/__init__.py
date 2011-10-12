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

# stdlib
import logging
from traceback import format_exc

# Bunch
from bunch import Bunch

# ZeroMQ
import zmq

logger = logging.getLogger(__name__)

class SocketPair(object):
    def __init__(self, name=None, pull=None, pub=None):
        self.name = name
        self.pull = pull
        self.pub = pub

class BaseBroker(object):
    def __init__(self, *pairs):
        self.pairs = pairs
        self.context = zmq.Context()
        self.keep_running = True
        self.sockets = Bunch()
        self.pull_sockets = []
        self.poller = zmq.Poller()
        
    def pre_run(self):
        """ Initialize all objects first.
        """
        
        for pair in self.pairs:
            sock_pull = self.context.socket(zmq.PULL)
            sock_pull.bind(pair.pull)
            
            sock_pub = self.context.socket(zmq.PUB)
            sock_pub.bind(pair.pub)
            
            self.sockets[pair.name] = Bunch()
            self.sockets[pair.name].pull = sock_pull
            self.sockets[pair.name].pub = sock_pub
            
            self.pull_sockets.append(sock_pull)
            self.poller.register(sock_pull, zmq.POLLIN)
        
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
        for pair in self.sockets.values():
            pair.pull.close()
            pair.pub.close()
            
        # .. and the context.
        self.context.term()
        
        msg = 'Closed ZMQ sockets and terminated the context'
        logger.info(msg)
        
    def on_message(self, msg):
        raise NotImplementedError()