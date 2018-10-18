# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from copy import deepcopy
from datetime import datetime, timedelta
from errno import EADDRINUSE
from httplib import BAD_REQUEST, INTERNAL_SERVER_ERROR, NOT_FOUND, responses
from logging import getLogger
from socket import error as SocketError
from traceback import format_exc
from urlparse import urlparse

# Bunch
from bunch import Bunch, bunchify

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
from zato.common import CHANNEL, DATA_FORMAT, ParsingException, PUBSUB, SEC_DEF_TYPE, WEB_SOCKET
from zato.common.exception import Reportable
from zato.common.pubsub import HandleNewMessageCtx
from zato.common.util import new_cid
from zato.common.util.hook import HookTool
from zato.server.connection.connector import Connector
from zato.server.connection.web_socket.msg import AuthenticateResponse, ClientInvokeRequest, ClientMessage, copy_forbidden, \
     error_response, ErrorResponse, Forbidden, OKResponse, PubSubClientInvokeRequest
from zato.server.pubsub.task import PubSubTool
from zato.vault.client import VAULT

# ################################################################################################################################

logger = getLogger('zato_web_socket')
logger_zato = getLogger('zato')

# ################################################################################################################################

http404 = b'{} {}'.format(NOT_FOUND, responses[NOT_FOUND])

# ################################################################################################################################

_wsgi_drop_keys = ('ws4py.socket', 'wsgi.errors', 'wsgi.input')

# ################################################################################################################################

VAULT_TOKEN_HEADER=VAULT.HEADERS.TOKEN_RESPONSE

# ################################################################################################################################

hook_type_to_method = {
    WEB_SOCKET.HOOK_TYPE.ON_CONNECTED: 'on_connected',
    WEB_SOCKET.HOOK_TYPE.ON_DISCONNECTED: 'on_disconnected',
}

# ################################################################################################################################

class HookCtx(object):
    __slots__ = ('hook_type', 'config', 'pub_client_id', 'ext_client_id', 'ext_client_name', 'connection_time', 'user_data',
        'forwarded_for', 'forwarded_for_fqdn', 'peer_address', 'peer_host', 'peer_fqdn', 'peer_conn_info_pretty')

    def __init__(self, hook_type, **kwargs):
        self.hook_type = hook_type
        for name in self.__slots__:
            if name != 'hook_type':
                setattr(self, name, kwargs[name])

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
    def __init__(self, container, config, _unusued_sock, _unusued_protocols, _unusued_extensions, wsgi_environ, **kwargs):
        super(WebSocket, self).__init__(_unusued_sock, _unusued_protocols, _unusued_extensions, wsgi_environ, **kwargs)
        self.container = container
        self.config = config
        self.initial_http_wsgi_environ = wsgi_environ
        self.has_session_opened = False
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
        self.user_data = Bunch() # Arbitrary user-defined data
        self._disconnect_requested = False # Have we been asked to disconnect this client?

        # Manages access to service hooks
        if self.config.hook_service:

            self.hook_tool = HookTool(self.config.parallel_server, HookCtx, hook_type_to_method, self.invoke_service)

            self.config.on_connected_service_invoker = self.hook_tool.get_hook_service_invoker(
                config.hook_service, WEB_SOCKET.HOOK_TYPE.ON_CONNECTED)

            self.config.on_disconnected_service_invoker = self.hook_tool.get_hook_service_invoker(
                config.hook_service, WEB_SOCKET.HOOK_TYPE.ON_DISCONNECTED)

        else:
            self.hook_tool = None

        # For publish/subscribe over WSX
        self.pubsub_tool = PubSubTool(self.config.parallel_server.worker_store.pubsub, self,
            PUBSUB.ENDPOINT_TYPE.WEB_SOCKETS.id, self.deliver_pubsub_msg)

        # Active WebSocket client ID (WebSocketClient model, web_socket_client.id in SQL)
        self.sql_ws_client_id = None

        # For tokens assigned externally independent of our WS-level self.token.
        # Such tokens will be generated by Vault, for instance.
        self.ext_token = None

        # Drop WSGI keys pointing to complex Python objects such as sockets
        for name in _wsgi_drop_keys:
            self.initial_http_wsgi_environ.pop(name, None)

        # Responses to previously sent requests - keyed by request IDs
        self.responses_received = {}

        _local_address = self.sock.getsockname()
        self._local_address = '{}:{}'.format(_local_address[0], _local_address[1])

        _peer_address = self.sock.getpeername()
        self._peer_address = '{}:{}'.format(_peer_address[0], _peer_address[1])

        self.forwarded_for = self.initial_http_wsgi_environ.get('HTTP_X_FORWARDED_FOR')

        if self.forwarded_for:
            self.forwarded_for_fqdn = socket.getfqdn(self.forwarded_for)
        else:
            self.forwarded_for_fqdn = '(Unknown)'

        _peer_fqdn = '(Unknown)'

        try:
            self._peer_host = socket.gethostbyaddr(_peer_address[0])[0]
            _peer_fqdn = socket.getfqdn(self._peer_host)
        except Exception, e:
            logger.warn(format_exc(e))
        finally:
            self._peer_fqdn = _peer_fqdn

        self.peer_conn_info_pretty = self.get_peer_info_pretty()

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

    def deliver_pubsub_msg(self, sub_key, msg):
        """ Delivers one or more pub/sub messages to the connected WSX client.
        """
        # A list of messages is given on input so we need to serialize each of them individually
        if isinstance(msg, list):
            len_msg = len(msg)
            data = []
            for elem in msg:
                data.append(elem.serialized if elem.serialized else elem.to_external_dict())

        # A single message was given on input
        else:
            len_msg = 1
            data = msg.serialized if msg.serialized else msg.to_external_dict()

        cid = new_cid()
        logger.info('Delivering %d pub/sub message{} to sub_key `%s`'.format('s' if len_msg > 1 else ''), len_msg, sub_key)

        self.invoke_client(cid, data, _Class=PubSubClientInvokeRequest)

# ################################################################################################################################

    def add_sub_key(self, sub_key):
        self.pubsub_tool.add_sub_key(sub_key)

# ################################################################################################################################

    def remove_sub_key(self, sub_key):
        self.pubsub_tool.remove_sub_key(sub_key)

# ################################################################################################################################

    def add_pubsub_message(self, sub_key, message):
        self.pubsub_tool.add_message(sub_key, message)

# ################################################################################################################################

    def get_peer_info_pretty(self):
        return 'name:`{}` id:`{}` fwd_for:`{}` peer:`{}` pub:`{}`'.format(
            self.ext_client_name, self.ext_client_id, self.forwarded_for_fqdn, self._peer_fqdn, self.pub_client_id)

# ################################################################################################################################

    def get_on_connected_hook(self):
        """ Returns a hook triggered when a new connection was made.
        """
        if self.hook_tool:
            return self.config.on_connected_service_invoker

# ################################################################################################################################

    def get_on_disconnected_hook(self):
        """ Returns a hook triggered when an existing connection was dropped.
        """
        if self.hook_tool:
            return self.config.on_disconnected_service_invoker

# ################################################################################################################################

    def parse_json(self, data, _create_session=WEB_SOCKET.ACTION.CREATE_SESSION, _response=WEB_SOCKET.ACTION.CLIENT_RESPONSE):

        parsed = loads(data)
        msg = ClientMessage()

        meta = parsed.get('meta', {})

        if meta:
            meta = bunchify(meta)

            msg.action = meta.get('action', _response)
            msg.id = meta.id
            msg.timestamp = meta.timestamp
            msg.token = meta.get('token') # Optional because it won't exist during first authentication

            # self.ext_client_id and self.ext_client_name will exist after create-session action
            # so we use them if they are available but fall back to meta.client_id and meta.client_name during
            # the very create-session action.
            if meta.get('client_id'):
                self.ext_client_id = meta.client_id

            if meta.get('client_name'):
                self.ext_client_name = meta.client_name

            msg.ext_client_id = self.ext_client_id
            msg.ext_client_name = self.ext_client_name

            if msg.action == _create_session:
                msg.username = meta.get('username')

                # Secret is optional because WS channels may be without credentials attached
                msg.secret = meta.secret if self.config.needs_auth else ''

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

    def create_session(self, cid, request, _sec_def_type_vault=SEC_DEF_TYPE.VAULT, _VAULT_TOKEN_HEADER=VAULT_TOKEN_HEADER):
        """ Creates a new session in the channel's auth backend and assigned metadata based on the backend's response.
        """
        # This dictionary will be written to
        headers = {}

        if not self.config.needs_auth:
            can_create_session = True
        else:
            can_create_session = self.config.auth_func(
                request.cid, self.sec_type, {'username':request.username, 'secret':request.secret}, self.config.sec_name,
                self.config.vault_conn_default_auth_method, self.initial_http_wsgi_environ, headers)

        if can_create_session:

            with self.update_lock:

                # If we are using Vault, use its own header
                if self.config.sec_type == _sec_def_type_vault:
                    self.ext_token = headers['zato.http.response.headers'][_VAULT_TOKEN_HEADER]
                    self_token = self.ext_token

                # Otherwise, generate our own
                else:
                    self_token = new_cid()

                self.token = 'ws.token.{}'.format(self_token)

                self.has_session_opened = True
                self.ext_client_id = request.ext_client_id
                self.ext_client_name = request.ext_client_name

                # Update peer name pretty now that we have more details about it
                self.peer_conn_info_pretty = self.get_peer_info_pretty()

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
                    try:
                        response = self.invoke_client(new_cid(), None, use_send=False)
                    except RuntimeError:
                        logger.warn('Closing connection due to `%s`', format_exc())
                        self.on_socket_terminated()

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

    def _get_hook_request(self):
        out = {
            'peer_address': self._peer_address,
            'peer_host': self._peer_host,
            'peer_fqdn': self._peer_fqdn,
        }

        for name in HookCtx.__slots__:
            if name not in('hook_type', 'peer_address', 'peer_host', 'peer_fqdn'):
                out[name] = getattr(self, name)

        return out

# ################################################################################################################################

    def register_auth_client(self):
        """ Registers peer in ODB and sets up background pings to keep its connection alive.
        Called only if authentication succeeded.
        """
        self.sql_ws_client_id = self.invoke_service('zato.channel.web-socket.client.create', {
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
        }, needs_response=True).ws_client_id

        spawn(self.send_background_pings)

        # Run the relevant on_connected hook, if any is available
        hook = self.get_on_connected_hook()
        if hook:
            hook(**self._get_hook_request())

# ################################################################################################################################

    def unregister_auth_client(self):
        """ Unregisters an already registered peer in ODB.
        """
        if self.has_session_opened:

            # Deletes state from SQL
            self.invoke_service('zato.channel.web-socket.client.delete-by-pub-id', {
                'pub_client_id': self.pub_client_id,
            })

            if self.pubsub_tool.sub_keys:

                # Deletes across all workers the in-RAM pub/sub state about the client that is disconnecting
                self.invoke_service('zato.channel.web-socket.client.unregister-ws-sub-key', {
                    'sub_key_list': list(self.pubsub_tool.sub_keys),
                })

                # Clears out our own delivery tasks
                self.pubsub_tool.remove_all_sub_keys()

        # Run the relevant on_connected hook, if any is available (even if the session was never opened)
        hook = self.get_on_disconnected_hook()
        if hook:
            hook(**self._get_hook_request())

# ################################################################################################################################

    def handle_create_session(self, cid, request):
        if request.is_auth:
            response = self.create_session(cid, request)
            if response:
                self.register_auth_client()
                self.send(response)
                logger.info(
                    'Client %s (%s %s) logged in successfully to %s (%s)', self._peer_address, self._peer_fqdn,
                    self.pub_client_id, self._local_address, self.config.name)
            else:
                self.on_forbidden('sent invalid credentials')
        else:
            self.on_forbidden('is not authenticated')

# ################################################################################################################################

    def invoke_service(self, service_name, data, cid=None, needs_response=True, _channel=CHANNEL.WEB_SOCKET,
            _data_format=DATA_FORMAT.DICT, serialize=False):

        return self.config.on_message_callback({
            'cid': cid or new_cid(),
            'data_format': _data_format,
            'service': service_name,
            'payload': data,
            'environ': {
                'web_socket': self,
                'sql_ws_client_id': self.sql_ws_client_id,
                'ws_channel_config': self.config,
                'ws_token': self.token,
                'ext_token': self.ext_token,
                'pub_client_id': self.pub_client_id,
                'ext_client_id': self.ext_client_id,
                'ext_client_name': self.ext_client_name,
                'peer_conn_info_pretty': self.peer_conn_info_pretty,
                'connection_time': self.connection_time,
                'pings_missed': self.pings_missed,
                'pings_missed_threshold': self.pings_missed_threshold,
                'peer_host': self._peer_host,
                'peer_fqdn': self._peer_fqdn,
                'forwarded_for': self.forwarded_for,
                'forwarded_for_fqdn': self.forwarded_for_fqdn,
                'initial_http_wsgi_environ': self.initial_http_wsgi_environ,
            },
        }, CHANNEL.WEB_SOCKET, None, needs_response=needs_response, serialize=serialize)

# ################################################################################################################################

    def handle_client_message(self, cid, msg, _action=WEB_SOCKET.ACTION):
        self._handle_client_response(cid, msg) if msg.action == _action.CLIENT_RESPONSE else self._handle_invoke_service(cid, msg)

# ################################################################################################################################

    def _handle_invoke_service(self, cid, msg):

        try:
            service_response = self.invoke_service(self.config.service_name, msg.data, cid=cid)
        except Exception as e:

            logger.warn('Service `%s` could not be invoked, id:`%s` cid:`%s`, e:`%s`',
                self.config.service_name, msg.id, cid, format_exc())

            # Errors known to map to HTTP ones
            if isinstance(e, Reportable):
                status = e.status
                error_message = e.msg

            # Catch SimpleIO-related errors, i.e. missing input parameters
            elif isinstance(e, ParsingException):
                status = BAD_REQUEST
                error_message = 'I/O processing error'

            # Anything else
            else:
                status = INTERNAL_SERVER_ERROR
                error_message = 'Could not invoke service `{}`, id:`{}`, cid:`{}`'.format(self.config.service_name, msg.id, cid)

            response = ErrorResponse(cid, msg.id, status, error_message)

        else:
            response = OKResponse(cid, msg.id, service_response)

        serialized = response.serialize()

        logger.info('Sending response %s', serialized)

        try:
            self.send(serialized)
        except AttributeError as e:
            if e.message == "'NoneType' object has no attribute 'text_message'":
                _msg = 'Service response discarded (client disconnected), cid:`%s`, msg.meta:`%s`'
                _meta = msg.get_meta()
                logger.warn(_msg, _meta)
                logger_zato.warn(_msg, _meta)

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

    def _wait_for_client_response(self, request_id, wait_time=5):
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

            if self.has_session_opened:

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
                try:
                    self.handle_client_message(cid, request) if not request.is_auth else self.handle_create_session(cid, request)
                except RuntimeError as e:
                    if e.message == 'Cannot send on a terminated websocket':
                        msg = 'Ignoring message (client disconnected), cid:`%s`, request:`%s`'
                        logger.info(msg, cid, request)
                        logger_zato.info(msg, cid, request)
                    else:
                        raise

            # Unauthenticated - require credentials on input
            else:
                self.handle_create_session(cid, request)

            logger.info('Response returned cid:`%s`, time:`%s`', cid, _now()-now)

        except Exception, e:
            logger.warn(format_exc(e))

# ################################################################################################################################

    def received_message(self, message):
        logger.info('Received message %r', message.data)
        try:
            spawn(self._received_message, deepcopy(message.data))
        except Exception, e:
            logger.warn(format_exc(e))

# ################################################################################################################################

    def notify_pubsub_message(self, cid, request):
        """ Invoked by internal services each time a pub/sub message is available for at least one of sub_keys
        this WSX client is responsible for.
        """
        self.pubsub_tool.handle_new_messages(HandleNewMessageCtx(cid, request['has_gd'], request['sub_key_list'],
            request['non_gd_msg_list'], request['is_bg_call'], request['pub_time_max']))

# ################################################################################################################################

    def run(self):
        try:
            super(WebSocket, self).run()
        except Exception:
            logger.warn('Exception in WebSocket.run `%s`', format_exc())

# ################################################################################################################################

    def _ensure_session_created(self, _now=datetime.utcnow):
        """ Runs in its own greenlet and waits for an authentication request to arrive by self.create_session_by,
        which is a timestamp object. If self.has_session_opened is not True by that time, connection to the remote end
        is closed.
        """
        if self._wait_for_event(self.config.new_token_wait_time, lambda: self.has_session_opened):
            return

        # We get here if self.has_session_opened has not been set to True by self.create_session_by
        self.on_forbidden('did not create session within {}s'.format(self.config.new_token_wait_time))

# ################################################################################################################################

    def invoke_client(self, cid, request, timeout=5, use_send=True, _Class=ClientInvokeRequest):
        """ Invokes a remote WSX client with request given on input, returning its response,
        if any was produced in the expected time.
        """
        # If input request is a string, try to decode it from JSON, but leave as-is in case
        # of an error or if it is not a string.
        if isinstance(request, basestring):
            try:
                request = loads(request)
            except ValueError:
                pass

        msg = _Class(cid, request)
        serialized = msg.serialize()
        (self.send if use_send else self.ping)(serialized)

        if _Class is not PubSubClientInvokeRequest:
            logger_zato.info('Sending msg `%s`', serialized)
            response = self._wait_for_client_response(msg.id, timeout)
            if response:
                return response if isinstance(response, bool) else response.data # It will be bool in pong responses

# ################################################################################################################################

    def _close_connection(self, verb, *_ignored_args, **_ignored_kwargs):
        logger.info('{} %s (%s) to %s (%s %s %s%s'.format(verb),
            self._peer_address, self._peer_fqdn, self._local_address, self.config.name, self.ext_client_id,
            self.pub_client_id, ' {})'.format(self.ext_client_name) if self.ext_client_name else ')')

        self.unregister_auth_client()
        del self.container.clients[self.pub_client_id]

# ################################################################################################################################

    def disconnect_client(self, cid):
        """ Disconnects the remote client, cleaning up internal resources along the way.
        """
        self._disconnect_requested = True
        self._close_connection('Disconnecting client from')
        self.close()

# ################################################################################################################################

    def opened(self, _now=datetime.utcnow, _timedelta=timedelta):
        logger.info('New connection from %s (%s) to %s (%s)', self._peer_address, self._peer_fqdn,
            self._local_address, self.config.name)

        spawn(self._ensure_session_created)

# ################################################################################################################################

    def closed(self, _ignored_code=None, _ignored_reason=None):

        # The diconnect requested already cleaned up everything
        if not self._disconnect_requested:
            self._close_connection('Closing connection from')

    on_socket_terminated = closed

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

        try:
            if environ['PATH_INFO'] != self.config.path:
                start_response(http404, {})
                return [error_response[NOT_FOUND][self.config.data_format]]

            super(WebSocketContainer, self).__call__(environ, start_response)
        except Exception:
            logger.warn('Could not execute __call__, e:`%s`', format_exc())

    def invoke_client(self, cid, pub_client_id, request, timeout):
        return self.clients[pub_client_id].invoke_client(cid, request, timeout)

    def disconnect_client(self, cid, pub_client_id):
        return self.clients[pub_client_id].disconnect_client(cid)

    def notify_pubsub_message(self, cid, pub_client_id, request):
        return self.clients[pub_client_id].notify_pubsub_message(cid, request)

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

    def invoke_client(self, cid, pub_client_id, request, timeout):
        return self.application.invoke_client(cid, pub_client_id, request, timeout)

    def disconnect_client(self, cid, pub_client_id):
        return self.application.disconnect_client(cid, pub_client_id)

    def notify_pubsub_message(self, cid, pub_client_id, request):
        return self.application.notify_pubsub_message(cid, pub_client_id, request)

# ################################################################################################################################

class ChannelWebSocket(Connector):
    """ A WebSocket channel connector to which external client applications connect.
    """
    start_in_greenlet = True

    def _start(self):
        self.server = WebSocketServer(self.config, self.auth_func, self.on_message_callback)
        self.is_connected = True
        try:
            self.server.serve_forever()
        except SocketError, e:
            if e.errno == EADDRINUSE:
                logger.info('Ignoring EADDRINUSE for %s %s', self.config.address, e)
            else:
                raise

    def _stop(self):
        self.server.stop(3)

    def get_log_details(self):
        return self.config.address

    def invoke(self, cid, pub_client_id, request, timeout=5):
        return self.server.invoke_client(cid, pub_client_id, request, timeout)

    def disconnect_client(self, cid, pub_client_id, *ignored_args, **ignored_kwargs):
        return self.server.disconnect_client(cid, pub_client_id)

    def notify_pubsub_message(self, cid, pub_client_id, request):
        return self.server.notify_pubsub_message(cid, pub_client_id, request)

# ################################################################################################################################
