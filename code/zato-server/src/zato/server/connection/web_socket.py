# -*- coding: utf-8 -*-

"""
Copyright (C) 2016 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from httplib import FORBIDDEN, NOT_FOUND, responses
from logging import getLogger
from traceback import format_exc
from urlparse import urlparse

# Bunch
from bunch import Bunch

# ws4py
from ws4py.websocket import EchoWebSocket, WebSocket as _WebSocket
from ws4py.server.geventserver import WSGIServer
from ws4py.server.wsgiutils import WebSocketWSGIApplication

# Zato
from zato.common import DATA_FORMAT
from zato.server.connection.connector import Connector

# ################################################################################################################################

logger = getLogger('zato_web_socket')

# ################################################################################################################################

# Note that we always return forbidden even if unathorized could make sense because we do not want
# to tell anyone what are expect authentication methods are.

http403 = b'{} {}'.format(FORBIDDEN, responses[FORBIDDEN])
http404 = b'{} {}'.format(NOT_FOUND, responses[NOT_FOUND])

xml_error_template = '<?xml version="1.0" encoding="utf-8"?><error>{}</error>'

copy_forbidden = b'You are not authorized to access this resource'
copy_not_found = b'Not found'

error_response = {

    FORBIDDEN: {
        None: copy_forbidden,
        DATA_FORMAT.JSON: {'error': copy_forbidden},
        DATA_FORMAT.XML: xml_error_template.format(copy_forbidden)
    },

    NOT_FOUND: {
        None: copy_not_found,
        DATA_FORMAT.JSON: {'error': copy_not_found},
        DATA_FORMAT.XML: xml_error_template.format(copy_not_found)
    }

}

# ################################################################################################################################

class WebSocket(_WebSocket):
    """ Encapsulates an individual connection from a WebSocket client.
    """
    def __init__(self, container, config, *args, **kwargs):
        super(WebSocket, self).__init__(*args, **kwargs)
        self.container = container
        self.config = config
        self.is_authenticated = False

        _local_address = self.sock.getsockname()
        self._local_address = '{}:{}'.format(_local_address[0], _local_address[1])

        _peer_address = self.sock.getpeername()
        self._peer_address = '{}:{}'.format(_peer_address[0], _peer_address[1])

    def opened(self):
        logger.info('New connection from %s to %s (%s)', self._peer_address, self._local_address, self.config.name)

    def closed(self, code, reason=None):
        logger.info('Closing connection from %s to %s (%s)', self._peer_address, self._local_address, self.config.name)

    def received_message(self, message):

        if not self.is_authenticated:
            logger.warn('Peer %s not authenticated, closing connection to %s (%s)', self._peer_address, self._local_address,
                self.config.name)
            self.send(error_response[FORBIDDEN][self.config.data_format])
            self.close()

        self.send('qqq', message.is_binary)

    def run(self):
        try:
            super(WebSocket, self).run()
        except Exception, e:
            logger.warn(format_exc(e))

# ################################################################################################################################

class WebSocketContainer(WebSocketWSGIApplication):

    def __init__(self, config, *args, **kwargs):
        self.config = config
        super(WebSocketContainer, self).__init__(*args, **kwargs)

    def make_websocket(self, sock, protocols, extensions, environ):
        try:
            websocket = self.handler_cls(self, self.config, sock, protocols, extensions, environ.copy())
            environ['ws4py.websocket'] = websocket
            return websocket
        except Exception, e:
            logger.warn(format_exc(e))

    def __call__(self, environ, start_response):

        if environ['PATH_INFO'] != self.config.path:
            start_response(http404, {})
            return [error_response[NOT_FOUND][self.config.data_format]]

        super(WebSocketContainer, self).__call__(environ, start_response)

# ################################################################################################################################

class WebSocketServer(WSGIServer):
    """ A WebSocket server exposing Zato services to client applications.
    """
    def __init__(self, config):

        address_info = urlparse(config.address)

        config.host, config.port = address_info.netloc.split(':')
        config.port = int(config.port)

        config.path = address_info.path
        config.needs_tls = address_info.scheme == 'wss'

        super(WebSocketServer, self).__init__((config.host, config.port), WebSocketContainer(config, handler_cls=WebSocket))

# ################################################################################################################################

class ChannelWebSocket(Connector):
    """ A WebSocket channel connector to which external client applications connect.
    """
    start_in_greenlet = True

    def _start(self):
        self.server = WebSocketServer(self.config)
        self.server.serve_forever()

    def _stop(self):
        self.server.stop(1)

    def get_log_details(self):
        return self.config.address

# ################################################################################################################################
