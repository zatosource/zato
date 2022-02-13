# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

#
# Note that this module must not have any runtime Zato-related dependencies, e.g. imports from zato.common,
# because it is distributed via PyPI as well under the name of zato-wsx-client.
#
# It may have any external dependencies, as required.
#

# stdlib
import logging
import random
from dataclasses import dataclass
from datetime import datetime, timedelta
from http.client import OK
from traceback import format_exc

# gevent
from gevent import sleep, spawn

# pysimdjson
from simdjson import Parser as SIMDJSONParser

# ujson
from ujson import dumps as json_dumps

# ws4py
from ws4py.client.geventclient import WebSocketClient

# ################################################################################################################################
# ################################################################################################################################

if 0:
    # Type-checking dependencies are acceptable
    from zato.common.typing_ import any_, anydict, callable_, callnone, strnone

# ################################################################################################################################
# ################################################################################################################################

def new_cid(bytes:'int'=12, _random:'callable_'=random.getrandbits) -> 'str':
    # Copied over from zato.common.util.api
    return hex(_random(bytes * 8))[2:]

# ################################################################################################################################
# ################################################################################################################################

class MSG_PREFIX:
    _COMMON = 'zwsxc.{}'
    INVOKE_SERVICE = _COMMON.format('inv.{}')
    SEND_AUTH = _COMMON.format('auth.{}')
    SEND_RESP = _COMMON.format('rsp.{}')

# ################################################################################################################################
# ################################################################################################################################

zato_keep_alive_ping = 'zato-keep-alive-ping'
_invalid = '_invalid.' + new_cid()

utcnow = datetime.utcnow

# ################################################################################################################################
# ################################################################################################################################

class Default:
    ResponseWaitTime = 5 # How many seconds to wait for responses

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Config:

    address: 'str'
    client_id: 'str'
    client_name: 'str'
    on_request_callback: 'callable_'

    username: 'strnone' = None
    secret: 'strnone' = None
    on_closed_callback: 'callnone' = None
    wait_time: 'int' = Default.ResponseWaitTime

# ################################################################################################################################
# ################################################################################################################################

class MessageToZato:
    """ An individual message from a WebSocket client to Zato, either request or response to a previous request from Zato.
    """
    action = _invalid

    def __init__(self, msg_id:'str', config:'Config', token:'strnone'=None) -> 'None':
        self.config = config
        self.msg_id = msg_id
        self.token = token

    def serialize(self) -> 'str':
        return json_dumps(self.enrich({
            'data': {},
            'meta': {
                'action': self.action,
                'id': self.msg_id,
                'timestamp': utcnow().isoformat(),
                'token': self.token,
                'client_id': self.config.client_id,
                'client_name': self.config.client_name,
            }
        }))

    def enrich(self, msg:'anydict') -> 'anydict':
        """ Implemented by subclasses that need to add extra information.
        """
        return msg

# ################################################################################################################################
# ################################################################################################################################

class AuthRequest(MessageToZato):
    """ Logs a client into a WebSocket connection.
    """
    action = 'create-session'

    def enrich(self, msg:'anydict') -> 'anydict':
        msg['meta']['username'] = self.config.username
        msg['meta']['secret'] = self.config.secret
        return msg

# ################################################################################################################################
# ################################################################################################################################

class ServiceInvokeRequest(MessageToZato):
    """ Encapsulates information about an invocation of a Zato service.
    """
    action = 'invoke-service'

    def __init__(self, request_id:'str', data:'any_', *args:'any_', **kwargs:'any_') -> 'None':
        self.data = data
        super(ServiceInvokeRequest, self).__init__(request_id, *args, **kwargs)

    def enrich(self, msg:'anydict') -> 'anydict':
        msg['data'].update(self.data)
        return msg

# ################################################################################################################################
# ################################################################################################################################

class ResponseFromZato:
    """ A response from Zato to a previous request by this client.
    """
    id: 'str'
    timestamp: 'str'
    in_reply_to: 'strnone'
    status: 'str'
    is_ok: 'bool'
    data: 'any_'
    msg_impl: 'any_'

    @staticmethod
    def from_json(msg:'anydict') -> 'ResponseFromZato':
        response = ResponseFromZato()
        response.msg_impl = msg
        meta = msg['meta']
        response.id = meta['id']
        response.timestamp = meta['timestamp']
        response.in_reply_to = meta['in_reply_to']
        response.status = meta['status']
        response.is_ok = response.status == OK
        response.data = msg.get('data')

        return response

# ################################################################################################################################
# ################################################################################################################################

class RequestFromZato:
    """ A request from Zato to this client.
    """
    id: 'str'
    timestamp: 'str'
    data: 'any_'
    msg_impl: 'any_'

    @staticmethod
    def from_json(msg:'anydict') -> 'RequestFromZato':
        request = RequestFromZato()
        request.msg_impl = msg
        request.id = msg['meta']['id']
        request.timestamp = msg['meta']['timestamp']
        request.data = msg['data']

        return request

# ################################################################################################################################
# ################################################################################################################################

class ResponseToZato(MessageToZato):
    """ A response from this client to a previous request from Zato.
    """
    action = 'client-response'

    def __init__(self, in_reply_to:'str', data:'any_', *args:'any_', **kwargs:'any_') -> 'None':
        self.in_reply_to = in_reply_to
        self.data = data
        super(ResponseToZato, self).__init__(*args, **kwargs)

    def enrich(self, msg:'anydict') -> 'anydict':
        msg['meta']['in_reply_to'] = self.in_reply_to
        msg['data']['response'] = self.data
        return msg

# ################################################################################################################################
# ################################################################################################################################

class _WebSocketClientImpl(WebSocketClient):
    """ A low-level subclass of ws4py's WebSocket client functionality.
    """
    def __init__(
        self,
        on_connected_callback:'callable_',
        on_message_callback:'callable_',
        on_error_callback:'callable_',
        on_closed_callback:'callable_',
        *args:'any_',
        **kwargs:'any_'
    ) -> 'None':
        self.on_connected_callback = on_connected_callback
        self.on_message_callback = on_message_callback
        self.on_error_callback = on_error_callback
        self.on_closed_callback = on_closed_callback
        super(_WebSocketClientImpl, self).__init__(*args, **kwargs)

    def opened(self) -> 'None':
        _ = spawn(self.on_connected_callback)

    def received_message(self, msg:'anydict') -> 'None':
        self.on_message_callback(msg)

    def unhandled_error(self, error:'any_') -> 'None':
        _ = spawn(self.on_error_callback, error)

    def closed(self, code:'int', reason:'strnone'=None) -> 'None':
        super(_WebSocketClientImpl, self).closed(code, reason)
        self.on_closed_callback(code, reason)

# ################################################################################################################################
# ################################################################################################################################

class Client:
    """ A WebSocket client that knows how to invoke Zato services.
    """
    def __init__(self, config:'Config') -> 'None':
        self.config = config
        self.conn = _WebSocketClientImpl(self.on_connected, self.on_message, self.on_error, self.on_closed, self.config.address)
        self.keep_running = True
        self.is_authenticated = False
        self.is_connected = False
        self.is_auth_needed = bool(self.config.username)
        self.auth_token = None
        self.on_request_callback = self.config.on_request_callback
        self.on_closed_callback = self.config.on_closed_callback
        self.needs_auth = bool(self.config.username)
        self._json_parser = SIMDJSONParser()
        self.logger = logging.getLogger(__name__)

        # Keyed by IDs of requests sent from this client to Zato
        self.requests_sent = {}

        # Same key as self.requests_sent but the dictionary contains responses to previously sent requests
        self.responses_received = {}

        # Requests initiated by Zato, keyed by their IDs
        self.requests_received = {}

        # Log information that we are about to become available
        self.logger.info('Starting WSX client: %s -> name:`%s`; id:`%s`; u:`%s`',
            self.config.address, self.config.client_name, self.config.client_id, self.config.username)

# ################################################################################################################################

    def send(self, msg_id:'str', msg:'MessageToZato', wait_time:'int'=2) -> 'None':
        """ Spawns a greenlet to send a message to Zato.
        """
        _ = spawn(self._send, msg_id, msg, msg.serialize(), wait_time)

# ################################################################################################################################

    def _send(self, msg_id:'str', msg:'dict', serialized:'str', wait_time:'int') -> 'None':
        """ Sends a request to Zato and waits up to wait_time or self.config.wait_time seconds for a reply.
        """
        self.logger.info('Sending msg `%s`', serialized)

        # So that it can be correlated with a future response
        self.requests_sent[msg_id] = msg

        # Actually send the messageas string now
        self.conn.send(serialized)

# ################################################################################################################################

    def _wait_for_response(
        self,
        request_id:'str',
        wait_time:'int'=Default.ResponseWaitTime,
    ) -> 'any_':
        """ Wait until a response arrives and return it
        or return None if there is no response up to wait_time or self.config.wait_time.
        """
        now = utcnow()
        until = now + timedelta(seconds=wait_time or self.config.wait_time)

        while now < until:

            response = self.responses_received.get(request_id)
            if response:
                return response
            else:
                sleep(0.01)
                now = utcnow()

# ################################################################################################################################

    def authenticate(self, request_id:'str') -> 'None':
        """ Authenticates the client with Zato.
        """
        self.logger.info('Authenticating as `%s` (%s %s)', self.config.username, self.config.client_name, self.config.client_id)
        _ = spawn(self.send, request_id, AuthRequest(request_id, self.config, self.auth_token))

# ################################################################################################################################

    def on_connected(self) -> 'None':
        """ Invoked upon establishing an initial connection - logs the client in with self.config's credentials
        """
        self.logger.info('Connected to `%s` %s (%s %s)',
            self.config.address,
            'as `{}`'.format(self.config.username) if self.config.username else 'without credentials',
            self.config.client_name, self.config.client_id)

        request_id = MSG_PREFIX.SEND_AUTH.format(new_cid())
        self.authenticate(request_id)

        response = self._wait_for_response(request_id)

        if not response:
            self.logger.warning('No response to authentication request `%s`', request_id)
        else:
            self.auth_token = response.data['token']
            self.is_authenticated = True
            del self.responses_received[request_id]

            self.logger.info('Authenticated successfully as `%s` (%s %s)',
                self.config.username, self.config.client_name, self.config.client_id)

# ################################################################################################################################

    def on_message(self, msg:'ResponseFromZato') -> 'None':
        """ Invoked for each message received from Zato, both for responses to previous requests and for incoming requests.
        """
        _msg_parsed = self._json_parser.parse(msg.data) # type: any_
        _msg = _msg_parsed.as_dict() # type: anydict
        self.logger.info('Received message `%s`', _msg)

        in_reply_to = _msg['meta'].get('in_reply_to')

        # Reply from Zato to one of our requests
        if in_reply_to:
            self.responses_received[in_reply_to] = ResponseFromZato.from_json(_msg)

        # Request from Zato
        else:
            data = self.on_request_callback(RequestFromZato.from_json(_msg))
            response_id = MSG_PREFIX.SEND_RESP.format(new_cid())
            self.send(response_id, ResponseToZato(_msg['meta']['id'], data, response_id, self.config, self.auth_token))

# ################################################################################################################################

    def on_closed(self, code:'int', reason:'strnone'=None) -> 'None':
        self.logger.info('Closed WSX client connection to `%s` (remote code:%s reason:%s)', self.config.address, code, reason)
        if self.on_closed_callback:
            self.on_closed_callback(code, reason)

# ################################################################################################################################

    def on_error(self, error:'any_') -> 'None':
        """ Invoked for each unhandled error in the lower-level ws4py library.
        """
        self.logger.warning('Caught error %s', error)

# ################################################################################################################################

    def _run(self, max_wait:'int'=10, _sleep_time:'int'=2) -> 'None':
        """ Attempts to connects to a remote WSX server or raises an exception if max_wait time is exceeded.
        """
        needs_connect = True
        start = now = datetime.utcnow()

        # In the first few seconds, do not warn about socket errors in case
        # the other end is intrinsically slow to connect to.
        warn_from = start + timedelta(seconds=3)
        use_warn = False

        # Wait for max_wait seconds until we have the connection
        until = now + timedelta(seconds=max_wait)

        while self.keep_running and needs_connect and now < until:
            try:
                if self.conn.sock:
                    self.conn.connect()
                else:
                    raise ValueError('No WSX connection to {} after {}'.format(self.config.address, now - start))
            except Exception as e:

                if use_warn:
                    log_func = self.logger.warning
                else:
                    if now >= warn_from:
                        log_func = self.logger.warning
                        use_warn = True
                    else:
                        log_func = self.logger.debug

                log_func('Exception caught `%s` while connecting to WSX `%s (%s)`', e, self.config.address, format_exc())
                sleep(_sleep_time)
                now = utcnow()
            else:
                needs_connect = False
                self.is_connected = True

# ################################################################################################################################

    def run(self, max_wait:'int'=20) -> 'None':

        # Actually try to connect ..
        self._run()

        # .. wait for the connection for that much time ..
        now = utcnow()
        until = now + timedelta(seconds=max_wait)

        # .. do wait and return if max. wait time is exceeded ..
        while not self.is_connected:
            sleep(0.01)
            now = utcnow()
            if now >= until:
                return

        # .. otherwise, if we are here, it means that we are connected,
        # .. although we may be still not authenticated as this step
        # .. is carried out by the on_connected_callback method.

# ################################################################################################################################

    def stop(self, reason:'str'='') -> 'None':
        self.keep_running = False
        self.conn.close(reason=reason)
        self.is_connected = False

# ################################################################################################################################

    def invoke(self, data:'any_', timeout:'int'=Default.ResponseWaitTime) -> 'any_':
        if self.needs_auth and (not self.is_authenticated):
            raise Exception('Client is not authenticated')

        request_id = MSG_PREFIX.INVOKE_SERVICE.format(new_cid())
        spawn(self.send, request_id, ServiceInvokeRequest(request_id, data, self.config, self.auth_token))

        response = self._wait_for_response(request_id, wait_time=timeout)

        if not response:
            self.logger.warning('No response to invocation request `%s`', request_id)
        else:
            return response

################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # First thing in the process
    from gevent import monkey
    monkey.patch_all()

    log_format = '%(asctime)s - %(levelname)s - %(name)s:%(lineno)d - %(message)s'
    logging.basicConfig(level=logging.DEBUG, format=log_format)

    _cli_logger = logging.getLogger('zato')

    def on_request_from_zato(msg:'RequestFromZato') -> 'any_':
        try:
            _cli_logger.info('Message from Zato received -> %s', msg)
            return 'Hello'
        except Exception:
            return format_exc()

    address = 'ws://127.0.0.1:47043/zato.wsx.apitests'
    client_id = '123456'
    client_name = 'My Client'
    on_request_callback = on_request_from_zato

    config = Config()
    config.address = address
    config.client_id = client_id
    config.client_name = client_name
    config.on_request_callback = on_request_callback
    config.username = 'user1'
    config.secret = 'secret1'

    client = Client(config)
    client.run()

    # Wait until we are authenticated to invoke a test service
    sleep(0.5)
    client.invoke({'service':'zato.ping'})

    _cli_logger.info('Press Ctrl-C to quit')

    try:
        x = 0
        while x < 1000 and client.keep_running:
            sleep(0.2)
    except KeyboardInterrupt:
        client.stop()

# ################################################################################################################################
################################################################################################################################
