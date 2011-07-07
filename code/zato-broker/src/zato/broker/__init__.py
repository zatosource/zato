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



from gevent import spawn

import gevent.monkey
gevent.monkey.patch_all()
#gevent.monkey.patch_httplib()

# stdlib
import logging, urllib2, ssl

# gevent_zeromq
from gevent_zeromq import zmq

# Zato
from zato.common.util import TRACE1

logger = logging.getLogger(__name__)

CONFIG_MESSAGE_PREFIX = 'ZATO_CONFIG'

# Default addresses
conf_sock_to_brok_address = 'tcp://*:5100'
conf_sock_from_brok_address = 'tcp://*:5101'

controller_sock_addr = 'tcp://*:5102'

class Broker(object):
    def __init__(self, conf_sock_to_brok_address, conf_sock_from_brok_address,
                 controller_sock_addr):
        self.conf_sock_to_brok_address = conf_sock_to_brok_address
        self.conf_sock_from_brok_address = conf_sock_from_brok_address
        self.controller_sock_addr = controller_sock_addr
        self.context = zmq.Context()

    def run(self):

        # PULL - for receiving updates to the configuration of Zato servers.
        self.conf_sock_to_brok = self.context.socket(zmq.PULL)
        self.conf_sock_to_brok.bind(self.conf_sock_to_brok_address)

        # PUB - for sending out updates to the configuration of Zato servers.
        self.conf_sock_from_brok = self.context.socket(zmq.PUB)
        self.conf_sock_from_brok.bind(self.conf_sock_from_brok_address)

        # PULL - for receiving requests of updating our own configuration.
        self.controller_socket = self.context.socket(zmq.PULL)
        self.controller_socket.bind(self.controller_sock_addr)

        poller = zmq.Poller()
        poller.register(self.conf_sock_to_brok)
        poller.register(self.conf_sock_from_brok)
        poller.register(self.controller_socket)

        keep_running = True

        while keep_running:
            #socks = dict(poller.poll())
            #if socks.get(self.conf_sock_to_brok) == zmq.POLLIN:

            message = self.conf_sock_to_brok.recv()

            print(22, message)

            cert = ssl.get_server_certificate(('duckduckgo.com', 443))
            print(cert)

            #req = urllib2.Request('http://example.com')
            #opener = urllib2.build_opener()
            #resp = opener.open(req)

            #response = resp.read()
            #resp.close()

            '''
                logger.log(TRACE1, 'Got a config message [{0}]'.format(message))

                self.conf_sock_from_brok.send(CONFIG_MESSAGE_PREFIX + ':' + message)

            elif socks.get(self.controller_socket) == zmq.POLLIN:

                message = self.controller_socket.recv()
                logger.log(TRACE1, 'Got a controller message [{0}]'.format(message))

                keep_running = False
                '''

if __name__ == '__main__':
    b = Broker(conf_sock_to_brok_address, conf_sock_from_brok_address,
               controller_sock_addr)
    spawn(b.run).join()
