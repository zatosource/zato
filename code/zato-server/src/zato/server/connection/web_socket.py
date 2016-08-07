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
from bunch import Bunch, bunchify

# pyrapidjson
from rapidjson import dumps, loads

# ws4py
from ws4py.websocket import EchoWebSocket, WebSocket as _WebSocket
from ws4py.server.geventserver import WSGIServer
from ws4py.server.wsgiutils import WebSocketWSGIApplication

# Zato
from zato.common import DATA_FORMAT
from zato.common.util import new_cid
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
        DATA_FORMAT.JSON: dumps({'error': copy_forbidden}),
        DATA_FORMAT.XML: xml_error_template.format(copy_forbidden)
    },

    NOT_FOUND: {
        None: copy_not_found,
        DATA_FORMAT.JSON: dumps({'error': copy_not_found}),
        DATA_FORMAT.XML: xml_error_template.format(copy_not_found)
    }

}

# ################################################################################################################################

class Request(object):
    """ An individual message received from a WebSocket.
    """
    def __init__(self):
        self.action = None
        self.service = None
        self.sec_type = None
        self.username = None
        self.password = None
        self.id = None
        self.cid = new_cid()
        self.in_reply_to = None
        self.data = None
        self.is_authenticate = False

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

        self._parse_func = {
            DATA_FORMAT.JSON: self.parse_json,
            DATA_FORMAT.XML: self.parse_xml,
            None: lambda data: data
        }[self.config.data_format]

# ################################################################################################################################

    def parse_json(self, data):
        parsed = loads(data)

        meta = bunchify(parsed['meta'])

        request = Request()
        request.action = meta.action
        request.id = meta.id

        if request.action == 'authenticate':
            request.sec_type = meta.sec_type
            request.username = meta.username
            request.password = meta.password
            request.is_authenticate = True
        else:
            request.in_reply_to = meta.get('in_reply_to')
            request.data = parsed['data']

        return request

# ################################################################################################################################

    def parse_xml(self, data):
        pass

    def authenticate(self, request):
        if self.config.auth_func(request.cid, request.username, request.password, self.config.sec_name):
            return 'zxc'

# ################################################################################################################################

    def on_forbidden(self, action):
        logger.warn('Peer %s %s, closing connection to %s (%s)', self._peer_address, action,
            self._local_address, self.config.name)
        self.send(error_response[FORBIDDEN][self.config.data_format])
        self.close()

# ################################################################################################################################

    def received_message(self, message):

        request = self._parse_func(message.data)

        if self.is_authenticated:
            zzz
        else:
            if request.is_authenticate:
                response = self.authenticate(request)
                if response:
                    self.send(response, message.is_binary)
                else:
                    self.on_forbidden('sent invalid credentials')
            else:
                self.on_forbidden('not authenticated')

# ################################################################################################################################

    def run(self):
        try:
            super(WebSocket, self).run()
        except Exception, e:
            logger.warn(format_exc(e))

# ################################################################################################################################

    def opened(self):
        logger.info('New connection from %s to %s (%s)', self._peer_address, self._local_address, self.config.name)

        if not self.config.needs_auth:
            self.is_authenticated = True

# ################################################################################################################################

    def closed(self, code, reason=None):
        logger.info('Closing connection from %s to %s (%s)', self._peer_address, self._local_address, self.config.name)

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
    def __init__(self, config, auth_func):

        address_info = urlparse(config.address)

        config.host, config.port = address_info.netloc.split(':')
        config.port = int(config.port)

        config.path = address_info.path
        config.needs_tls = address_info.scheme == 'wss'
        config.auth_func = auth_func
        config.needs_auth = bool(config.sec_name)

        super(WebSocketServer, self).__init__((config.host, config.port), WebSocketContainer(config, handler_cls=WebSocket))

# ################################################################################################################################

class ChannelWebSocket(Connector):
    """ A WebSocket channel connector to which external client applications connect.
    """
    start_in_greenlet = True

    def _start(self):
        self.server = WebSocketServer(self.config, self.auth_func)
        self.server.serve_forever()

    def _stop(self):
        self.server.stop(3)

    def get_log_details(self):
        return self.config.address

# ################################################################################################################################
