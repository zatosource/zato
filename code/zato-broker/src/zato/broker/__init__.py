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
to_brok_address = 'tcp://*:5100'
from_brok_address = 'tcp://*:5101'

class BaseBroker(object):
    def __init__(self, to_brok_address=to_brok_address, from_brok_address=from_brok_address):
        self.to_brok_address = to_brok_address
        self.from_brok_address = from_brok_address
        self.context = zmq.Context()
        self.keep_running = True
        
    def pre_run(self):
        
        self.to_broker_sock = self.context.socket(zmq.PULL)
        self.to_broker_sock.bind(self.to_brok_address)
        
        self.from_broker_sock = self.context.socket(zmq.PUSH)
        self.from_broker_sock.bind(self.from_brok_address)
        
    def run(self):
        self.pre_run()
        
        while self.keep_running:
            msg = self.to_broker_sock.recv()
            spawn(self.on_message, msg)
        
    def on_message(self, msg):
        raise NotImplementedError()