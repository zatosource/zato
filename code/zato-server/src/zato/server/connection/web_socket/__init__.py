# -*- coding: utf-8 -*-

"""
Copyright (C) 2016 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from copy import deepcopy
from datetime import datetime, timedelta
from httplib import INTERNAL_SERVER_ERROR, NOT_FOUND, responses
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
from zato.server.connection.web_socket.msg import AuthenticateResponse, ClientInvokeRequest, ClientMessage, copy_forbidden, \
     error_response, ErrorResponse, Forbidden, OKResponse

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

    def extend(self, extend_by=None, _timedelta=timedelta):
        self.expires_at = self.expires_at + _timedelta(seconds=extend_by or self.ttl)

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
        self.sec_type = self.config.sec_type
        self.pings_missed = 0
        self.pings_missed_threshold = self.config.get('pings_missed_threshold', 5)
        self.ping_last_response_time = None

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

            msg.action = meta.get('action', _response)
            msg.id = meta.id
            msg.timestamp = meta.timestamp
            msg.token = meta.get('token') # Optional because it won't exist during first authentication

            # self.ext_client_id and self.ext_client_name will exist after authenticate action
            # so we use them if they are available but fall back to meta.client_id and meta.client_name during
            # the very authenticate action.
            msg.ext_client_id = self.ext_client_id or meta.client_id
            msg.ext_client_name = self.ext_client_name or meta.get('client_name')

            if msg.action == _auth:
                msg.username = meta.get('username')
                msg.secret = meta.secret
                msg.is_auth = True
            else:
                msg.in_reply_to = meta.get('in_reply_to')
                msg.is_auth = False

        msg.data = parsed.get('data', {})

        return msg

# ################################################################################################################################

    def parse_xml(self, data):
        raise NotImplementedError('Not supported yet')

# ################################################################################################################################

    def authenticate(self, cid, request):
        if self.config.auth_func(request.cid, self.sec_type, {'username':request.username, 'secret':request.secret},
            self.config.sec_name, self.config.vault_conn_default_auth_method):

            with self.update_lock:
                self.token = 'ws.token.{}'.format(new_cid())
                self.is_authenticated = True
                self.ext_client_id = request.ext_client_id
                self.ext_client_name = request.ext_client_name

            return AuthenticateResponse(self.token.value, request.cid, request.id).serialize()

# ################################################################################################################################

    def on_forbidden(self, action, data=copy_forbidden):
        cid = new_cid()
        logger.warn(
            'Peer %s (%s) %s, closing its connection to %s (%s), cid:`%s`', self._peer_address, self._peer_fqdn, action,
            self._local_address, self.config.name, cid)
        self.send(Forbidden(cid, data).serialize())

        self.server_terminated = True
        self.client_terminated = True

# ################################################################################################################################

    def send_background_pings(self, ping_extend=30):
        try:
            while self.stream:

                # Sleep for N seconds before sending a ping but check if we are connected upfront because
                # we could have disconnected in between while and sleep calls.
                sleep(ping_extend)

                # Ok, still connected
                if self.stream:
                    response = self.invoke_client(new_cid(), None, False)

                    with self.update_lock:
                        if response:
                            self.pings_missed = 0
                            self.ping_last_response_time = datetime.utcnow()
                            self.token.extend(ping_extend)
                        else:
                            # self._peer_address, action, self._local_address, self.config.name
                            self.pings_missed += 1
                            if self.pings_missed < self.pings_missed_threshold:
                                logger.warn(
                                    'Peer %s (%s) missed %s/%s ping messages from %s (%s). Last response time: %s{}'.format(
                                        ' UTC' if self.ping_last_response_time else ''),
                                    self._peer_address, self._peer_fqdn, self.pings_missed, self.pings_missed_threshold,
                                    self._local_address, self.config.name, self.ping_last_response_time)
                            else:
                                self.on_forbidden('missed {}/{} ping messages'.format(
                                    self.pings_missed, self.pings_missed_threshold))

                # No stream = already disconnected, we can quit
                else:
                    return

        except Exception, e:
            logger.warn(format_exc(e))

# ################################################################################################################################

    def register_auth_client(self):
        """ Registers peer in ODB and sets up background pings to keep its connection alive.
        Called only if authentication succeeded.
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

        spawn(self.send_background_pings)

# ################################################################################################################################

    def unregister_auth_client(self):
        """ Unregisters an already registered peer in ODB.
        """
        if self.is_authenticated:
            self.invoke_service(new_cid(), 'zato.channel.web-socket.client.delete-by-pub-id', {
                'pub_client_id': self.pub_client_id,
            }, needs_response=True)

# ################################################################################################################################

    def handle_authenticate(self, cid, request):
        if request.is_auth:
            response = self.authenticate(cid, request)
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
            'environ': {'pub_client_id': self.pub_client_id},
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
            response = OKResponse(cid, msg.id, service_response)

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

            # If client is authenticated, allow it to re-authenticate, which grants a new token, or to invoke a service.
            # Otherwise, authentication is required.

            if self.is_authenticated:

                # Reject request if an already existing token was not given on input, it should have been
                # because the client is authenticated after all.
                if not request.token:
                    self.on_forbidden('did not send token')
                    return

                # Reject request if token is provided but it already expired
                if _now() > self.token.expires_at:
                    self.on_forbidden('used an expired token')
                    return

                # Ok, we can proceed
                self.handle_client_message(cid, request) if not request.is_auth else self.handle_authenticate(cid, request)

            # Unauthenticated - require credentials on input
            else:
                self.handle_authenticate(cid, request)

            logger.info('Response returned cid:`%s`, time:`%s`', cid, _now()-now)

        except Exception, e:
            logger.warn(format_exc(e))

    def received_message(self, message):
        logger.info('Received message %r', message.data)
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

    def invoke_client(self, cid, request, use_send=True):
        msg = ClientInvokeRequest(cid, request)
        (self.send if use_send else self.ping)(msg.serialize())

        response = self._wait_for_client_response(msg.id)
        if response:
            return response if isinstance(response, bool) else response.data # It will be bool in pong responses

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
        logger.info('Closing connection from %s (%s) to %s (%s %s %s)',
            self._peer_address, self._peer_fqdn, self._local_address, self.ext_client_id, self.config.name, self.pub_client_id)

        if self.config.needs_auth:
            self.unregister_auth_client()
        del self.container.clients[self.pub_client_id]

# ################################################################################################################################

    def ponged(self, msg, _loads=loads, _action=WEB_SOCKET.ACTION.CLIENT_RESPONSE):

        # Pretend it's an actual response from the client,
        # we cannot use in_reply_to because pong messages are 1:1 copies of ping ones.
        # TODO: Use lxml for XML eventually but for now we are always using JSON
        self.responses_received[_loads(msg.data)['meta']['id']] = True

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
        self.is_connected = True
        self.server.serve_forever()

    def _stop(self):
        self.server.stop(3)

    def get_log_details(self):
        return self.config.address

    def invoke(self, cid, pub_client_id, request):
        return self.server.invoke_client(cid, pub_client_id, request)

# ################################################################################################################################

