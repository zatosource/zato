# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

class _UTF8Validator:
    """ A pass-through UTF-8 validator for ws4py - we do not need for this layer
    to validate UTF-8 bytes because we do it anyway during JSON parsing.
    """
    def validate(*ignored_args:'any_', **ignored_kwargs:'any_') -> 'any_':
        return True, True, None, None

    def reset(*ignored_args:'any_', **ignored_kwargs:'any_') -> 'any_':
        pass

from zato.server.ext.ws4py import streaming
streaming.Utf8Validator = _UTF8Validator

# ################################################################################################################################
# ################################################################################################################################

# stdlib
from datetime import datetime, timedelta
from http.client import BAD_REQUEST, FORBIDDEN, INTERNAL_SERVER_ERROR, NOT_FOUND, responses, UNPROCESSABLE_ENTITY
from json import loads as stdlib_loads
from logging import DEBUG, getLogger

from traceback import format_exc
from urllib.parse import urlparse

# Bunch
from bunch import Bunch, bunchify

# gevent
from gevent import sleep, socket, spawn
from gevent.lock import RLock
from gevent.pywsgi import WSGIServer as _Gevent_WSGIServer

# ws4py
from zato.server.ext.ws4py.exc import HandshakeError
from zato.server.ext.ws4py.websocket import WebSocket as _WebSocket
from zato.server.ext.ws4py.server.geventserver import GEventWebSocketPool, WebSocketWSGIHandler
from zato.server.ext.ws4py.server.wsgiutils import WebSocketWSGIApplication

# Zato
from zato.common.api import CHANNEL, DATA_FORMAT, PUBSUB, SEC_DEF_TYPE, WEB_SOCKET
from zato.common.audit_log import DataReceived, DataSent
from zato.common.exception import ParsingException, Reportable, RuntimeInvocationError
from zato.common.pubsub import HandleNewMessageCtx, MSG_PREFIX, PubSubMessage
from zato.common.typing_ import cast_
from zato.common.util.api import new_cid, parse_extra_into_dict
from zato.common.util.hook import HookTool
from zato.common.util.json_ import JSONParser
from zato.common.util.python_ import get_python_id
from zato.common.util.wsx import cleanup_wsx_client, ContextHandler
from zato.common.vault_ import VAULT
from zato.server.connection.connector import Connector
from zato.server.connection.web_socket.msg import AuthenticateResponse, InvokeClientRequest, ClientMessage, copy_forbidden, \
     error_response, ErrorResponse, Forbidden, OKResponse, InvokeClientPubSubRequest
from zato.server.pubsub.delivery.tool import PubSubTool

# ################################################################################################################################

if 0:
    from gevent._socketcommon import SocketMixin
    from zato.common.audit_log import DataEvent
    from zato.common.model.wsx import WSXConnectorConfig
    from zato.common.typing_ import any_, anydict, anylist, boolnone, callable_, callnone, intnone, optional, stranydict, strset
    from zato.server.base.parallel import ParallelServer

    DataEvent = DataEvent
    ParallelServer = ParallelServer
    WSXConnectorConfig = WSXConnectorConfig

# ################################################################################################################################

logger = getLogger('zato_web_socket')
logger_has_debug = logger.isEnabledFor(DEBUG)

logger_zato = getLogger('zato')
logger_zato_has_debug = logger_zato.isEnabledFor(DEBUG)

# ################################################################################################################################

_supported_json_dumps = {'stdlib', 'zato_default', 'rapidjson', 'bson', 'orjson'}

_now=datetime.utcnow
_timedelta=timedelta

# ################################################################################################################################

http400 = '{} {}'.format(BAD_REQUEST, responses[BAD_REQUEST])
http400_bytes = http400.encode('latin1')

http403 = '{} {}'.format(FORBIDDEN, responses[FORBIDDEN])
http403_bytes = http403.encode('latin1')

http404 = '{} {}'.format(NOT_FOUND, responses[NOT_FOUND])
http404_bytes = http404.encode('latin1')

# ################################################################################################################################

_wsgi_drop_keys = ('ws4py.socket', 'wsgi.errors', 'wsgi.input')

# ################################################################################################################################

code_invalid_utf8 = 4001
code_pings_missed = 4002

# ################################################################################################################################

_missing = object()

# ################################################################################################################################

# Maps WSGI keys to our own
new_conn_map_config = {
    'REMOTE_ADDR': 'remote_addr',
    'HTTP_X_FORWARDED_FOR': 'forwarded_for',
    'PATH_INFO': 'path_info',
    'REMOTE_PORT': 'remote_port',
    'HTTP_USER_AGENT': 'user_agent',
    'SERVER_NAME': 'server_name',
    'SERVER_PORT': 'server_port',
    'REQUEST_METHOD': 'http_method',
}

new_conn_pattern = ('{remote_addr}:{remote_port} -> {channel_name} -> fwd:{forwarded_for} -> ' \
    '{server_name}:{server_port}{path_info} -> ({user_agent} - {http_method})')

# ################################################################################################################################

class close_code:
    runtime_invoke_client = 3701
    runtime_background_ping = 3702
    unhandled_error = 3703
    runtime_error = 4003
    connection_error = 4003
    default_closed = 4004
    default_diconnect = 4005

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
_audit_msg_type = WEB_SOCKET.AUDIT_KEY

# ################################################################################################################################

log_msg_max_size = 8192
_interact_update_interval = WEB_SOCKET.DEFAULT.INTERACT_UPDATE_INTERVAL

# ################################################################################################################################

ExtraProperties = WEB_SOCKET.ExtraProperties
WebSocketAction = WEB_SOCKET.ACTION

# ################################################################################################################################

class HookCtx:
    __slots__ = (
        'hook_type', 'config', 'pub_client_id', 'ext_client_id', 'ext_client_name', 'connection_time', 'user_data',
        'forwarded_for', 'forwarded_for_fqdn', 'peer_address', 'peer_host', 'peer_fqdn', 'peer_conn_info_pretty', 'msg'
    )

    def __init__(self, hook_type:'str', *args:'any_', **kwargs:'any_') -> 'None':
        self.hook_type = hook_type
        for name in self.__slots__:
            if name != 'hook_type':
                setattr(self, name, kwargs.get(name))

# ################################################################################################################################

class TokenInfo:
    def __init__(self, value:'any_', ttl:'int'):
        self.value = value
        self.ttl = ttl
        self.creation_time = _now()
        self.expires_at = self.creation_time
        self.extend()

    def extend(self, extend_by:'intnone'=None):
        self.expires_at = self.expires_at + _timedelta(seconds=extend_by or self.ttl)

# ################################################################################################################################

class WebSocket(_WebSocket):
    """ Encapsulates information about an individual connection from a WebSocket client.
    """
    store_ctx: 'bool'
    ctx_file: 'ContextHandler'
    client_attrs: 'stranydict'

    def __init__(
        self,
        container:'any_',
        config:'WSXConnectorConfig',
        _unusued_sock:'any_',
        _unusued_protocols:'any_',
        _unusued_extensions:'any_',
        wsgi_environ:'anydict',
        **kwargs:'any_'
    ) -> 'None':

        # The object containing this WebSocket
        self.container = container

        # Note: configuration object is shared by all WebSockets and any writes will be visible to all of them
        self.config = config

        # This is needed for API completeness with non-Zato WSX clients
        self.url = self.config.address

        # For later reference
        self.initial_http_wsgi_environ = wsgi_environ

        # Referred to soon enough so created here
        self.pub_client_id = 'ws.{}'.format(new_cid())

        # A dictionary of attributes that each client can send across
        self.client_attrs = {}

        # Zato parallel server this WebSocket runs on
        self.parallel_server = cast_('ParallelServer', self.config.parallel_server)

        # JSON dumps function can be overridden by users
        self._json_dump_func = self._set_json_dump_func()

        # A reusable JSON parser
        self._json_parser = JSONParser()

        if config.extra_properties:
            self.extra_properties = stdlib_loads(config.extra_properties) # type: stranydict

            # Check if we should store runtime context for later use
            self.store_ctx = bool(self.extra_properties.get(ExtraProperties.StoreCtx))

        else:
            self.extra_properties = {}
            self.store_ctx = False

        # If yes, we can obtain a file object to write the context information with
        if self.store_ctx:
            self.ctx_handler = ContextHandler(ctx_container_name=self.config.name, is_read_only=False)

        super(WebSocket, self).__init__(
            self.parallel_server,
            _unusued_sock,
            _unusued_protocols,
            _unusued_extensions,
            wsgi_environ,
            **kwargs
        )

# ################################################################################################################################

    def _set_json_dump_func(
        self,
        _default:'str'='zato_default',
        _supported:'strset'=_supported_json_dumps
    ) -> 'callable_':

        json_library = self.parallel_server.fs_server_config.wsx.get('json_library', _default)

        if json_library not in _supported:

            # Warn only if something was set by users
            if json_library:
                logger.warning('Unrecognized JSON library `%s` configured for WSX, not one of `%s`, switching to `%s`',
                    json_library, _supported, _default)

            json_library = _default

        if json_library in ('orjson', 'zato_default'):
            from orjson import dumps as dumps_func

        elif json_library == 'rapidjson':
            from rapidjson import dumps as dumps_func # type: ignore

        elif json_library == 'bson':
            from bson.json_util import dumps as dumps_func

        else:
            from zato.common.json_ import dumps as dumps_func

        logger.info('Setting JSON dumps function based on `%s`', json_library)

        return dumps_func

# ################################################################################################################################

    def _init(self):

        # Assign core attributes to this object before calling parent class
        self.python_id = get_python_id(self)

        # Must be set here and then to True later on because our parent class may already want
        # to accept connections, and we need to postpone their processing until we are initialized fully.
        self._initialized = False

        pings_missed_threshold = getattr(self.config, 'pings_missed_threshold', None)
        pings_missed_threshold = pings_missed_threshold or WEB_SOCKET.DEFAULT.PINGS_MISSED_THRESHOLD

        ping_interval = getattr(self.config, 'ping_interval', None)
        ping_interval = ping_interval or WEB_SOCKET.DEFAULT.PING_INTERVAL

        self.has_session_opened = False
        self._token = None
        self.update_lock = RLock()
        self.ext_client_id = None
        self.ext_client_name = None
        self.connection_time = self.last_seen = datetime.utcnow()
        self.sec_type = self.config.sec_type
        self.pings_missed = 0
        self.pings_missed_threshold = pings_missed_threshold
        self.ping_interval = ping_interval
        self.user_data = Bunch() # Arbitrary user-defined data
        self._disconnect_requested = False # Have we been asked to disconnect this client?

        # Audit log configuration ..
        self.is_audit_log_sent_active     = getattr(self.config, 'is_audit_log_sent_active', False)
        self.is_audit_log_received_active = getattr(self.config, 'is_audit_log_received_active', False)

        # .. and audit log setup.
        self.parallel_server.set_up_object_audit_log_by_config(_audit_msg_type, self.pub_client_id, self.config, False)

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
        self.pubsub_interact_interval = _interact_update_interval
        self.interact_last_updated = None
        self.last_interact_source = None
        self.interact_last_set = None

        # Manages access to service hooks
        if self.config.hook_service:

            self.hook_tool = HookTool(self.config.parallel_server, HookCtx, hook_type_to_method, self.invoke_service)

            self.on_connected_service_invoker = self.hook_tool.get_hook_service_invoker(
                cast_('str', self.config.hook_service), WEB_SOCKET.HOOK_TYPE.ON_CONNECTED)

            self.on_disconnected_service_invoker = self.hook_tool.get_hook_service_invoker(
                cast_('str', self.config.hook_service), WEB_SOCKET.HOOK_TYPE.ON_DISCONNECTED)

            self.on_pubsub_response_service_invoker = self.hook_tool.get_hook_service_invoker(
                cast_('str', self.config.hook_service), WEB_SOCKET.HOOK_TYPE.ON_PUBSUB_RESPONSE)

            self.on_vault_mount_point_needed = self.hook_tool.get_hook_service_invoker(
                cast_('str', self.config.hook_service), WEB_SOCKET.HOOK_TYPE.ON_VAULT_MOUNT_POINT_NEEDED)

        else:
            self.hook_tool = None
            self.on_connected_service_invoker = None
            self.on_disconnected_service_invoker = None
            self.on_pubsub_response_service_invoker = None
            self.on_vault_mount_point_needed = None

        # For publish/subscribe over WSX
        self.pubsub_tool = PubSubTool(self.parallel_server.worker_store.pubsub, self,
            PUBSUB.ENDPOINT_TYPE.WEB_SOCKETS.id, deliver_pubsub_msg=self.deliver_pubsub_msg)

        # Active WebSocket client ID (WebSocketClient model, web_socket_client.id in SQL)
        self._sql_ws_client_id = -1

        # For tokens assigned externally independent of our WS-level self.token.
        # Such tokens will be generated by Vault, for instance.
        self.ext_token = ''

        # Drop WSGI keys pointing to complex Python objects such as sockets
        for name in _wsgi_drop_keys:
            _ = self.initial_http_wsgi_environ.pop(name, None)

        # Responses to previously sent requests - keyed by request IDs
        self.responses_received = {}

        _local_address = self.sock.getsockname() # type: ignore
        self._local_address = '{}:{}'.format(_local_address[0], _local_address[1])

        _peer_address = self.sock.getpeername() # type: ignore
        self._peer_address = '{}:{}'.format(_peer_address[0], _peer_address[1])

        self.forwarded_for = self.initial_http_wsgi_environ.get('HTTP_X_FORWARDED_FOR')

        if self.forwarded_for:
            self.forwarded_for_fqdn = socket.getfqdn(self.forwarded_for)
        else:
            self.forwarded_for_fqdn = WEB_SOCKET.DEFAULT.FQDN_UNKNOWN

        _peer_fqdn = WEB_SOCKET.DEFAULT.FQDN_UNKNOWN
        self._peer_host = _peer_fqdn

        try:
            get_host_by_addr_func = socket.gethostbyaddr # type: ignore
            self._peer_host = get_host_by_addr_func(_peer_address[0])[0]
            _peer_fqdn = socket.getfqdn(self._peer_host)
        except Exception as e:
            logger.info('WSX exception in FQDN lookup `%s` (%s)', e.args, _peer_address)
        finally:
            self._peer_fqdn = _peer_fqdn

        self.peer_conn_info_pretty = self.get_peer_info_pretty()

        # We always expect for input data to be JSON
        self._parse_func = self.parse_json

        # Store context details
        if self.store_ctx:
            self.ctx_handler.store(self)

        # All set, we can process connections now
        self._initialized = True

# ################################################################################################################################

    @property
    def token(self) -> 'TokenInfo':
        return cast_('TokenInfo', self._token)

    @token.setter
    def token(self, value:'any_') -> 'None':

        if not self._token:
            self._token = TokenInfo(value, self.config.token_ttl)
        else:
            self._token.value = value
            self._token.extend()

# ################################################################################################################################

    # This is a property so as to make it easier to add logging calls to observe what is getting and setting the value

    @property
    def sql_ws_client_id(self) -> 'int':
        return self._sql_ws_client_id

    @sql_ws_client_id.setter
    def sql_ws_client_id(self, value:'int') -> 'None':
        self._sql_ws_client_id = value

# ################################################################################################################################

    def set_last_interaction_data(
        self,
        source, # type: str
        _interval=_interact_update_interval # type: int
        ) -> 'None':
        """ Updates metadata regarding pub/sub about this WSX connection.
        """
        with self.update_lock:

            # Local aliases
            now = _now()

            # Update last interaction metadata time for our peer
            self.last_interact_source = source

            # It is possible that we are setting the metadata the first time here,
            # in which case we will always invoke the service,
            # having first stored current timestamp for later use.
            if not self.interact_last_set:
                self.interact_last_set = now
                needs_services = True
            else:

                # We must have been already called before, in which case we execute services only if it is our time to do it.
                needs_services = True if self.interact_last_updated + timedelta(minutes=_interval) < now else False # type: ignore

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

                if logger_has_debug:
                    logger.debug('Setting pub/sub interaction metadata `%s`', pub_sub_request)

                self.invoke_service('zato.pubsub.subscription.update-interaction-metadata', pub_sub_request)

                if logger_has_debug:
                    logger.debug('Setting WSX last seen `%s`', wsx_request)

                self.invoke_service('zato.channel.web-socket.client.set-last-seen', wsx_request)

                # Finally, store it for the future use
                self.interact_last_updated = now

# ################################################################################################################################

    def deliver_pubsub_msg(self, sub_key:'str', msg:'PubSubMessage | anylist') -> 'None':
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

    def add_sub_key(self, sub_key:'str') -> 'None':
        self.pubsub_tool.add_sub_key(sub_key)

# ################################################################################################################################

    def remove_sub_key(self, sub_key:'str') -> 'None':
        self.pubsub_tool.remove_sub_key(sub_key)

# ################################################################################################################################

    def get_peer_info_dict(self) -> 'stranydict':
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

    def get_peer_info_pretty(self) -> 'str':

        sock = getattr(self, 'sock', None)
        return 'name:`{}` id:`{}` fwd_for:`{}` conn:`{}` pub:`{}`, py:`{}`, sock:`{}`, swc:`{}`'.format(
            self.ext_client_name, self.ext_client_id, self.forwarded_for_fqdn, self._peer_fqdn,
            self.pub_client_id, self.python_id, sock, self.sql_ws_client_id)

# ################################################################################################################################

    def get_on_connected_hook(self) -> 'callnone':
        """ Returns a hook triggered when a new connection was made.
        """
        if self.hook_tool:
            return self.on_connected_service_invoker

# ################################################################################################################################

    def get_on_disconnected_hook(self) -> 'callnone':
        """ Returns a hook triggered when an existing connection was dropped.
        """
        if self.hook_tool:
            return self.on_disconnected_service_invoker

# ################################################################################################################################

    def get_on_pubsub_hook(self) -> 'callnone':
        """ Returns a hook triggered when a pub/sub response arrives from the connected client.
        """
        if self.hook_tool:
            return self.on_pubsub_response_service_invoker

# ################################################################################################################################

    def get_on_vault_mount_point_needed(self) -> 'callnone':
        """ Returns a hook triggered when a Vault moint point needed to check credentials is not known.
        """
        if self.hook_tool:
            return self.on_vault_mount_point_needed

# ################################################################################################################################

    def parse_json(
        self,
        data:'any_',
        cid:'str'='',
        _create_session:'str'=WEB_SOCKET.ACTION.CREATE_SESSION,
        _response:'str'=WEB_SOCKET.ACTION.CLIENT_RESPONSE,
        _code_invalid_utf8:'int'=code_invalid_utf8
    ) -> 'ClientMessage':
        """ Parses an incoming message into a Bunch object.
        """
        # Parse JSON into a dictionary
        parsed = self._json_parser.parse(data) # type: any_

        # Create a request message
        msg = ClientMessage()

        # Request metadata is optional
        meta = parsed.get('meta', {})

        if meta:
            msg.action = meta.get('action', _response)
            msg.id = meta['id']
            msg.timestamp = meta['timestamp']
            msg.token = meta.get('token') # Optional because it won't exist during first authentication

            if client_attrs := (meta.get('attrs') or {}):
                msg.client_attrs = parse_extra_into_dict(client_attrs)

            # self.ext_client_id and self.ext_client_name will exist after create-session action
            # so we use them if they are available but fall back to meta.client_id and meta.client_name during
            # the very create-session action.
            ext_client_id = meta.get('client_id')
            if ext_client_id:
                self.ext_client_id = meta.get('client_id')

            ext_client_name = meta.get('client_name', '')
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
                msg.secret = meta['secret'] if self.config.needs_auth else ''

                msg.is_auth = True
            else:
                msg.in_reply_to = meta.get('in_reply_to') or None
                msg.is_auth = False

                ctx = meta.get('ctx')
                if ctx:
                    msg.reply_to_sk = ctx.get('reply_to_sk')
                    msg.deliver_to_sk = ctx.get('deliver_to_sk')

        # Data is optional
        msg.data = parsed.get('data', {})

        return msg

# ################################################################################################################################

    def parse_xml(self, data:'any_') -> 'None':
        raise NotImplementedError('Not supported yet')

# ################################################################################################################################

    def create_session(
        self,
        cid:'str',
        request:'ClientMessage',
        _sec_def_type_vault:'str'=SEC_DEF_TYPE.VAULT,
        _VAULT_TOKEN_HEADER:'str'=VAULT_TOKEN_HEADER
    ) -> 'optional[AuthenticateResponse]':
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

            auth_func = cast_('callable_', self.config.auth_func)
            can_create_session = auth_func(
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

                self.token = 'zwsxt.{}'.format(self_token)

                self.has_session_opened = True
                self.ext_client_id = request.ext_client_id
                self.ext_client_name = request.ext_client_name

                # Update peer name pretty now that we have more details about it
                self.peer_conn_info_pretty = self.get_peer_info_pretty()

                logger.info('Assigning wsx py:`%s` to `%s` (%s %s)', self.python_id, self.pub_client_id,
                   self.ext_client_id, self.ext_client_name)

            _timestamp = _now()

            logger.info('Tok auth: [%s / %s] ts:%s exp:%s -> %s',
                self.token.value, self.pub_client_id, _timestamp, self.token.expires_at,
                _timestamp > self.token.expires_at)

            return AuthenticateResponse(self.token.value, request.cid, request.id).serialize(self._json_dump_func)

# ################################################################################################################################

    def on_forbidden(self, action:'str', data:'str'=copy_forbidden) -> 'None':
        cid = new_cid()
        logger.warning(
            'Peer %s (%s) %s, closing its connection to %s (%s), cid:`%s` (%s)', self._peer_address, self._peer_fqdn, action,
            self._local_address, self.config.name, cid, self.peer_conn_info_pretty)

        # If the client is already known to have disconnected there is no point in sending a Forbidden message.
        if self.is_client_disconnected():
            self.update_terminated_status()
            return

        try:
            msg = Forbidden(cid, data)
            serialized = msg.serialize(self._json_dump_func)
            self.send(serialized, cid)
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

    def update_terminated_status(self) -> 'None':
        self.server_terminated = True
        self.client_terminated = True

# ################################################################################################################################

    def is_client_disconnected(self) -> 'bool':
        return self.terminated or self.sock is None

    def is_client_connected(self) -> 'bool':
        return not self.is_client_disconnected()

# ################################################################################################################################

    def send_background_pings(self, ping_interval:'int') -> 'None':

        logger.info('Starting WSX background pings (%s:%s) for `%s`',
            ping_interval, self.pings_missed_threshold, self.peer_conn_info_pretty)

        try:
            while self.stream and (not self.server_terminated):

                # Sleep for N seconds before sending a ping but check if we are connected upfront because
                # we could have disconnected in between while and sleep calls.
                sleep(ping_interval)

                # Ok, still connected
                if self.stream and (not self.server_terminated):

                    # The response object will be None in case there is an exception
                    response = None

                    try:

                        _ts_before_invoke = _now()

                        if logger_has_debug:
                            logger.info('Tok ext0: [%s / %s] ts:%s exp:%s -> %s',
                                self.token.value, self.pub_client_id, _ts_before_invoke, self.token.expires_at,
                                _ts_before_invoke > self.token.expires_at)

                        response = self.invoke_client(new_cid(), None, use_send=False)

                    except ConnectionError as e:
                        logger.warning('ConnectionError; set keep_sending to False; closing connection -> `%s`', e.args)
                        self.disconnect_client(code=close_code.connection_error, reason='Background pingConnectionError')
                    except RuntimeError:
                        logger.warning('RuntimeError; set keep_sending to False; closing connection -> `%s`', format_exc())
                        self.disconnect_client(code=close_code.runtime_error, reason='Background ping RuntimeError')

                    with self.update_lock:
                        if response:

                            _timestamp = _now()

                            self.pings_missed = 0
                            self.ping_last_response_time = _timestamp

                            if logger_has_debug:
                                logger.info('Tok ext1: [%s / %s] ts:%s exp:%s -> %s',
                                    self.token.value, self.pub_client_id, _timestamp, self.token.expires_at,
                                    _timestamp > self.token.expires_at)

                            self.token.extend(ping_interval)

                            if logger_has_debug:
                                logger.info('Tok ext2: [%s / %s] ts:%s exp:%s -> %s',
                                    self.token.value, self.pub_client_id, _timestamp, self.token.expires_at,
                                    _timestamp > self.token.expires_at)

                        else:
                            self.pings_missed += 1
                            if self.pings_missed < self.pings_missed_threshold:
                                logger.info(
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
                                self.on_pings_missed()
                                return

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
            logger.warning(format_exc())

# ################################################################################################################################

    def _get_hook_request(self) -> 'Bunch':
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

    def on_pings_missed(self) -> 'None':
        logger.warning(
            'Peer %s (%s) missed %s/%s pings, forcing its connection to close (%s)',
            self._peer_address, self._peer_fqdn, self.pings_missed, self.pings_missed_threshold,
            self.peer_conn_info_pretty)

        self.disconnect_client(new_cid(), code_pings_missed, 'Pings missed')
        self.update_terminated_status()

# ################################################################################################################################

    def register_auth_client(self, _assigned_msg:'str'='Assigned sws_id:`%s` to `%s` (%s %s %s)') -> 'None':
        """ Registers peer in ODB and sets up background pings to keep its connection alive.
        Called only if authentication succeeded.
        """
        response = self.invoke_service('zato.channel.web-socket.client.create', {
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
        }, needs_response=True)

        self.sql_ws_client_id = response['ws_client_id']

        logger.info(
            _assigned_msg, self.sql_ws_client_id, self.python_id, self.pub_client_id, self.ext_client_id, self.ext_client_name)

        # Run the relevant on_connected hook, if any is available
        hook = self.get_on_connected_hook()

        if hook:
            hook(**self._get_hook_request())

        _ = spawn(self.send_background_pings, self.ping_interval)

# ################################################################################################################################

    def unregister_auth_client(self) -> 'None':
        """ Unregisters an already registered peer in ODB.
        """
        hook = self.get_on_disconnected_hook()
        hook_request = self._get_hook_request() if hook else None

        # To clear out our own delivery tasks
        opaque_func_list = [self.pubsub_tool.remove_all_sub_keys]

        cleanup_wsx_client(self.has_session_opened, self.invoke_service, self.pub_client_id, list(self.pubsub_tool.sub_keys),
            self.get_on_disconnected_hook(), self.config.hook_service, hook_request, opaque_func_list)

# ################################################################################################################################

    def handle_create_session(self, cid:'str', request:'ClientMessage') -> 'None':
        if request.is_auth:
            response = self.create_session(cid, request)
            if response:

                # Assign any potential attributes sent across by the client WebSocket
                self.client_attrs = request.client_attrs

                # Register the client for future use
                self.register_auth_client()

                # Send an auth response to the client
                self.send(response, cid)

                logger.info(
                    'Client %s logged in successfully to %s (%s) (%s %s)', self.pub_client_id, self._local_address,
                    self.config.name, self.ext_client_id, self.ext_client_name)
            else:
                self.on_forbidden('sent invalid credentials')
        else:
            self.on_forbidden('is not authenticated')

# ################################################################################################################################

    def invoke_service(
        self,
        service_name:'str',
        data:'any_',
        cid:'str'='',
        needs_response:'bool'=True,
        _channel:'str'=CHANNEL.WEB_SOCKET,
        _data_format:'str'=DATA_FORMAT.DICT,
        serialize:'bool'=False
    ) -> 'any_':

        # It is possible that this method will be invoked before self.__init__ completes,
        # because self's parent manages the underlying TCP stream, in which can self
        # will not be fully initialized yet so we need to wait a bit until it is.
        while not self._initialized:
            sleep(0.1)

        environ = {
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
        }

        msg = {
            'cid': cid or new_cid(),
            'data_format': _data_format,
            'service': service_name,
            'payload': data,
            'environ': environ,
            'wsx': self,
        }

        on_message_callback = cast_('callable_', self.config.on_message_callback)
        response = on_message_callback(
            msg,
            CHANNEL.WEB_SOCKET,
            None,
            needs_response=needs_response,
            serialize=serialize
        )

        return response

# ################################################################################################################################

    def handle_client_message(self, cid:'str', msg:'Bunch') -> 'None':
        func = self._handle_client_response if msg.action == WebSocketAction.CLIENT_RESPONSE else self._handle_invoke_service
        func(cid, msg)

# ################################################################################################################################

    def _handle_invoke_service(self, cid:'str', msg:'Bunch') -> 'None':

        try:
            service_response = self.invoke_service(cast_('str', self.config.service_name), msg.data, cid=cid)
        except Exception as e:

            # This goes to WSX logs, with a full traceback
            logger.warning('Service `%s` could not be invoked, id:`%s` cid:`%s`, conn:`%s`, e:`%s`',
                self.config.service_name, msg.id, cid, self.peer_conn_info_pretty, format_exc())

            # This goes to server.log and has only an error message
            logger_zato.warning('Service `%s` could not be invoked, id:`%s` cid:`%s`, conn:`%s`, e:`%s`',
                self.config.service_name, msg.id, cid, self.peer_conn_info_pretty, e)

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

        logger.info('Sending response `%s` to `%s` (%s %s)',
           self._shorten_data(serialized), self.pub_client_id, self.ext_client_id, self.ext_client_name)

        try:
            self.send(serialized, msg.cid, cid)
        except AttributeError as e:
            if e.args[0] == "'NoneType' object has no attribute 'text_message'":
                _msg = 'Service response discarded (client disconnected), cid:`%s`, msg.meta:`%s`'
                _meta = msg.get_meta()
                logger.warning(_msg, _meta)
                logger_zato.warning(_msg, _meta)

# ################################################################################################################################

    def _wait_for_event(
        self,
        wait_time:'int',
        condition_callable:'callable_',
        _delta:'callable_'=timedelta,
        _sleep:'callable_'=sleep,
        *args:'any_',
        **kwargs:'any_'
    ) -> 'any_':

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

    def _handle_client_response(
        self,
        cid:'str',
        msg:'any_',
        _msg_id_prefix:'str'=MSG_PREFIX.MSG_ID
    ) -> 'None':
        """ Processes responses from WSX clients - either invokes callbacks for pub/sub responses
        or adds the message to the list of received ones because someone is waiting for it.
        """
        # Pub/sub response
        if msg.in_reply_to.startswith(_msg_id_prefix):
            hook = self.get_on_pubsub_hook()
            if not hook:
                log_msg = 'Ignoring pub/sub response, on_pubsub_response hook not implemented for `%s`, conn:`%s`, msg:`%s`'
                logger.info(log_msg, self.config.name, self.peer_conn_info_pretty, msg)
                if logger_zato_has_debug:
                    logger_zato.debug(log_msg, self.config.name, self.peer_conn_info_pretty, msg)
            else:
                request = self._get_hook_request()
                request['msg'] = msg
                hook(**request)

        # Regular synchronous response, simply enqueue it and someone else will take care of it
        else:
            self.responses_received[msg.in_reply_to] = msg

    def _has_client_response(self, request_id:'str') -> 'any_':
        return self.responses_received.get(request_id)

    def _wait_for_client_response(self, request_id:'str', wait_time:'int'=5) -> 'any_':
        """ Wait until a response from client arrives and return it or return None if there is no response up to wait_time.
        """
        return self._wait_for_event(wait_time, self._has_client_response, request_id=request_id)

# ################################################################################################################################

    def _received_message(
        self,
        data:'any_',
        _default_data:'str'='',
        *args:'any_',
        **kwargs:'any_'
    ) -> 'None':

        # This is one of methods that can be invoked before self.__init__ completes,
        # because self's parent manages the underlying TCP stream, in which can self
        # will not be fully initialized yet so we need to wait a bit until it is.
        while not self._initialized:
            sleep(0.1)

        try:

            # Input bytes must be UTF-8
            try:
                data.decode('utf8')
            except UnicodeDecodeError as e:
                reason = 'Invalid UTF-8 bytes'
                msg = '{}; `{}`'.format(reason, e.args)
                logger.warning(msg)
                logger_zato.warning(msg)
                if self.has_session_opened:
                    response = ErrorResponse('<no-cid>', '<no-msg-id>', UNPROCESSABLE_ENTITY, reason)
                    serialized = response.serialize(self._json_dump_func)
                    log_msg = 'About to send the invalid UTF-8 message to client'
                    logger.warning(log_msg)
                    logger_zato.warning(log_msg)
                    self.send(serialized, new_cid())
                    return
                else:
                    log_msg = 'Disconnecting client due to invalid UTF-8 data'
                    logger.warning(log_msg)
                    logger_zato.warning(log_msg)
                    self.disconnect_client('<no-cid>', code_invalid_utf8, reason)
                    return

            cid = new_cid()
            request = self._parse_func(data or _default_data) # type: any_
            now = _now()
            self.last_seen = now

            if self.is_audit_log_received_active:
                self._store_audit_log_data(DataReceived, data, cid)

            # If client is authenticated, allow it to re-authenticate, which grants a new token, or to invoke a service.
            # Otherwise, authentication is required.

            if self.has_session_opened:

                # Reject request if an already existing token was not given on input, it should have been
                # because the client is authenticated after all.
                if not request.token:
                    self.on_forbidden('did not send token')
                    return

                if request.token != self.token.value:
                    self.on_forbidden('sent an invalid token (`{!r}` instead of `{!r}`)'.format(request.token, self.token.value))
                    return

                # Reject request if token is provided but it already expired
                _timestamp = _now()

                logger.info('Tok rcv: [%s / %s] ts:%s exp:%s -> %s',
                    self.token.value, self.pub_client_id, _timestamp, self.token.expires_at, _timestamp > self.token.expires_at)

                if _timestamp > self.token.expires_at:
                    self.on_forbidden('used an expired token; tok: [{} / {}] ts:{} > exp:{}'.format(
                        self.token.value, self.pub_client_id, _timestamp, self.token.expires_at))
                    return

                # Ok, we can proceed
                try:
                    self.handle_client_message(cid, request) if not request.is_auth else self.handle_create_session(cid, request)

                except ConnectionError as e:
                    msg = 'Ignoring message (ConnectionError), cid:`%s`; conn:`%s`; e:`%s`'
                    logger.info(msg, cid, self.peer_conn_info_pretty, e.args)
                    logger_zato.info(msg, cid, self.peer_conn_info_pretty, e.args)

                except RuntimeError as e:
                    if e.args[0] == _cannot_send:
                        msg = 'Ignoring message (socket terminated #1), cid:`%s`, request:`%s` conn:`%s`'
                        logger.info(msg, cid, request, self.peer_conn_info_pretty)
                        logger_zato.info(msg, cid, request, self.peer_conn_info_pretty)
                    else:
                        raise

            # Unauthenticated - require credentials on input
            else:
                self.handle_create_session(cid, request)

            if logger_has_debug:
                logger.debug('Response returned cid:`%s`, time:`%s`', cid, _now() - now)

        except Exception:
            logger.warning(format_exc())

# ################################################################################################################################

    def received_message(self, message:'Bunch') -> 'None':

        logger.info('Received message %r from `%s` (%s %s)', self._shorten_data(message.data),
            self.pub_client_id, self.ext_client_id, self.ext_client_name)

        try:
            self._received_message(message.data)
        except Exception:
            logger.warning(format_exc())

# ################################################################################################################################

    def send(self, data:'any_'='', cid:'str'='', in_reply_to:'str'='') -> 'None':

        if self.is_audit_log_sent_active:
            self._store_audit_log_data(DataSent, data, cid, in_reply_to)

        # Call the super-class that will actually send the message.
        super().send(data)

# ################################################################################################################################

    def _store_audit_log_data(
        self,
        event_class:'any_',
        data:'any_',
        cid:'str'='',
        in_reply_to:'str'='',
    ) -> 'None':

        # Describe our event ..
        data_event = event_class()
        data_event.type_ = _audit_msg_type
        data_event.object_id = self.pub_client_id
        data_event.data = data if isinstance(data, str) else str(data)
        data_event.timestamp = _now()
        data_event.msg_id = cid
        data_event.in_reply_to = in_reply_to

        # .. and store it in the audit log.
        self.parallel_server.audit_log.store_data(data_event)

# ################################################################################################################################

    def notify_pubsub_message(self, cid:'str', request:'any_') -> 'None':
        """ Invoked by internal services each time a pub/sub message is available for at least one of sub_keys
        this WSX client is responsible for.
        """
        self.pubsub_tool.handle_new_messages(HandleNewMessageCtx(cid, request['has_gd'], request['sub_key_list'],
            request['non_gd_msg_list'], request['is_bg_call'], request['pub_time_max']))

# ################################################################################################################################

    def subscribe_to_topic(self, cid:'str', request:'any_') -> 'None':
        """ Subscribes current WebSocket a topic pointed to by input request object.
        """
        self.invoke_service('zato.pubsub.subscription.create-wsx-subscription-for-current', {
            'topic_name': request
        }, cid=cid)

# ################################################################################################################################

    def run(self) -> 'None':
        try:
            self._init()
            super(WebSocket, self).run()
        except Exception:
            logger.warning('Exception in WebSocket.run `%s`', format_exc())

# ################################################################################################################################

    def _ensure_session_created(self) -> 'None':
        """ Runs in its own greenlet and waits for an authentication request to arrive by self.create_session_by,
        which is a timestamp object. If self.has_session_opened is not True by that time, connection to the remote end
        is closed.
        """
        try:
            if self._wait_for_event(self.config.new_token_wait_time, lambda: self.has_session_opened):
                return

            # We get here if self.has_session_opened has not been set to True by self.create_session_by
            self.on_forbidden('did not create a session within {}s (#1)'.format(self.config.new_token_wait_time))

        except Exception as e:
            if e.args[0] == "'NoneType' object has no attribute 'text_message'":
                self.on_forbidden('did not create a session within {}s (#2)'.format(self.config.new_token_wait_time))
            else:
                logger.warning('Exception in WSX _ensure_session_created `%s`', format_exc())

# ################################################################################################################################

    def _shorten_data(self, data:'str', max_size:'int'=log_msg_max_size) -> 'str':

        # Reusable
        len_data = len(data)

        # No need to shorten anything as long as we fit in the max length allowed ..
        if len_data <= max_size:
            out = data

        # ..otherwise, we need to make a shorter copy
        else:
            out = '%s [...]' % (data[:max_size])

        return '%s (%s B)' % (out, len_data)

# ################################################################################################################################

    def invoke_client(
        self,
        cid:'str',
        request:'any_',
        timeout:'int'=5,
        ctx:'any_'=None,
        use_send:'bool'=True,
        _Class:'any_'=InvokeClientRequest,
        wait_for_response:'bool'=True
    ) -> 'any_':
        """ Invokes a remote WSX client with request given on input, returning its response,
        if any was produced in the expected time.
        """
        # If input request is a string, try to decode it from JSON, but leave as-is in case
        # of an error or if it is not a string.
        if isinstance(request, str):
            try:
                request = stdlib_loads(request)
            except ValueError:
                pass

        # Serialize to string
        msg = _Class(cid, request, ctx)
        serialized = msg.serialize(self._json_dump_func)

        # Log what is about to be sent
        if use_send:
            logger.info('Sending message `%s` from `%s` to `%s` `%s` `%s` `%s`', self._shorten_data(serialized),
                self.python_id, self.pub_client_id, self.ext_client_id, self.ext_client_name, self.peer_conn_info_pretty)

        try:
            if use_send:
                self.send(serialized, cid, msg.in_reply_to)
            else:
                # Do not send whitespace so as not to the exceed the 125 bytes length limit
                # that each ping message has to be contained within.
                serialized = serialized.replace(' ', '').replace('\n', '')
                self.ping(serialized)

        except RuntimeError as e:
            if str(e) == _cannot_send:
                msg = 'Cannot send message (socket terminated #2), cid:`%s`, msg:`%s` conn:`%s`'
                data_msg = self._shorten_data(msg)
                logger.info(data_msg, cid, serialized, self.peer_conn_info_pretty)
                logger_zato.info(data_msg, cid, serialized, self.peer_conn_info_pretty)

            self.disconnect_client(cid, close_code.runtime_invoke_client, 'Client invocation runtime error')
            raise RuntimeInvocationError(cid, 'WSX client disconnected cid:`{}, peer:`{}`'.format(cid, self.peer_conn_info_pretty))

        # Wait for response but only if it is not a pub/sub message,
        # these are always asynchronous and that channel's WSX hook
        # will process the response, if any arrives.
        if _Class is not InvokeClientPubSubRequest:
            if wait_for_response:
                response = self._wait_for_client_response(msg.id, timeout)
                if response:
                    return response if isinstance(response, bool) else response.data # It will be bool in pong responses

# ################################################################################################################################

    def _close_connection(self, verb:'str', *_ignored_args:'any_', **_ignored_kwargs:'any_') -> 'None':
        logger.info('{} %s (%s) to %s (%s %s %s%s'.format(verb),
            self._peer_address, self._peer_fqdn, self._local_address, self.config.name, self.ext_client_id,
            self.pub_client_id, ' {})'.format(self.ext_client_name) if self.ext_client_name else ')')

        self.unregister_auth_client()
        self.container.clients.pop(self.pub_client_id, None)

        # Unregister the client from audit log
        if self.is_audit_log_sent_active or self.is_audit_log_received_active:
            self.parallel_server.audit_log.delete_container(_audit_msg_type, self.pub_client_id)

# ################################################################################################################################

    def disconnect_client(self, cid:'str'='', code:'int'=close_code.default_diconnect, reason:'str'='') -> 'None':
        """ Disconnects the remote client, cleaning up internal resources along the way.
        """
        self._disconnect_requested = True
        self._close_connection('cid:{}; c:{}; r:{}; Disconnecting client from'.format(cid, code, reason))
        if self.stream:
            self.close(code, reason)

# ################################################################################################################################

    def opened(self) -> 'None':
        logger.info('Handling new WSX conn from %s (%s) to %s (%s %s) (%s %s) (%s)', self._peer_address, self._peer_fqdn,
            self._local_address, self.config.name, self.python_id, self.forwarded_for, self.forwarded_for_fqdn,
            self.pub_client_id)

        _ = spawn(self._ensure_session_created)

# ################################################################################################################################

    def closed(self, code:'int'=close_code.default_closed, reason:'str'='') -> 'None':

        # Our self.disconnect_client must have cleaned up everything already
        if not self._disconnect_requested:
            self._close_connection('c:{}; r:{}; Client closed its connection from'.format(code, reason))

    on_socket_terminated = closed

# ################################################################################################################################

    def ponged(self, msg:'Bunch') -> 'None':

        # Audit log comes first
        if self.is_audit_log_received_active:
            self._store_audit_log_data(DataReceived, msg.data)

        # Pretend it's an actual response from the client,
        # we cannot use in_reply_to because pong messages are 1:1 copies of ping ones.
        data = self._json_parser.parse(msg.data) # type: any_
        if data:
            msg_id = data['meta']['id']
            self.responses_received[msg_id] = True

        # Since we received a pong response, it means that the peer is connected,
        # in which case we update its pub/sub metadata.
        self.set_last_interaction_data('wsx.ponged')

# ################################################################################################################################

    def unhandled_error(
        self,
        e:'Exception',
        _msg:'str'='Low-level exception caught, about to close connection from `%s`, e:`%s`'
    ) -> 'None':
        """ Called by the underlying WSX library when a low-level TCP/OS exception occurs.
        """
        # Do not log too many details for common disconnection events ..
        if isinstance(e, ConnectionError):
            details = e.args

        # .. but log everything in other cases.
        else:
            details = format_exc()

        peer_info = self.get_peer_info_pretty()

        logger.info(_msg, peer_info, details)
        logger_zato.info(_msg, peer_info, details)

        self.disconnect_client('<unhandled-error>', close_code.runtime_background_ping, 'Unhandled error caught')

# ################################################################################################################################

    def close(
        self,
        code:'int'=1000,
        reason:'str'='',
        _msg:'str'='Error while closing connection from `%s`, e:`%s`',
        _msg_ignored:'str'='Caught an exception while closing connection from `%s`, e:`%s`'
    ) -> 'None':
        """ Re-implemented from the base class to be able to catch exceptions in self._write when closing connections.
        """
        if not self.server_terminated:
            self.server_terminated = True
            try:
                if self.stream:
                    self._write(self.stream.close(code=code, reason=reason).single(mask=self.stream.always_mask))
                else:
                    raise ConnectionError('WSX stream is already closed')
            except Exception as e:

                peer_info = self.get_peer_info_pretty()

                # Ignore non-essential errors about broken pipes, connections being already reset etc.
                if isinstance(e, ConnectionError):
                    e_description = e.args
                    logger.info(_msg_ignored, peer_info, e_description)
                    logger_zato.info(_msg_ignored, peer_info, e_description)

                # Log details of exceptions of other types.
                else:
                    exc = format_exc()
                    logger.info(_msg, peer_info, exc)
                    logger_zato.info(_msg, peer_info, exc)

# ################################################################################################################################
# ################################################################################################################################

class WebSocketContainer(WebSocketWSGIApplication):

    def __init__(
        self,
        config:'WSXConnectorConfig',
        *args:'any_',
        **kwargs:'any_'
    ) -> 'None':
        self.config = config
        self.clients = {}
        super(WebSocketContainer, self).__init__(*args, **kwargs)

# ################################################################################################################################

    def make_websocket(self, sock:'SocketMixin', protocols:'any_', extensions:'any_', wsgi_environ:'stranydict') -> 'any_':
        try:
            websocket = self.handler_cls(self, self.config, sock, protocols, extensions, wsgi_environ.copy())
            self.clients[websocket.pub_client_id] = websocket
            wsgi_environ['ws4py.websocket'] = websocket
            return websocket
        except Exception:
            logger.warning(format_exc())

# ################################################################################################################################

    def __call__(self, wsgi_environ:'stranydict', start_response:'callable_') -> 'any_':

        try:

            # Populate basic information about the connection
            new_conn_map = {
                'channel_name': self.config.name,
            } # type: stranydict

            for wsgi_key, map_key in new_conn_map_config.items():
                value = wsgi_environ.get(wsgi_key)
                new_conn_map[map_key] = value

            # Log basic details about the incoming connection
            new_conn_info = new_conn_pattern.format(**new_conn_map)
            logger.info('About to handle WSX conn: %s', new_conn_info)

            # Make sure this is a WebSockets request
            if 'HTTP_UPGRADE' not in wsgi_environ:
                raise HandshakeError('No HTTP_UPGRADE in wsgi_environ')

            # Do we have such a path?
            if wsgi_environ['PATH_INFO'] != self.config.path:
                start_response(http404, {})
                _response_dict = error_response[NOT_FOUND]
                _serialized = _response_dict[self.config.data_format]
                return [_serialized]

            # Yes, we do, although we are not sure yet if input is valid,
            # e.g. HTTP_UPGRADE may be missing.
            else:
                _ = super(WebSocketContainer, self).__call__(wsgi_environ, start_response)

        except HandshakeError:
            logger.warning('Handshake error; e:`%s`', format_exc())

            start_response(http400, {})
            _response_dict = error_response[BAD_REQUEST]
            _serialized = _response_dict[self.config.data_format]
            return [_serialized]

        except Exception as e:
            logger.warning('Could not execute __call__; e:`%s`', e.args[0])
            raise

# ################################################################################################################################

    def invoke_client(self, cid:'str', pub_client_id:'str', request:'any_', timeout:'int') -> 'any_':

        #
        # We need to handle a few cases:
        #
        # 1) We have a specific pub_client_id, in which case we invoke that one client and the response is not a list
        # 2) We have no pub_client_id and we have only one client so we invoke that one client and the response is not a list
        # 3) We have no pub_client_id and we have multiple clients so we invoke them all and the response is a list
        #

        #
        # Case 1)
        #
        if pub_client_id:
            return self.clients[pub_client_id].invoke_client(cid, request, timeout) # type: ignore
        else:
            out = {} # type: ignore
            for pub_client_id, wsx in self.clients.items(): # type: ignore
                response:'any_' = wsx.invoke_client(cid, request, timeout)
                out[pub_client_id] = response

            if len(out) > 1:
                return out # type: ignore
            else:
                key = list(out)[0] # type: ignore
                response = out[key] # type: ignore
                return response

# ################################################################################################################################

    def invoke_client_by_attrs(self, cid:'str', attrs:'stranydict', request:'any_', timeout:'int') -> 'any_':

        # Iterate over all the currently connected WebSockets ..
        for client in self.clients.values():

            # .. by default, assume that we do not need to invoke this client ..
            should_invoke = False

            # .. add static typing ..
            client = cast_('WebSocket', client)

            # .. go through each of the attrs that the client is expected to have ..
            for expected_key, expected_value in attrs.items():

                # .. check if the client has such a key at all ..
                client_value = client.client_attrs.get(expected_key, _missing)

                # .. if not, we do not need to continue ..
                if client_value is _missing:
                    continue

                # .. otherwise, confirm that the value is the same ..
                # .. and iterate further if it is not ..
                if client_value != expected_value:
                    continue

                # .. if we are here, it means that this client can be invoked ..
                should_invoke = True

            # .. do invoke it now in background ..
            if should_invoke:
                _ = spawn(client.invoke_client, cid, request, wait_for_response=False)

# ################################################################################################################################

    def broadcast(self, cid:'str', request:'any_') -> 'None':
        for client in self.clients.values():
            _ = spawn(client.invoke_client, cid, request, wait_for_response=False)

# ################################################################################################################################

    def disconnect_client(self, cid:'str', pub_client_id:'str') -> 'any_':

        client = self.clients.get(pub_client_id)
        if client:
            return client.disconnect_client(cid)
        else:
            logger.info('No such WSX client `%s` (%s) (disconnect_client)', pub_client_id, cid)

# ################################################################################################################################

    def notify_pubsub_message(self, cid:'str', pub_client_id:'str', request:'any_') -> 'any_':

        client = self.clients.get(pub_client_id)
        if client:
            return client.notify_pubsub_message(cid, request)
        else:
            logger.info('No such WSX client `%s` (%s) (notify_pubsub_message)', pub_client_id, cid)

# ################################################################################################################################

    def subscribe_to_topic(self, cid:'str', pub_client_id:'str', request:'any_') -> 'any_':
        client = self.clients.get(pub_client_id)
        if client:
            return client.subscribe_to_topic(cid, request)
        else:
            logger.info('No such WSX client `%s` (%s) (subscribe_to_topic)', pub_client_id, cid)

# ################################################################################################################################

    def get_client_by_pub_id(self, pub_client_id:'str') -> 'any_':
        client = self.clients.get(pub_client_id)
        if client:
            return client
        else:
            logger.info('No such WSX client `%s` (get_client_by_pub_id)', pub_client_id)

# ################################################################################################################################
# ################################################################################################################################

class WSXWSGIHandler(WebSocketWSGIHandler):

    def process_result(self) -> 'None':
        for data in self.result or '':
            if data:
                self.write(data)
            else:
                self.write(b'')
        if self.status and not self.headers_sent:
            # In other words, the application returned an empty
            # result iterable (and did not use the write callable)
            # Trigger the flush of the headers.
            self.write(b'')
        if self.response_use_chunked:
            self._sendall(b'0\r\n\r\n')

# ################################################################################################################################
# ################################################################################################################################

class WSXGEventWebSocketPool(GEventWebSocketPool):
    """ Overrides self.clear in order to use __self__ instead of im_self (Python 3).
    """
    def clear(self):
        for greenlet in list(self):
            try:
                websocket = greenlet._run.__self__
                if websocket:
                    websocket.close(1001, 'Server is shutting down')
            except Exception as e:
                logger.info('WSX pool clear exception (info) -> %s', e)
            finally:
                self.discard(greenlet)

# ################################################################################################################################
# ################################################################################################################################

class WebSocketServer(_Gevent_WSGIServer):
    """ A WebSocket server exposing Zato services to client applications.
    """
    handler_class = WSXWSGIHandler

    def __init__(
        self,
        config:'WSXConnectorConfig',
        auth_func:'callable_',
        on_message_callback:'callable_'
    ) -> 'None':

        address_info = urlparse(config.address)

        host, port = address_info.netloc.split(':') # type: ignore
        config.host = host # type: ignore
        config.port = int(port)

        config.path = address_info.path # type: ignore
        config.needs_tls = address_info.scheme == 'wss'
        config.auth_func = auth_func
        config.on_message_callback = on_message_callback
        config.needs_auth = bool(config.sec_name)

        super(WebSocketServer, self).__init__((config.host, config.port), WebSocketContainer(config, handler_cls=WebSocket))

        self.pool = WSXGEventWebSocketPool()

# ################################################################################################################################

    def stop(self, *args:'any_', **kwargs:'any_') -> 'None':
        """ Reimplemented from the parent class to be able to call shutdown prior to its calling self.socket.close.
        """
        # self.socket will exist only if we have previously successfully
        # bound to an address. Otherwise, there will be no such attribute.
        self.pool.clear()
        if hasattr(self, 'socket'):
            self.socket.shutdown(2) # SHUT_RDWR has value of 2 in 'man 2 shutdown'
        super(WebSocketServer, self).stop(*args, **kwargs)

# ################################################################################################################################

    # These two methods are reimplemented from gevent.server to make it possible to use SO_REUSEPORT.

    @classmethod
    def get_listener(self:'any_', address:'any_', backlog:'any_'=None, family:'any_'=None) -> 'any_': # type: ignore
        if backlog is None:
            backlog = self.backlog
        return WebSocketServer._make_socket(address, backlog=backlog, reuse_addr=self.reuse_addr, family=family)

# ################################################################################################################################

    @staticmethod
    def _make_socket(
        address:'str',
        backlog:'int'=50,
        reuse_addr:'boolnone'=None,
        family:'any_'=socket.AF_INET # type: ignore
    ) -> 'any_':

        sock = socket.socket(family=family) # type: ignore
        if reuse_addr is not None:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, reuse_addr) # type: ignore
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1) # type: ignore
        try:
            sock.bind(address)
        except socket.error as e:
            strerror = getattr(e, 'strerror', None)
            if strerror is not None:
                e.strerror = strerror + ': ' + repr(address) # type: ignore
            raise
        sock.listen(backlog)
        sock.setblocking(0)
        return sock

# ################################################################################################################################
# ################################################################################################################################

    def invoke_client(self, cid:'str', pub_client_id:'str', request:'any_', timeout:'int') -> 'any_':
        return self.application.invoke_client(cid, pub_client_id, request, timeout)

    def invoke_client_by_attrs(self, cid:'str', attrs:'stranydict', request:'any_', timeout:'int') -> 'any_':
        return self.application.invoke_client_by_attrs(cid, attrs, request, timeout)

    def broadcast(self, cid:'str', request:'any_') -> 'any_':
        return self.application.broadcast(cid, request)

    def disconnect_client(self, cid:'str', pub_client_id:'str') -> 'any_':
        return self.application.disconnect_client(cid, pub_client_id)

    def notify_pubsub_message(self, cid:'str', pub_client_id:'str', request:'any_') -> 'any_':
        return self.application.notify_pubsub_message(cid, pub_client_id, request)

    def subscribe_to_topic(self, cid:'str', pub_client_id:'str', request:'any_') -> 'any_':
        return self.application.subscribe_to_topic(cid, pub_client_id, request)

    def get_client_by_pub_id(self, pub_client_id:'str') -> 'any_':
        return self.application.get_client_by_pub_id(pub_client_id)

# ################################################################################################################################
# ################################################################################################################################

class ChannelWebSocket(Connector):
    """ A WebSocket channel connector to which external client applications connect.
    """
    start_in_greenlet = True
    _wsx_server: 'WebSocketServer'

    def _start(self) -> 'None':
        config = cast_('any_', self.config)
        self._wsx_server = WebSocketServer(config, self.auth_func, self.on_message_callback)
        self.is_connected = True
        self._wsx_server.start()

    def _stop(self) -> 'None':
        if self.is_connected:
            self._wsx_server.stop(3)
            self.is_connected = False

    def get_log_details(self) -> 'str':
        return cast_('str', self.config.address)

    def invoke(
        self,
        cid:'str',
        pub_client_id:'str'='',
        request:'any_'=None,
        timeout:'int'=5,
        remove_wrapper:'bool'=True
    ) -> 'any_':
        response = self._wsx_server.invoke_client(cid, pub_client_id, request, timeout)
        if remove_wrapper:
            if isinstance(response, dict):
                if 'response' in response:
                    return response['response'] # type: ignore
        return response # type: ignore

    def invoke_by_attrs(self, cid:'str', attrs:'stranydict', request:'any_', timeout:'int'=5) -> 'any_':
        return self._wsx_server.invoke_client_by_attrs(cid, attrs, request, timeout)

    def broadcast(self, cid:'str', request:'any_') -> 'any_':
        return self._wsx_server.broadcast(cid, request)

    def disconnect_client(self, cid:'str', pub_client_id:'str', *ignored_args:'any_', **ignored_kwargs:'any_') -> 'any_':
        return self._wsx_server.disconnect_client(cid, pub_client_id)

    def notify_pubsub_message(self, cid:'str', pub_client_id:'str', request:'any_') -> 'any_':
        return self._wsx_server.notify_pubsub_message(cid, pub_client_id, request)

    def subscribe_to_topic(self, cid:'str', pub_client_id:'str', request:'any_') -> 'any_':
        return self._wsx_server.subscribe_to_topic(cid, pub_client_id, request)

    def get_client_by_pub_id(self, pub_client_id:'str') -> 'any_':
        return self._wsx_server.get_client_by_pub_id(pub_client_id)

    def get_conn_report(self) -> 'stranydict':
        return self._wsx_server.environ

    # Convenience aliases
    invoke_client = invoke
    invoke_client_by_attrs = invoke_by_attrs

# ################################################################################################################################
# ################################################################################################################################
