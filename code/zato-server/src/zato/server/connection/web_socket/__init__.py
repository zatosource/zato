# -*- coding: utf-8 -*-

"""
Copyright (C) 2016 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from copy import deepcopy
from datetime import datetime, timedelta
from httplib import FORBIDDEN, INTERNAL_SERVER_ERROR, NOT_FOUND, responses
from logging import getLogger
from traceback import format_exc
from urlparse import urlparse

# Bunch
from bunch import bunchify

# gevent
from gevent import sleep, socket, spawn
from gevent.lock import RLock

# pyrapidjson
from rapidjson import loads

# ws4py
from ws4py.websocket import WebSocket as _WebSocket
from ws4py.server.geventserver import WSGIServer
from ws4py.server.wsgiutils import WebSocketWSGIApplication

# Zato
from zato.common import CHANNEL, DATA_FORMAT, WEB_SOCKET
from zato.common.util import new_cid
from zato.server.connection.connector import Connector
from zato.server.connection.web_socket.msg import AuthenticateResponse, ClientInvokeRequest, ClientMessage, error_response, \
     ErrorResponse, OKResponse

# ################################################################################################################################

logger = getLogger('zato_web_socket')

# ################################################################################################################################

http404 = b'{} {}'.format(NOT_FOUND, responses[NOT_FOUND])

# ################################################################################################################################

class TokenInfo(object):
    def __init__(self, value, ttl, _now=datetime.utcnow):
        self.value = value
        self.ttl = ttl
        self.creation_time = _now()
        self.expires_at =  self.creation_time
        self.extend()

    def extend(self, _timedelta=timedelta):
        self.expires_at = self.expires_at + _timedelta(seconds=self.ttl)

# ################################################################################################################################

class WebSocket(_WebSocket):
    """ Encapsulates information about an individual connection from a WebSocket client.
    """
    def __init__(self, container, config, *args, **kwargs):
        super(WebSocket, self).__init__(*args, **kwargs)
        self.container = container
        self.config = config
        self.is_authenticated = False
        self._token = None
        self.update_lock = RLock()
        self.pub_client_id = 'ws.{}'.format(new_cid())
        self.ext_client_id = None
        self.ext_client_name = None
        self.connection_time = self.last_seen = datetime.utcnow()

        # Responses to previously sent requests - keyed by request IDs
        self.responses_received = {}

        _local_address = self.sock.getsockname()
        self._local_address = '{}:{}'.format(_local_address[0], _local_address[1])

        _peer_address = self.sock.getpeername()
        self._peer_address = '{}:{}'.format(_peer_address[0], _peer_address[1])

        _peer_fqdn = '(Unknown)'

        try:
            _peer_host = socket.gethostbyaddr(_peer_address[0])[0]
            _peer_fqdn = socket.getfqdn(_peer_host)
        except Exception, e:
            logger.warn(format_exc(e))
        finally:
            self._peer_fqdn = _peer_fqdn

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

    def parse_json(self, data, _auth=WEB_SOCKET.ACTION.AUTHENTICATE, _response=WEB_SOCKET.ACTION.CLIENT_RESPONSE):

        parsed = loads(data)
        msg = ClientMessage()

        meta = parsed.get('meta', {})

        if meta:
            meta = bunchify(meta)

            msg.action = meta.action
            msg.id = meta.id
            msg.timestamp = meta.timestamp
            msg.ext_client_id = meta.client_id
            msg.ext_client_name = meta.get('client_name')

            if msg.action == _auth:
                msg.sec_type = meta.sec_type
                msg.username = meta.username
                msg.secret = meta.secret
                msg.has_credentials = True
            else:
                msg.in_reply_to = meta.get('in_reply_to')

        _data = parsed.get('data', {}).get('input')
        msg.data =_data['response'] if msg.action == _response else _data

        return msg

# ################################################################################################################################

    def parse_xml(self, data):
        raise NotImplementedError('Not supported yet')

# ################################################################################################################################

    def authenticate(self, request):
        if self.config.auth_func(request.cid, request.sec_type, request.username, request.secret, self.config.sec_name):

            with self.update_lock:
                self.token = 'ws.token.{}'.format(new_cid())
                self.is_authenticated = True
                self.ext_client_id = request.ext_client_id
                self.ext_client_name = request.ext_client_name

            return AuthenticateResponse(self.token.value, request.id).serialize()

# ################################################################################################################################

    def on_forbidden(self, action):
        logger.warn(
            'Peer %s %s, closing its connection to %s (%s)', self._peer_address, action, self._local_address, self.config.name)
        self.send(error_response[FORBIDDEN][self.config.data_format])

        self.server_terminated = True
        self.client_terminated = True

# ################################################################################################################################

    def register_auth_client(self):
        """ Registers peer in ODB. Called only if authentication succeeded.
        """
        self.invoke_service(new_cid(), 'zato.channel.web-socket.client.create', {
            'pub_client_id': self.pub_client_id,
            'ext_client_id': self.ext_client_id,
            'ext_client_name': self.ext_client_name,
            'is_internal': True,
            'local_address': self.local_address,
            'peer_address': self.peer_address,
            'peer_fqdn': self._peer_fqdn,
            'connection_time': self.connection_time,
            'last_seen': self.last_seen,
            'channel_name': self.config.name,
        }, needs_response=True)

# ################################################################################################################################

    def unregister_auth_client(self):
        """ Unregisters an already registered peer in ODB.
        """
        if self.is_authenticated:
            self.invoke_service(new_cid(), 'zato.channel.web-socket.client.delete-by-pub-id', {
                'pub_client_id': self.pub_client_id,
            }, needs_response=True)

# ################################################################################################################################

    def handle_authenticate(self, request):
        if request.has_credentials:
            response = self.authenticate(request)
            if response:
                self.send(response)
                self.register_auth_client()
                logger.info(
                    'Client %s (%s %s) logged in successfully to %s (%s)', self._peer_address, self._peer_fqdn,
                    self.pub_client_id, self._local_address, self.config.name)
            else:
                self.on_forbidden('sent invalid credentials')
        else:
            self.on_forbidden('is not authenticated')

# ################################################################################################################################

    def invoke_service(self, cid, service_name, data, needs_response=True, _channel=CHANNEL.WEB_SOCKET,
            _data_format=DATA_FORMAT.DICT):

        return self.config.on_message_callback({
            'cid': cid,
            'data_format': _data_format,
            'service': service_name,
            'payload': data,
        }, CHANNEL.WEB_SOCKET, None, needs_response=needs_response, serialize=False)

# ################################################################################################################################

    def handle_client_message(self, cid, msg, _action=WEB_SOCKET.ACTION):
        self._handle_client_response(cid, msg) if msg.action == _action.CLIENT_RESPONSE else self._handle_invoke_service(cid, msg)

# ################################################################################################################################

    def _handle_invoke_service(self, cid, msg):

        try:
            service_response = self.invoke_service(cid, self.config.service_name, msg.data)
        except Exception, e:

            logger.warn('Service `%s` could not be invoked, id:`%s` cid:`%s`, e:`%s`', self.config.service_name, msg.id,
                cid, format_exc(e))

            response = ErrorResponse(cid, msg.id, INTERNAL_SERVER_ERROR,
                    'Could not invoke service `{}`, id:`{}`, cid:`{}`'.format(self.config.service_name, msg.id, cid))
        else:
            response = OKResponse(msg.id, service_response)

        self.send(response.serialize())

# ################################################################################################################################

    def _wait_for_event(self, wait_time, condition_callable, _now=datetime.utcnow, _delta=timedelta,
                        _sleep=sleep, *args, **kwargs):
        now = _now()
        until = now + _delta(seconds=wait_time)

        while now < until:

            response = condition_callable(*args, **kwargs)
            if response:
                return response
            else:
                _sleep(0.01)
                now = _now()

# ################################################################################################################################

    def _handle_client_response(self, cid, msg):
        self.responses_received[msg.in_reply_to] = msg

    def _has_client_response(self, request_id):
        return self.responses_received.get(request_id)

    def _wait_for_client_response(self, request_id, wait_time=1):
        """ Wait until a response from client arrives and return it or return None if there is no response up to wait_time.
        """
        return self._wait_for_event(wait_time, self._has_client_response, request_id=request_id)

# ################################################################################################################################

    def _received_message(self, data, _now=datetime.utcnow, _default_data='', *args, **kwargs):

        try:

            request = self._parse_func(data or _default_data)
            cid = new_cid()
            now = _now()
            self.last_seen = now

            logger.info('Request received cid:`%s`, client:`%s`', cid, self.pub_client_id)

            # If client is authenticated we allow either for it to re-authenticate, which grants a new token, or to invoke a service.
            # Otherwise, authentication is required.

            if self.is_authenticated:
                self.handle_client_message(cid, request) if not request.has_credentials else self.handle_authenticate(request)
            else:
                self.handle_authenticate(request)

            logger.info('Response returned cid:`%s`, time:`%s`', cid, _now()-now)

        except Exception, e:
            logger.warn(format_exc(e))

    def received_message(self, message):
        try:
            spawn(self._received_message, deepcopy(message.data))
        except Exception, e:
            logger.warn(format_exc(e))

# ################################################################################################################################

    def run(self):
        try:
            super(WebSocket, self).run()
        except Exception, e:
            logger.warn(format_exc(e))

# ################################################################################################################################

    def _ensure_authenticated(self, _now=datetime.utcnow):
        """ Runs in its own greenlet and waits for an authentication request to arrive by self.authenticate_by,
        which is a timestamp object. If self.is_authenticated is not True by that time, connection to the remote end
        is closed.
        """
        if self._wait_for_event(self.config.new_token_wait_time, lambda: self.is_authenticated):
            return

        # We get here if self.is_authenticated has not been set to True by self.authenticate_by
        self.on_forbidden('did not authenticate within {}s'.format(self.config.new_token_wait_time))

# ################################################################################################################################

    def invoke_client(self, cid, request):
        msg = ClientInvokeRequest(cid, request)
        self.send(msg.serialize())

        response = self._wait_for_client_response(msg.id)
        if response:
            return response.data

# ################################################################################################################################

    def opened(self, _now=datetime.utcnow, _timedelta=timedelta):
        logger.info('New connection from %s (%s) to %s (%s)', self._peer_address, self._peer_fqdn,
            self._local_address, self.config.name)

        if not self.config.needs_auth:
            with self.update_lock:
                self.is_authenticated = True
        else:
            spawn(self._ensure_authenticated)

# ################################################################################################################################

    def closed(self, code, reason=None):
        logger.info('Closing connection from %s (%s) to %s (%s %s)',
            self._peer_address, self._peer_fqdn, self._local_address, self.pub_client_id, self.config.name)

        self.unregister_auth_client()
        del self.container.clients[self.pub_client_id]

# ################################################################################################################################

class WebSocketContainer(WebSocketWSGIApplication):

    def __init__(self, config, *args, **kwargs):
        self.config = config
        self.clients = {}
        super(WebSocketContainer, self).__init__(*args, **kwargs)

    def make_websocket(self, sock, protocols, extensions, environ):
        try:
            websocket = self.handler_cls(self, self.config, sock, protocols, extensions, environ.copy())
            self.clients[websocket.pub_client_id] = websocket
            environ['ws4py.websocket'] = websocket
            return websocket
        except Exception, e:
            logger.warn(format_exc(e))

    def __call__(self, environ, start_response):

        if environ['PATH_INFO'] != self.config.path:
            start_response(http404, {})
            return [error_response[NOT_FOUND][self.config.data_format]]

        super(WebSocketContainer, self).__call__(environ, start_response)

    def invoke_client(self, cid, pub_client_id, request):
        return self.clients[pub_client_id].invoke_client(cid, request)

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

    def invoke_client(self, cid, pub_client_id, request):
        return self.application.invoke_client(cid, pub_client_id, request)

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

    def invoke(self, cid, pub_client_id, request):
        return self.server.invoke_client(cid, pub_client_id, request)

# ################################################################################################################################

