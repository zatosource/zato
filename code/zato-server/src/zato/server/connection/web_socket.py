# -*- coding: utf-8 -*-

"""
Copyright (C) 2016 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from datetime import datetime, timedelta
from httplib import BAD_REQUEST, FORBIDDEN, NOT_FOUND, OK, responses
from logging import getLogger
from traceback import format_exc
from urlparse import urlparse

# Bunch
from bunch import Bunch, bunchify

# gevent
from gevent.lock import RLock

# pyrapidjson
from rapidjson import dumps, loads

# ws4py
from ws4py.websocket import EchoWebSocket, WebSocket as _WebSocket
from ws4py.server.geventserver import WSGIServer
from ws4py.server.wsgiutils import WebSocketWSGIApplication

# Zato
from zato.common import CHANNEL, DATA_FORMAT, WEB_SOCKET
from zato.common.util import make_repr, new_cid
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
        DATA_FORMAT.JSON: dumps({'error': copy_forbidden}),
        DATA_FORMAT.XML: xml_error_template.format(copy_forbidden)
    },

    NOT_FOUND: {
        DATA_FORMAT.JSON: dumps({'error': copy_not_found}),
        DATA_FORMAT.XML: xml_error_template.format(copy_not_found)
    }

}

# ################################################################################################################################

class ClientMessage(object):
    """ An individual message received from a WebSocket client.
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
        self.data = Bunch()
        self.has_credentials = False
        self.token = None

    def __repr__(self):
        return make_repr(self)

# ################################################################################################################################

class ServerMessage(object):
    """ A message sent from a WebSocket server to a client.
    """
    def __init__(self, id_prefix, in_reply_to, status=OK, error_message=''):
        self.id = '{}.{}'.format(id_prefix, new_cid())
        self.in_reply_to = in_reply_to
        self.meta = Bunch(id=self.id, in_reply_to=in_reply_to, status=status)
        self.data = Bunch()

        if error_message:
            self.meta.error_message = error_message

    def serialize(self):
        return dumps({
            'meta': self.meta,
            'data': self.data,
        })

# ################################################################################################################################

class AuthenticateResponse(ServerMessage):
    def __init__(self, token, *args, **kwargs):
        super(AuthenticateResponse, self).__init__('ws.auth', *args, **kwargs)
        self.data.token = token

# ################################################################################################################################

class ServiceInvokeResponse(ServerMessage):
    def __init__(self, in_reply_to, data):
        super(ServiceInvokeResponse, self).__init__('ws.si', in_reply_to)
        self.data = data

# ################################################################################################################################

class TokenInfo(object):
    def __init__(self, value, ttl, _utcnow=datetime.utcnow):
        self.value = value
        self.ttl = ttl
        self.creation_time = _utcnow()
        self.expires_at =  self.creation_time
        self.extend()

    def extend(self, _timedelta=timedelta):
        self.expires_at = self.expires_at + _timedelta(seconds=self.ttl)

# ################################################################################################################################

class WebSocket(_WebSocket):
    """ Encapsulates an individual connection from a WebSocket client.
    """
    def __init__(self, container, config, *args, **kwargs):
        super(WebSocket, self).__init__(*args, **kwargs)
        self.container = container
        self.config = config
        self.is_authenticated = False
        self._token = None
        self.update_lock = RLock()

        _local_address = self.sock.getsockname()
        self._local_address = '{}:{}'.format(_local_address[0], _local_address[1])

        _peer_address = self.sock.getpeername()
        self._peer_address = '{}:{}'.format(_peer_address[0], _peer_address[1])

        self._parse_func = {
            DATA_FORMAT.JSON: self.parse_json,
            DATA_FORMAT.XML: self.parse_xml,
        }[self.config.data_format]

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, value):

        if not self._token:
            self._token = TokenInfo(value, self.config.token_ttl)
        else:
            self._token.value = value
            self._token.extend()

# ################################################################################################################################

    def parse_json(self, data, _auth_action=WEB_SOCKET.ACTION.AUTHENTICATE):
        parsed = loads(data)

        meta = bunchify(parsed['meta'])

        request = ClientMessage()
        request.action = meta.action
        request.id = meta.id

        if request.action == _auth_action:
            request.sec_type = meta.sec_type
            request.username = meta.username
            request.password = meta.password
            request.has_credentials = True
        else:
            request.in_reply_to = meta.get('in_reply_to')
            request.data = parsed['data']

        return request

# ################################################################################################################################

    def parse_xml(self, data):
        raise NotImplementedError('Not supported yet')

# ################################################################################################################################

    def authenticate(self, request):
        if self.config.auth_func(request.cid, request.username, request.password, self.config.sec_name):

            with self.update_lock:
                self.token = 'ws.token.{}'.format(new_cid())
                self.is_authenticated = True

            return AuthenticateResponse(self.token.value, request.id).serialize()

# ################################################################################################################################

    def on_forbidden(self, action):
        logger.warn(
            'Peer %s %s, closing connection to %s (%s)', self._peer_address, action, self._local_address, self.config.name)
        self.send(error_response[FORBIDDEN][self.config.data_format])
        self.close()

# ################################################################################################################################

    def handle_authenticate(self, request):
        if request.has_credentials:
            response = self.authenticate(request)
            if response:
                self.send(response)
            else:
                self.on_forbidden('sent invalid credentials')
        else:
            self.on_forbidden('not authenticated')

# ################################################################################################################################

    def handle_invoke_service(self, request, _channel=CHANNEL.WEB_SOCKET, _data_format=DATA_FORMAT.DICT):
        try:

            service_response = self.config.on_message_callback({
                'cid': new_cid(),
                'data_format': _data_format,
                'service': self.config.service_name,
                'payload': request.data,
            }, CHANNEL.WEB_SOCKET, None, needs_response=True, serialize=False)

        except Exception, e:
            logger.warn(format_exc(e))
            service_response = {'aa': format_exc(e)}

        self.send(ServiceInvokeResponse(request.id, service_response).serialize())

# ################################################################################################################################

    def received_message(self, message):
        request = self._parse_func(message.data)

        # If client is authenticated we allow either for it to re-authenticate, which grants a new token, or to invoke a service.
        # Otherwise, authentication is required.

        if self.is_authenticated:
            self.handle_invoke_service(request) if not request.has_credentials else self.handle_authenticate(request)
        else:
            self.handle_authenticate(request)

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
            with self.update_lock:
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
    def __init__(self, config, auth_func, on_message_callback):

        address_info = urlparse(config.address)

        config.host, config.port = address_info.netloc.split(':')
        config.port = int(config.port)

        config.path = address_info.path
        config.needs_tls = address_info.scheme == 'wss'
        config.auth_func = auth_func
        config.on_message_callback = on_message_callback
        config.needs_auth = bool(config.sec_name)

        super(WebSocketServer, self).__init__((config.host, config.port), WebSocketContainer(config, handler_cls=WebSocket))

# ################################################################################################################################

class ChannelWebSocket(Connector):
    """ A WebSocket channel connector to which external client applications connect.
    """
    start_in_greenlet = True

    def _start(self):
        self.server = WebSocketServer(self.config, self.auth_func, self.on_message_callback)
        self.server.serve_forever()

    def _stop(self):
        self.server.stop(3)

    def get_log_details(self):
        return self.config.address

# ################################################################################################################################
