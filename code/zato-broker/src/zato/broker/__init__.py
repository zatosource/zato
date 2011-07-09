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

# ZeroMQ
import zmq

# gevent
from gevent import spawn

# gevent_zeromq
from gevent_zeromq import zmq

# Default addresses
to_brok_address_pull = 'tcp://*:5100'
from_brok_address_push = 'tcp://*:5101'
from_brok_address_dealer = 'tcp://*:5102'

class Addresses(object):
    def __init__(self, pull=to_brok_address_pull, push=from_brok_address_push, 
                 dealer=from_brok_address_dealer):
        self.pull = pull
        self.push = push
        self.dealer = dealer

class BaseBroker(object):
    def __init__(self, addresses):
        self.addresses = addresses
        self.context = zmq.Context()
        self.keep_running = True
        
    def pre_run(self):
        
        self.to_broker_sock_pull = self.context.socket(zmq.PULL)
        self.to_broker_sock_pull.bind(self.addresses.pull)
        
        self.from_broker_sock_push = self.context.socket(zmq.PUSH)
        self.from_broker_sock_push.bind(self.addresses.push)
        
        self.from_broker_sock_dealer = self.context.socket(zmq.XREQ)
        self.from_broker_sock_dealer.bind(self.addresses.dealer)
        
    def run(self):
        self.pre_run()
        
        while self.keep_running:
            msg = self.to_broker_sock_pull.recv()
            spawn(self.on_message, msg)
        
    def on_message(self, msg):
        raise NotImplementedError()