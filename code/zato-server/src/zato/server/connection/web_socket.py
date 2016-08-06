# -*- coding: utf-8 -*-

"""
Copyright (C) 2016 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from httplib import FORBIDDEN, NOT_FOUND, responses
from logging import getLogger
from urlparse import urlparse

# Bunch
from bunch import Bunch

# ws4py
from ws4py.websocket import EchoWebSocket, WebSocket
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

class WebSocketHandler(WebSocket):
    """ Encapsulates an individual connection from a WebSocket client.
    """
    def __init__(self, config, *args, **kwargs):
        super(WebSocketHandler, self).__init__(*args, **kwargs)
        self.config = config

    def opened(self):
        print('zzz opened', self.sock)

    def closed(self, code, reason=None):
        print('aaa', code, reason)

    def received_message(self, message):
        self.send('qqq', message.is_binary)

# ################################################################################################################################

class WSGIApplication(WebSocketWSGIApplication):

    def __init__(self, config, *args, **kwargs):
        self.config = config
        super(WSGIApplication, self).__init__(*args, **kwargs)

    def make_websocket(self, sock, protocols, extensions, environ):
        websocket = self.handler_cls(self.config, sock, protocols, extensions, environ.copy())
        environ['ws4py.websocket'] = websocket
        return websocket

    def __call__(self, environ, start_response):

        logger.info('111\n%s', self.config)

        if environ['PATH_INFO'] != self.config.path:
            start_response(http404, {})
            return [error_response[NOT_FOUND][self.config.data_format]]

        super(WSGIApplication, self).__call__(environ, start_response)

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

        super(WebSocketServer, self).__init__((config.host, config.port), WSGIApplication(config, handler_cls=WebSocketHandler))

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
