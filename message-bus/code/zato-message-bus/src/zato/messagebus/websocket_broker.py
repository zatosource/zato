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
import logging, os
from traceback import format_exc

# gevent
from gevent.pywsgi import WSGIServer
from gevent.coros import RLock

# gevent-websocket
from geventwebsocket import WebSocketError, WebSocketHandler

class Broker(WSGIServer):
    def __init__(self, host='', port=5100):
        super(Broker, self).__init__((host, port), self.on_connect, handler_class=WebSocketHandler)
        
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # All the connected clients
        self.clients = set()
        
        # An RLock for updating the list of connected clients
        self._client_update_lock = RLock()
        
        # The server-side of websockets will run as long as it's True
        self.keep_running = True
        
    def _on_bad_request(self, environ, start_response):
        """ The client must've sent something else than a WebSocket connection.
        """
        msg = '400 Bad Request, REMOTE_ADDR:[{}], PATH_INFO:[{}], QUERY_STRING:[{}], HTTP_USER_AGENT:[{}]'.format(
            environ.get('REMOTE_ADDR'), environ.get('PATH_INFO'), environ.get('QUERY_STRING'), environ.get('HTTP_USER_AGENT'))
        self.logger.error(msg)
        
        start_response('400 Bad Request', [])
        return ['WebSocket connection is expected here.']
        
    def _on_disconnect(self, sock):
        """ A client has disconnected.
        """
        with self._client_update_lock:
            self.clients.remove(sock)
            
    def _on_message(self, sock, message):
        print(11, sock, message)

        for client in self.clients:
            client.send('aaa')
        
        return 'OK'
    
    def on_connect(self, environ, start_response):
        """ A new client WebSocket connection has arrived.
        """
        sock = environ.get('wsgi.websocket')
        
        if sock is None:
            return self._on_bad_request(environ, start_response)

        with self._client_update_lock:
            self.clients.add(sock)        
        
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
            
        except Exception, e:
            msg = 'Exception caught [{0}]'.format(format_exc(e))
            self.logger.error(msg)
            
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    broker = Broker()
    broker.serve_forever()
