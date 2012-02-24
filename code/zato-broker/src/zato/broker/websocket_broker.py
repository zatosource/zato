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
import os

# gevent
from gevent.pywsgi import WSGIServer
from gevent.coros import RLock

# gevent-websocket
from geventwebsocket import WebSocketError, WebSocketHandler

class Broker(WSGIServer):
    def __init__(self, host='', port=5100):
        super(Broker, self).__init__((host, port), self.on_connect, handler_class=WebSocketHandler)
        
        # All the connected clients
        self.clients = []
        
        # An RLock for updating the list of connected clients
        self._update_lock = RLock()
        
        # The server-side of websockets will run as long as it's True
        self.keep_running = True
        
    def _on_disconnect(self, sock):
        """ A client has disconnected.
        """
        with self._update_lock:
            print(22, sock)
            
    def _on_message(self, sock, message):
        print(11, sock, message)

        for client in self.clients:
            client.send('aaa')
        
        return 'OK'
    
    def on_connect(self, environ, start_response):
        """ A new client WebSocket connection has arrived.
        """
        sock = environ.get('wsgi.websocket')
        self.clients.append(sock)
        
        #for(k, v) in sorted(environ.items()):
        #    print(k, v)
        
        if sock is None:
            start_response('400 Bad Request', [])
            return ['WebSocket connection is expected here.']
        try:
            while self.keep_running:
                
                # Has there been any message for us?
                message = sock.receive()
                
                # It must be client's disconnected.
                if message is None:
                    self._on_disconnect(sock)
                    break
                
                # Handle the message.
                response = self._on_message(sock, message)
                sock.send(response)
                
            # The broker's shutting down, we're closing the connection.
            sock.close()
            
        except WebSocketError, ex:
            print("%s: %s" % (ex.__class__.__name__, ex))
            
if __name__ == '__main__':
    broker = Broker()
    broker.serve_forever()
