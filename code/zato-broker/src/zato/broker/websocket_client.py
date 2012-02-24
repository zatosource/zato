# -*- coding: utf-8 -*-

"""
Copyright (C) 2012 Dariusz Suchojad <dsuch at gefira.pl>

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
from threading import Thread

# websocket-client
from websocket import WebSocketApp

class Client(object):
    def __init__(self, address):
        self.address = address
        self.sock = None

    def on_open(self, *args, **kwargs):
        print('on_open', args, kwargs)

    def on_message(self, *args, **kwargs):
        print('on_message', args, kwargs)

    def on_error(self, *args, **kwargs):
        print('on_error', args, kwargs)
        
    def on_close(self, *args, **kwargs):
        print('on_close', args, kwargs)
        
    def run(self):
        self.sock = WebSocketApp(self.address, self.on_open, self.on_message, self.on_error, self.on_close)
        self.sock.run_forever()
        
    def send(self, data):
        return self.sock.send(data)
    
if __name__ == '__main__':
    from time import sleep
    
    client = Client('ws://127.0.0.1:5100/zato')
    data = '111'
    
    t = Thread(target=client.run)
    t.start()
    
    sleep(1)
    
    client.send(data)
    
    t.join()