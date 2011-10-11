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

# Monkey patch before importing anything else.

from gevent import monkey
monkey.patch_all()

# Bunch
from bunch import Bunch

# gevent
from gevent import spawn

# ZeroMQ
import zmq

# gevent_zeromq
from gevent_zeromq import zmq

# Default addresses
to_brok_address_pull = 'tcp://*:5100'
from_brok_address_push = 'tcp://*:5101'
from_brok_address_dealer = 'tcp://*:5102'

class SocketPair(object):
    def __init__(self, name=None, pull_addr=None, push_addr=None):
        self.name = name
        self.pull = pull_addr
        self.push = push_addr

class BaseBroker(object):
    def __init__(self, pairs):
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
            sock_pull.bind(pair.pull_addr)
            
            sock_push = self.context.socket(zmq.PUSH)
            sock_push.bind(pair.push_addr)
            
            self.sockets[pair.name].pull = sock_pull
            self.sockets[pair.name].push = sock_push
            
            self.pull_sockets.append(sock_pull)
            self.poller.register(sock_pull, zmq.POLLIN)
        
    def run(self):
        self.pre_run()
        
        while self.keep_running:
            socks = dict(self.poller.poll())
            for sock in self.pull_sockets:
                if socks.get(sock) == zmq.POLLIN:
                    msg = sock.recv()
                    spawn(self.on_message, msg)
        
    def on_message(self, msg):
        raise NotImplementedError()