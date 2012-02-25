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
import websocket
from websocket import WebSocket, WebSocketApp, WebSocketException

websocket.enableTrace(22)

class _App(WebSocketApp):
    def __init__(self, *args, **kwargs):
        super(_App, self).__init__(*args, **kwargs)
        self.keep_running = True
    
    def run_forever(self):
        """
        run event loop for WebSocket framework.
        This loop is infinite loop and is alive during websocket is available.
        """
        if self.sock:
            raise WebSocketException("socket is already opened")
        try:
            self.sock = WebSocket()
            self.sock.connect(self.url)
            self._run_with_no_err(self.on_open)
            while self.keep_running:
                data = self.sock.recv()
                if data is None:
                    break
                self._run_with_no_err(self.on_message, data)
        except Exception, e:
            self._run_with_no_err(self.on_error, e)
        finally:
            self.sock.close()
            self._run_with_no_err(self.on_close)
            self.sock = None

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
        self.sock = _App(self.address, self.on_open, self.on_message, self.on_error, self.on_close)
        self.sock.run_forever()
        
    def stop(self):
        self.sock.keep_running = False
        
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
    
    client.stop()
    t.join()