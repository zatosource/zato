# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from datetime import datetime, timedelta
from http.client import BAD_REQUEST, INTERNAL_SERVER_ERROR, NOT_FOUND, responses
from logging import getLogger
from threading import current_thread
from traceback import format_exc

# Bunch
from bunch import Bunch, bunchify

# gevent
from gevent import sleep, socket, spawn
from gevent.lock import RLock

# ws4py
from ws4py.websocket import WebSocket as _WebSocket
from ws4py.server.geventserver import WSGIServer
from ws4py.server.wsgiutils import WebSocketWSGIApplication

# Python 2/3 compatibility
from future.moves.urllib.parse import urlparse
from past.builtins import basestring

# Zato
from zato.common.api import CHANNEL, DATA_FORMAT, PUBSUB, SEC_DEF_TYPE, WEB_SOCKET
from zato.common.exception import ParsingException, Reportable
from zato.common.json_internal import loads
from zato.common.pubsub import HandleNewMessageCtx, MSG_PREFIX, PubSubMessage
from zato.common.util.api import new_cid
from zato.common.util.hook import HookTool
from zato.common.util.wsx import cleanup_wsx_client
from zato.common.vault_ import VAULT
from zato.server.connection.connector import Connector
from zato.server.connection.web_socket.msg import AuthenticateResponse, InvokeClientRequest, ClientMessage, copy_forbidden, \
     error_response, ErrorResponse, Forbidden, OKResponse, InvokeClientPubSubRequest
from zato.server.pubsub.task import PubSubTool

# ################################################################################################################################

if 0:
    from zato.server.base.parallel import ParallelServer

    ParallelServer = ParallelServer

# ################################################################################################################################

logger = getLogger('zato_web_socket')
logger_zato = getLogger('zato')

# ################################################################################################################################

http404 = '{} {}'.format(NOT_FOUND, responses[NOT_FOUND])
http404_bytes = http404.encode('latin1')

# ################################################################################################################################

_wsgi_drop_keys = ('ws4py.socket', 'wsgi.errors', 'wsgi.input')

# ################################################################################################################################

class close_code:
    runtime_invoke_client = 3701
    runtime_background_ping = 3702
    unhandled_error = 3703

# ################################################################################################################################

VAULT_TOKEN_HEADER=VAULT.HEADERS.TOKEN_RESPONSE

# ################################################################################################################################

hook_type_to_method = {
    WEB_SOCKET.HOOK_TYPE.ON_CONNECTED: 'on_connected',
    WEB_SOCKET.HOOK_TYPE.ON_DISCONNECTED: 'on_disconnected',
    WEB_SOCKET.HOOK_TYPE.ON_PUBSUB_RESPONSE: 'on_pubsub_response',
    WEB_SOCKET.HOOK_TYPE.ON_VAULT_MOUNT_POINT_NEEDED: 'on_vault_mount_point_needed',
}

# ################################################################################################################################

_cannot_send = 'Cannot send on a terminated websocket'

# ################################################################################################################################

class HookCtx(object):
    __slots__ = ('hook_type', 'config', 'pub_client_id', 'ext_client_id', 'ext_client_name', 'connection_time', 'user_data',
        'forwarded_for', 'forwarded_for_fqdn', 'peer_address', 'peer_host', 'peer_fqdn', 'peer_conn_info_pretty', 'msg')

    def __init__(self, hook_type, *args, **kwargs):
        self.hook_type = hook_type
        for name in self.__slots__:
            if name != 'hook_type':
                setattr(self, name, kwargs.get(name))

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

        # The object containing this WebSocket
        self.container = container

        # Note: configuration object is shared by all WebSockets and any writes will be visible to all of them
        self.config = config

        # For later reference
        self.initial_http_wsgi_environ = wsgi_environ

        # Referred to soon enough so created here
        self.pub_client_id = 'ws.{}'.format(new_cid())

        # Zato parallel server this WebSocket runs on
        self.parallel_server = self.config.parallel_server # type: ParallelServer

        # JSON dumps function can be overridden by users
        self._json_dump_func = self._set_json_dump_func()

        super(WebSocket, self).__init__(_unusued_sock, _unusued_protocols, _unusued_extensions, wsgi_environ, **kwargs)

    def _set_json_dump_func(self, _default='rapidjson', _supported=('rapidjson', 'bson')):
        json_library = self.parallel_server.fs_server_config.wsx.get('json_library', _default)

        if json_library not in _supported:

            # Warn only if something was set by users
            if json_library:
                logger.warn('Unrecognized JSON library `%s` configured for WSX, not one of `%s`, switching to `%s`',
                    json_library, _supported, _default)

            json_library = _default

        if json_library == 'rapidjson':
            from rapidjson import dumps as dumps_func

        elif json_library == 'bson':
            from bson.json_util import dumps as dumps_func

        logger.info('Setting JSON dumps function based on `%s`', json_library)

        return dumps_func

    def _init(self):

        # Python-level ID contains all the core details, our own ID and that of the thread (greenlet) that creates us
        _current_thread = current_thread()
        python_id = '{}.{}.{}'.format(hex(id(self)), _current_thread.name, hex(_current_thread.ident))

        # Assign core attributes to this object before calling parent class
        self.python_id = python_id

        # Must be set here and then to True later on because our parent class may already want
        # to accept connections, and we need to postpone their processing until we are initialized fully.
        self._initialized = False

        self.has_session_opened = False
        self._token = None
        self.update_lock = RLock()
        self.ext_client_id = None
        self.ext_client_name = None
        self.connection_time = self.last_seen = datetime.utcnow()
        self.sec_type = self.config.sec_type
        self.pings_missed = 0
        self.pings_missed_threshold = self.config.get('pings_missed_threshold', 5)
        self.user_data = Bunch() # Arbitrary user-defined data
        self._disconnect_requested = False # Have we been asked to disconnect this client?

        # This will be populated by the on_vault_mount_point_needed hook
        self.vault_mount_point = None

        # Last the we received a ping response (pong) from our peer
        self.ping_last_response_time = None

        #
        # If the peer ever subscribes to a pub/sub topic we will periodically
        # store in the ODB information about the last time the peer either sent
        # or received anything from us. Note that we store it if:
        #
        # * The peer has at least one subscription, and
        # * At least self.pubsub_interact_interval seconds elapsed since the last update
        #
        # And:
        #
        # * The peer received a pub/sub message, or
        # * The peer sent a pub/sub message
        #
        # Or:
        #
        # * The peer did not send or receive anything, but
        # * The peer correctly responds to ping messages
        #
        # Such a logic ensures that we do not overwhelm the database with frequent updates
        # if the peer uses pub/sub heavily - it is costly to do it for each message.
        #
        # At the same time, if the peer does not receive or send anything but it is still connected
        # (because it responds to ping) we set its SQL status too.
        #
        # All of this lets background processes clean up WSX clients that subscribe at one
        # point but they are never seen again, which may (theoretically) happen if a peer disconnects
        # in a way that does not allow for Zato to clean up its subscription status in the ODB.
        #
        self.pubsub_interact_interval = WEB_SOCKET.DEFAULT.INTERACT_UPDATE_INTERVAL
        self.interact_last_updated = None
        self.last_interact_source = None
        self.interact_last_set = None

        # Manages access to service hooks
        if self.config.hook_service:

            self.hook_tool = HookTool(self.config.parallel_server, HookCtx, hook_type_to_method, self.invoke_service)

            self.on_connected_service_invoker = self.hook_tool.get_hook_service_invoker(
                self.config.hook_service, WEB_SOCKET.HOOK_TYPE.ON_CONNECTED)

            self.on_disconnected_service_invoker = self.hook_tool.get_hook_service_invoker(
                self.config.hook_service, WEB_SOCKET.HOOK_TYPE.ON_DISCONNECTED)

            self.on_pubsub_response_service_invoker = self.hook_tool.get_hook_service_invoker(
                self.config.hook_service, WEB_SOCKET.HOOK_TYPE.ON_PUBSUB_RESPONSE)

            self.on_vault_mount_point_needed = self.hook_tool.get_hook_service_invoker(
                self.config.hook_service, WEB_SOCKET.HOOK_TYPE.ON_VAULT_MOUNT_POINT_NEEDED)

        else:
            self.hook_tool = None
            self.on_connected_service_invoker = None
            self.on_disconnected_service_invoker = None
            self.on_pubsub_response_service_invoker = None
            self.on_vault_mount_point_needed = None

        # For publish/subscribe over WSX
        self.pubsub_tool = PubSubTool(self.config.parallel_server.worker_store.pubsub, self,
            PUBSUB.ENDPOINT_TYPE.WEB_SOCKETS.id, deliver_pubsub_msg=self.deliver_pubsub_msg)

        # Active WebSocket client ID (WebSocketClient model, web_socket_client.id in SQL)
        self._sql_ws_client_id = None

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
            self.forwarded_for_fqdn = WEB_SOCKET.DEFAULT.FQDN_UNKNOWN

        _peer_fqdn = WEB_SOCKET.DEFAULT.FQDN_UNKNOWN
        self._peer_host = _peer_fqdn

        try:
            self._peer_host = socket.gethostbyaddr(_peer_address[0])[0]
            _peer_fqdn = socket.getfqdn(self._peer_host)
        except Exception:
            logger.warn('WSX exception in FQDN lookup `%s`', format_exc())
        finally:
            self._peer_fqdn = _peer_fqdn

        self.peer_conn_info_pretty = self.get_peer_info_pretty()

        self._parse_func = {
            DATA_FORMAT.JSON: self.parse_json,
            DATA_FORMAT.XML: self.parse_xml,
        }[self.config.data_format]

        # All set, we can process connections now
        self._initialized = True

# ################################################################################################################################

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

    # This is a property so as to make it easier to add logging calls to observe what is getting and setting the value

    @property
    def sql_ws_client_id(self):
        return self._sql_ws_client_id

    @sql_ws_client_id.setter
    def sql_ws_client_id(self, value):
        self._sql_ws_client_id = value

# ################################################################################################################################

    def set_last_interaction_data(self, source, _now=datetime.utcnow, _interval=WEB_SOCKET.DEFAULT.INTERACT_UPDATE_INTERVAL):
        """ Updates metadata regarding pub/sub about this WSX connection.
        """
        with self.update_lock:

            # Local aliases
            now = _now()

            # Update last interaction metadata time for our peer
            self.last_interact_source = source

            # It is possible that we set the metadata the first time,
            # in which case we will always invoke the service, having first stored current timestamp for later use.
            if not self.interact_last_set:
                self.interact_last_set = now
                needs_services = True
            else:

                # We must have been already called before, in which case we execute services only if it is our time to do it.
                needs_services = True if self.interact_last_updated + timedelta(minutes=_interval) < now else False

            # Are we to invoke the services this time?
            if needs_services:

                pub_sub_request = {
                    'sub_key': self.pubsub_tool.get_sub_keys(),
                    'last_interaction_time': now,
                    'last_interaction_type': self.last_interact_source,
                    'last_interaction_details': self.get_peer_info_pretty(),
                }

                wsx_request = {
                    'id': self.sql_ws_client_id,
                    'last_seen': now,
                }

                logger.info('Setting pub/sub interaction metadata `%s`', pub_sub_request)
                self.invoke_service('zato.pubsub.subscription.update-interaction-metadata', pub_sub_request)

                logger.info('Setting WSX last seen `%s`', wsx_request)
                self.invoke_service('zato.channel.web-socket.client.set-last-seen', wsx_request)

                # Finally, store it for the future use
                self.interact_last_updated = now

# ################################################################################################################################

    def deliver_pubsub_msg(self, sub_key, msg):
        """ Delivers one or more pub/sub messages to the connected WSX client.
        """
        ctx = {}

        if isinstance(msg, PubSubMessage):
            len_msg = 1
        else:
            len_msg = len(msg)
            msg = msg[0] if len_msg == 1 else msg

        # A list of messages is given on input so we need to serialize each of them individually
        if isinstance(msg, list):
            cid = new_cid()
            data = []
            for elem in msg:
                data.append(elem.serialized if elem.serialized else elem.to_external_dict())
                if elem.reply_to_sk:
                    ctx_reply_to_sk = ctx.setdefault('', [])
                    ctx_reply_to_sk.append(elem.reply_to_sk)

        # A single message was given on input
        else:
            cid = msg.pub_msg_id
            data = msg.serialized if msg.serialized else msg.to_external_dict()
            if msg.reply_to_sk:
                ctx['reply_to_sk'] = msg.reply_to_sk

        logger.info('Delivering %d pub/sub message{} to sub_key `%s` (ctx:%s)'.format('s' if len_msg > 1 else ''),
            len_msg, sub_key, ctx)

        # Actually deliver messages
        self.invoke_client(cid, data, ctx=ctx, _Class=InvokeClientPubSubRequest)

        # We get here if there was no exception = we can update pub/sub metadata
        self.set_last_interaction_data('pubsub.deliver_pubsub_msg')

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

    def get_peer_info_dict(self):
        return {
            'name': self.ext_client_name,
            'ext_client_id': self.ext_client_id,
            'forwarded_for_fqdn': self.forwarded_for_fqdn,
            'peer_fqdn': self._peer_fqdn,
            'pub_client_id': self.pub_client_id,
            'python_id': self.python_id,
            'sock': str(getattr(self, 'sock', '')),
            'swc': self.sql_ws_client_id,
        }

# ################################################################################################################################

    def get_peer_info_pretty(self):
        return 'name:`{}` id:`{}` fwd_for:`{}` conn:`{}` pub:`{}`, py:`{}`, sock:`{}`, swc:`{}`'.format(
            self.ext_client_name, self.ext_client_id, self.forwarded_for_fqdn, self._peer_fqdn,
            self.pub_client_id, self.python_id, getattr(self, 'sock', ''), self.sql_ws_client_id)

# ################################################################################################################################

    def get_on_connected_hook(self):
        """ Returns a hook triggered when a new connection was made.
        """
        if self.hook_tool:
            return self.on_connected_service_invoker

# ################################################################################################################################

    def get_on_disconnected_hook(self):
        """ Returns a hook triggered when an existing connection was dropped.
        """
        if self.hook_tool:
            return self.on_disconnected_service_invoker

# ################################################################################################################################

    def get_on_pubsub_hook(self):
        """ Returns a hook triggered when a pub/sub response arrives from the connected client.
        """
        if self.hook_tool:
            return self.on_pubsub_response_service_invoker

# ################################################################################################################################

    def get_on_vault_mount_point_needed(self):
        """ Returns a hook triggered when a Vault moint point needed to check credentials is not known.
        """
        if self.hook_tool:
            return self.on_vault_mount_point_needed

# ################################################################################################################################

    def parse_json(self, data, _create_session=WEB_SOCKET.ACTION.CREATE_SESSION, _response=WEB_SOCKET.ACTION.CLIENT_RESPONSE):

        data = data.decode('utf8')
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

            ext_client_name = meta.get('client_name')
            if ext_client_name:
                if isinstance(ext_client_name, dict):
                    _ext_client_name = []
                    for key, value in sorted(ext_client_name.items()):
                        _ext_client_name.append('{}: {}'.format(key, value))
                    ext_client_name = '; '.join(_ext_client_name)

            msg.ext_client_name = ext_client_name
            msg.ext_client_id = self.ext_client_id

            if msg.action == _create_session:
                msg.username = meta.get('username')

                # Secret is optional because WS channels may be without credentials attached
                msg.secret = meta.secret if self.config.needs_auth else ''

                msg.is_auth = True
            else:
                msg.in_reply_to = meta.get('in_reply_to')
                msg.is_auth = False

                ctx = meta.get('ctx')
                if ctx:
                    msg.reply_to_sk = ctx.get('reply_to_sk')
                    msg.deliver_to_sk = ctx.get('deliver_to_sk')

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

            # Discover which Vault mount point credentials will be under, unless we know it already.
            if not self.vault_mount_point:
                hook = self.get_on_vault_mount_point_needed()
                if hook:
                    hook(**self._get_hook_request())

            headers['HTTP_X_ZATO_VAULT_MOUNT_POINT'] = self.vault_mount_point

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

                logger.info('Assigning wsx py:`%s` to `%s`', self.python_id, self.peer_conn_info_pretty)

            return AuthenticateResponse(self.token.value, request.cid, request.id).serialize(self._json_dump_func)

# ################################################################################################################################

    def on_forbidden(self, action, data=copy_forbidden):
        cid = new_cid()
        logger.warn(
            'Peer %s (%s) %s, closing its connection to %s (%s), cid:`%s` (%s)', self._peer_address, self._peer_fqdn, action,
            self._local_address, self.config.name, cid, self.peer_conn_info_pretty)

        # If the client is already known to have disconnected there is no point in sending a Forbidden message.
        if self.is_client_disconnected():
            self.update_terminated_status()
            return

        try:
            self.send(Forbidden(cid, data).serialize(self._json_dump_func))
        except AttributeError as e:
            # Catch a lower-level exception which may be raised in case the client
            # disconnected and we did not manage to send the Forbidden message.
            # In this situation, the lower level will raise an attribute error
            # with a specific message. Otherwise, we reraise the exception.
            if not e.args[0] == "'NoneType' object has no attribute 'text_message'":
                raise
        else:
            self.update_terminated_status()

# ################################################################################################################################

    def update_terminated_status(self):
        self.server_terminated = True
        self.client_terminated = True

# ################################################################################################################################

    def is_client_disconnected(self):
        return self.terminated or self.sock is None

# ################################################################################################################################

    def send_background_pings(self, ping_extend=30):

        logger.info('Starting WSX background pings for `%s`', self.peer_conn_info_pretty)

        try:
            while self.stream and (not self.server_terminated):

                # Sleep for N seconds before sending a ping but check if we are connected upfront because
                # we could have disconnected in between while and sleep calls.
                sleep(ping_extend)

                # Ok, still connected
                if self.stream and (not self.server_terminated):
                    try:
                        response = self.invoke_client(new_cid(), None, use_send=False)
                    except RuntimeError:
                        logger.warn('Closing connection due to `%s`', format_exc())
                        self.on_socket_terminated(close_code.runtime_background_ping, 'Background ping runtime error')

                    with self.update_lock:
                        if response:
                            self.pings_missed = 0
                            self.ping_last_response_time = datetime.utcnow()
                            self.token.extend(ping_extend)
                        else:
                            self.pings_missed += 1
                            if self.pings_missed < self.pings_missed_threshold:
                                logger.warn(
                                    'Peer %s (%s) missed %s/%s ping messages from %s (%s). Last response time: %s{} (%s)'.format(
                                        ' UTC' if self.ping_last_response_time else ''),

                                    self._peer_address,
                                    self._peer_fqdn,

                                    self.pings_missed,
                                    self.pings_missed_threshold,

                                    self._local_address,
                                    self.config.name,

                                    self.ping_last_response_time,
                                    self.peer_conn_info_pretty)
                            else:
                                self.on_forbidden('missed {}/{} ping messages'.format(
                                    self.pings_missed, self.pings_missed_threshold))

                # No stream or server already terminated = we can quit
                else:
                    logger.info('Stopping background pings for peer %s (%s), stream:`%s`, st:`%s`, m:%s/%s (%s)',
                        self._peer_address,
                        self._peer_fqdn,

                        self.stream,
                        self.server_terminated,

                        self.pings_missed,
                        self.pings_missed_threshold,

                        self.peer_conn_info_pretty)
                    return

        except Exception:
            logger.warn(format_exc())

# ################################################################################################################################

    def _get_hook_request(self):
        out = bunchify({
            'peer_address': self._peer_address,
            'peer_host': self._peer_host,
            'peer_fqdn': self._peer_fqdn,
        })

        for name in HookCtx.__slots__:
            if name not in('hook_type', 'peer_address', 'peer_host', 'peer_fqdn', 'msg'):
                out[name] = getattr(self, name)

        return out

# ################################################################################################################################

    def register_auth_client(self, _assigned_msg='Assigned sws_id:`%s` to `%s` (%s %s %s)'):
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
            'peer_forwarded_for': self.forwarded_for,
            'peer_forwarded_for_fqdn': self.forwarded_for_fqdn,
        }, needs_response=True).ws_client_id

        logger.info(
            _assigned_msg, self.sql_ws_client_id, self.python_id, self.pub_client_id, self.ext_client_id, self.ext_client_name)

        # Run the relevant on_connected hook, if any is available
        hook = self.get_on_connected_hook()

        if hook:
            hook(**self._get_hook_request())

        spawn(self.send_background_pings)

# ################################################################################################################################

    def unregister_auth_client(self):
        """ Unregisters an already registered peer in ODB.
        """
        hook = self.get_on_disconnected_hook()
        hook_request = self._get_hook_request() if hook else None

        # To clear out our own delivery tasks
        opaque_func_list = [self.pubsub_tool.remove_all_sub_keys]

        cleanup_wsx_client(self.has_session_opened, self.invoke_service, self.pub_client_id, list(self.pubsub_tool.sub_keys),
            self.get_on_disconnected_hook(), self.config.hook_service, hook_request, opaque_func_list)

# ################################################################################################################################

    def handle_create_session(self, cid, request):
        if request.is_auth:
            response = self.create_session(cid, request)
            if response:
                self.register_auth_client()
                self.send(response)
                logger.info(
                    'Client %s logged in successfully to %s (%s) (%s)', self.pub_client_id, self._local_address,
                    self.config.name, self.peer_conn_info_pretty)
            else:
                self.on_forbidden('sent invalid credentials')
        else:
            self.on_forbidden('is not authenticated')

# ################################################################################################################################

    def invoke_service(self, service_name, data, cid=None, needs_response=True, _channel=CHANNEL.WEB_SOCKET,
            _data_format=DATA_FORMAT.DICT, serialize=False):

        # It is possible that this method will be invoked before self.__init__ completes,
        # because self's parent manages the underlying TCP stream, in which can self
        # will not be fully initialized yet so we need to wait a bit until it is.
        while not self._initialized:
            sleep(0.1)

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

            logger.warn('Service `%s` could not be invoked, id:`%s` cid:`%s`, conn:`%s`, e:`%s`',
                self.config.service_name, msg.id, cid, self.peer_conn_info_pretty, format_exc())

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
                error_message = 'Internal server error'

            response = ErrorResponse(cid, msg.id, status, error_message)

        else:
            response = OKResponse(cid, msg.id, service_response)

        serialized = response.serialize(self._json_dump_func)

        logger.info('Sending response `%s` from to `%s` `%s` `%s` `%s` %s', serialized,
            self.python_id, self.pub_client_id, self.ext_client_id, self.ext_client_name, self.peer_conn_info_pretty)

        try:
            self.send(serialized)
        except AttributeError as e:
            if e.args[0] == "'NoneType' object has no attribute 'text_message'":
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

    def _handle_client_response(self, cid, msg, _msg_id_prefix=MSG_PREFIX.MSG_ID):
        """ Processes responses from WSX clients - either invokes callbacks for pub/sub responses
        or adds the message to the list of received ones because someone is waiting for it.
        """
        # Pub/sub response
        if msg.in_reply_to.startswith(_msg_id_prefix):
            hook = self.get_on_pubsub_hook()
            if not hook:
                log_msg = 'Ignoring pub/sub response, on_pubsub_response hook not implemented for `%s`, conn:`%s`, msg:`%s`'
                logger.warn(log_msg, self.config.name, self.peer_conn_info_pretty, msg)
                logger_zato.warn(log_msg, self.config.name, self.peer_conn_info_pretty, msg)
            else:
                request = self._get_hook_request()
                request['msg'] = msg
                hook(**request)

        # Regular synchronous response, simply enqueue it and someone else will take care of it
        else:
            self.responses_received[msg.in_reply_to] = msg

    def _has_client_response(self, request_id):
        return self.responses_received.get(request_id)

    def _wait_for_client_response(self, request_id, wait_time=5):
        """ Wait until a response from client arrives and return it or return None if there is no response up to wait_time.
        """
        return self._wait_for_event(wait_time, self._has_client_response, request_id=request_id)

# ################################################################################################################################

    def _received_message(self, data, _now=datetime.utcnow, _default_data='', *args, **kwargs):

        # This is one of methods that can be invoked before self.__init__ completes,
        # because self's parent manages the underlying TCP stream, in which can self
        # will not be fully initialized yet so we need to wait a bit until it is.
        while not self._initialized:
            sleep(0.1)

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

                if request.token != self.token.value:
                    self.on_forbidden('sent an invalid token (`{!r}` instead `{!r}`)'.format(request.token, self.token.value))
                    return

                # Reject request if token is provided but it already expired
                if _now() > self.token.expires_at:
                    self.on_forbidden('used an expired token')
                    return

                # Ok, we can proceed
                try:
                    self.handle_client_message(cid, request) if not request.is_auth else self.handle_create_session(cid, request)
                except RuntimeError as e:
                    if str(e) == _cannot_send:
                        msg = 'Ignoring message (socket terminated #1), cid:`%s`, request:`%s` conn:`%s`'
                        logger.info(msg, cid, request, self.peer_conn_info_pretty)
                        logger_zato.info(msg, cid, request, self.peer_conn_info_pretty)
                    else:
                        raise

            # Unauthenticated - require credentials on input
            else:
                self.handle_create_session(cid, request)

            logger.info('Response returned cid:`%s`, time:`%s`', cid, _now()-now)

        except Exception:
            logger.warn(format_exc())

# ################################################################################################################################

    def received_message(self, message):
        logger.info('Received message %r to `%s` from `%s` `%s` `%s` `%s`', message.data,
            self.python_id, self.pub_client_id, self.ext_client_id, self.ext_client_name, self.peer_conn_info_pretty)

        try:
            self._received_message(message.data)
        except Exception:
            logger.warn(format_exc())

# ################################################################################################################################

    def notify_pubsub_message(self, cid, request):
        """ Invoked by internal services each time a pub/sub message is available for at least one of sub_keys
        this WSX client is responsible for.
        """
        self.pubsub_tool.handle_new_messages(HandleNewMessageCtx(cid, request['has_gd'], request['sub_key_list'],
            request['non_gd_msg_list'], request['is_bg_call'], request['pub_time_max']))

# ################################################################################################################################

    def subscribe_to_topic(self, cid, request):
        """ Subscribes current WebSocket a topic pointed to by input request object.
        """
        self.invoke_service('zato.pubsub.subscription.create-wsx-subscription-for-current', {
            'topic_name': request
        }, cid=cid)

# ################################################################################################################################

    def run(self):
        try:
            self._init()
            super(WebSocket, self).run()
        except Exception:
            logger.warn('Exception in WebSocket.run `%s`', format_exc())

# ################################################################################################################################

    def _ensure_session_created(self, _now=datetime.utcnow):
        """ Runs in its own greenlet and waits for an authentication request to arrive by self.create_session_by,
        which is a timestamp object. If self.has_session_opened is not True by that time, connection to the remote end
        is closed.
        """
        try:
            if self._wait_for_event(self.config.new_token_wait_time, lambda: self.has_session_opened):
                return

            # We get here if self.has_session_opened has not been set to True by self.create_session_by
            self.on_forbidden('did not create session within {}s (#1)'.format(self.config.new_token_wait_time))

        except Exception as e:
            if e.message == "'NoneType' object has no attribute 'text_message'":
                self.on_forbidden('did not create session within {}s (#2)'.format(self.config.new_token_wait_time))
            else:
                logger.warn('Exception in WSX _ensure_session_created `%s`', format_exc())

# ################################################################################################################################

    def invoke_client(self, cid, request, timeout=5, ctx=None, use_send=True, _Class=InvokeClientRequest, wait_for_response=True):
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

        # Serialize to string
        msg = _Class(cid, request, ctx)
        serialized = msg.serialize(self._json_dump_func)

        # Log what is about to be sent
        if use_send:
            logger.info('Sending message `%s` from `%s` to `%s` `%s` `%s` `%s`', serialized,
                self.python_id, self.pub_client_id, self.ext_client_id, self.ext_client_name, self.peer_conn_info_pretty)

        try:
            (self.send if use_send else self.ping)(serialized)
        except RuntimeError as e:
            if str(e) == _cannot_send:
                msg = 'Cannot send message (socket terminated #2), disconnecting client, cid:`%s`, msg:`%s` conn:`%s`'
                logger.info(msg, cid, serialized, self.peer_conn_info_pretty)
                logger_zato.info(msg, cid, serialized, self.peer_conn_info_pretty)
                self.disconnect_client(cid, close_code.runtime_invoke_client, 'Client invocation runtime error')
                raise Exception('WSX client disconnected cid:`{}, peer:`{}`'.format(cid, self.peer_conn_info_pretty))
            else:
                raise

        # Wait for response but only if it is not a pub/sub message,
        # these are always asynchronous and that channel's WSX hook
        # will process the response, if any arrives.
        if _Class is not InvokeClientPubSubRequest:
            if wait_for_response:
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

    def disconnect_client(self, cid=None, code=None, reason=None):
        """ Disconnects the remote client, cleaning up internal resources along the way.
        """
        self._disconnect_requested = True
        self._close_connection('cid:{}; c:{}; r:{}; Disconnecting client from')
        self.close(code, reason)

# ################################################################################################################################

    def opened(self):
        logger.info('New connection from %s (%s) to %s (%s %s %s)', self._peer_address, self._peer_fqdn,
            self._local_address, self.config.name, self.python_id, self.sock)

        spawn(self._ensure_session_created)

# ################################################################################################################################

    def closed(self, code=None, reason=None):

        # Our self.disconnect_client must have cleaned up everything already
        if not self._disconnect_requested:
            self._close_connection('c:{}; r:{}; Closing connection from'.format(code, reason))

    on_socket_terminated = closed

# ################################################################################################################################

    def ponged(self, msg, _loads=loads, _action=WEB_SOCKET.ACTION.CLIENT_RESPONSE):

        # Pretend it's an actual response from the client,
        # we cannot use in_reply_to because pong messages are 1:1 copies of ping ones.
        # TODO: Use lxml for XML eventually but for now we are always using JSON
        self.responses_received[_loads(msg.data.decode('utf8'))['meta']['id']] = True

        # Since we received a pong response, it means that the peer is connected,
        # in which case we update its pub/sub metadata.
        self.set_last_interaction_data('wsx.ponged')

# ################################################################################################################################

    def unhandled_error(self, e, _msg='Low-level exception caught, about to close connection from `%s`, e:`%s`'):
        """ Called by the underlying WSX library when a low-level TCP/OS exception occurs.
        """
        peer_info = self.get_peer_info_pretty()
        exc = format_exc()

        logger.info(_msg, peer_info, exc)
        logger_zato.info(_msg, peer_info, exc)

        self.disconnect_client('<unhandled-error>', close_code.runtime_background_ping, 'Unhandled error caught')

    def close(self, code=1000, reason='', _msg='Error while closing connection from `%s`, e:`%s`'):
        """ Re-implemented from the base class to be able to catch exceptions in self._write when closing connections.
        """
        if not self.server_terminated:
            self.server_terminated = True
            try:
                self._write(self.stream.close(code=code, reason=reason).single(mask=self.stream.always_mask))
            except Exception:

                peer_info = self.get_peer_info_pretty()
                exc = format_exc()

                logger.info(_msg, peer_info, exc)
                logger_zato.info(_msg, peer_info, exc)

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
        except Exception:
            logger.warn(format_exc())

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

    def broadcast(self, cid, request):
        for client in self.clients.values():
            spawn(client.invoke_client, cid, request, wait_for_response=False)

    def disconnect_client(self, cid, pub_client_id):
        return self.clients[pub_client_id].disconnect_client(cid)

    def notify_pubsub_message(self, cid, pub_client_id, request):
        return self.clients[pub_client_id].notify_pubsub_message(cid, request)

    def subscribe_to_topic(self, cid, pub_client_id, request):
        return self.clients[pub_client_id].subscribe_to_topic(cid, request)

    def get_client_by_pub_id(self, pub_client_id):
        return self.clients[pub_client_id]

# ################################################################################################################################
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

    def stop(self, *args, **kwargs):
        """ Reimplemented from the parent class to be able to call shutdown prior to its calling self.socket.close.
        """
        # self.socket will exist only if we have previously successfully
        # bound to an address. Otherwise, there will be no such attribute.
        if hasattr(self, 'socket'):
            self.socket.shutdown(2) # SHUT_RDWR has value of 2 in 'man 2 shutdown'
        super(WebSocketServer, self).stop(*args, **kwargs)

# ################################################################################################################################

    # These two methods are reimplemented from gevent.server to make it possible to use SO_REUSEPORT.

    @classmethod
    def get_listener(self, address, backlog=None, family=None):
        if backlog is None:
            backlog = self.backlog
        return WebSocketServer._make_socket(address, backlog=backlog, reuse_addr=self.reuse_addr, family=family)

    @staticmethod
    def _make_socket(address, backlog=50, reuse_addr=None, family=socket.AF_INET):
        sock = socket.socket(family=family)
        if reuse_addr is not None:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, reuse_addr)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        try:
            sock.bind(address)
        except socket.error as e:
            strerror = getattr(e, 'strerror', None)
            if strerror is not None:
                e.strerror = strerror + ': ' + repr(address)
            raise
        sock.listen(backlog)
        sock.setblocking(0)
        return sock

# ################################################################################################################################
# ################################################################################################################################

    def invoke_client(self, cid, pub_client_id, request, timeout):
        return self.application.invoke_client(cid, pub_client_id, request, timeout)

    def broadcast(self, cid, request):
        return self.application.broadcast(cid, request)

    def disconnect_client(self, cid, pub_client_id):
        return self.application.disconnect_client(cid, pub_client_id)

    def notify_pubsub_message(self, cid, pub_client_id, request):
        return self.application.notify_pubsub_message(cid, pub_client_id, request)

    def subscribe_to_topic(self, cid, pub_client_id, request):
        return self.application.subscribe_to_topic(cid, pub_client_id, request)

    def get_client_by_pub_id(self, pub_client_id):
        return self.application.get_client_by_pub_id(pub_client_id)

# ################################################################################################################################
# ################################################################################################################################

class ChannelWebSocket(Connector):
    """ A WebSocket channel connector to which external client applications connect.
    """
    start_in_greenlet = True

    def __init__(self, *args, **kwargs):
        self._wsx_server = None # type: WebSocketServer
        super(ChannelWebSocket, self).__init__(*args, **kwargs)

    def _start(self):
        self._wsx_server = WebSocketServer(self.config, self.auth_func, self.on_message_callback)
        self.is_connected = True
        self._wsx_server.start()

    def _stop(self):
        if self.is_connected:
            self._wsx_server.stop(3)
            self.is_connected = False

    def get_log_details(self):
        return self.config.address

    def invoke(self, cid, pub_client_id, request, timeout=5):
        return self._wsx_server.invoke_client(cid, pub_client_id, request, timeout)

    def broadcast(self, cid, request):
        return self._wsx_server.broadcast(cid, request)

    def disconnect_client(self, cid, pub_client_id, *ignored_args, **ignored_kwargs):
        return self._wsx_server.disconnect_client(cid, pub_client_id)

    def notify_pubsub_message(self, cid, pub_client_id, request):
        return self._wsx_server.notify_pubsub_message(cid, pub_client_id, request)

    def subscribe_to_topic(self, cid, pub_client_id, request):
        return self._wsx_server.subscribe_to_topic(cid, pub_client_id, request)

    def get_client_by_pub_id(self, pub_client_id):
        return self._wsx_server.get_client_by_pub_id(pub_client_id)

# ################################################################################################################################
# ################################################################################################################################
