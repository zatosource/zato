# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# First thing in the process
from gevent import monkey
_ = monkey.patch_all()

# stdlib
import os
import random
import socket
from dataclasses import dataclass
from datetime import datetime, timedelta
from http.client import OK
from json import dumps as json_dumps
from logging import getLogger
from threading import Thread
from traceback import format_exc
from types import GeneratorType

# gevent
from gevent import sleep, spawn

# ws4py
from ws4py.client.geventclient import WebSocketClient
from ws4py.messaging import Message as ws4py_Message, PingControlMessage

# Zato
from zato.common.api import WEB_SOCKET
from zato.common.marshal_.api import MarshalAPI, Model
from zato.common.util.json_ import JSONParser

try:
    from OpenSSL.SSL import Error as PyOpenSSLError
    _ = PyOpenSSLError
except ImportError:
    class PyOpenSSLError(Exception):
        pass

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from ws4py.messaging import TextMessage
    from zato.common.typing_ import any_, anydict, callable_, callnone, strnone

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

def new_cid(bytes:'int'=12, _random:'callable_'=random.getrandbits) -> 'str':
    # Copied over from zato.common.util.api
    return hex(_random(bytes * 8))[2:]

# ################################################################################################################################
# ################################################################################################################################

class MsgPrefix:
    _Common = 'zwsxc.{}'
    InvokeService = _Common.format('inv.{}')
    SendAuth = _Common.format('auth.{}')
    SendResponse = _Common.format('rsp.{}')

# ################################################################################################################################
# ################################################################################################################################

zato_keep_alive_ping = 'zato-keep-alive-ping'
_invalid = '_invalid.' + new_cid()

utcnow = datetime.utcnow

_ping_interval = WEB_SOCKET.DEFAULT.PING_INTERVAL
_ping_missed_threshold = WEB_SOCKET.DEFAULT.PING_INTERVAL

# This is how long we wait for responses - longer than the ping interval is
wsx_socket_timeout = _ping_interval + (_ping_interval * 0.1)

# ################################################################################################################################
# ################################################################################################################################

class Default:
    ResponseWaitTime = os.environ.get('Zato_WSX_Response_Wait_Time') or 5 # How many seconds to wait for responses
    MaxConnectAttempts = 1234567890
    MaxWaitTime = 999_999_999

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
    max_connect_attempts: 'int' = Default.MaxConnectAttempts

    # This is a method that will tell the client whether its parent connection definition is still active.
    check_is_active_func: 'callable_'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class ClientMeta(Model):
    id: 'str'
    action: 'str'
    attrs: 'strnone' = None
    timestamp: 'str'
    client_id: 'str'
    client_name: 'str'
    token: 'strnone'
    username: 'strnone' = None
    secret: 'strnone' = None
    in_reply_to: 'strnone' = None

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class ClientToServerModel(Model):
    meta: 'ClientMeta'
    data: 'anydict'

# ################################################################################################################################
# ################################################################################################################################

class ClientToServerMessage:
    """ An individual message from a WebSocket client to Zato, either request or response to a previous request from Zato.
    """
    action = _invalid

    def __init__(self, msg_id:'str', config:'Config', token:'strnone'=None) -> 'None':
        self.config = config
        self.msg_id = msg_id
        self.token = token

    def serialize(self) -> 'str':

        # Base metadata that we can always produce
        # and subclasses can always write to, if needed.
        meta = ClientMeta()
        meta.action = self.action
        meta.id = self.msg_id
        meta.timestamp = utcnow().isoformat()
        meta.token = self.token
        meta.client_id = self.config.client_id
        meta.client_name = self.config.client_name

        # We can build an empty request that subclasses will fill out with actual data
        request = ClientToServerModel()
        request.meta = meta
        request.data = {}

        # Each subclass can enrich the message with is own specific information
        enriched = self.enrich(request)

        # Now, we are ready to serialize the message ..
        serialized = json_dumps(enriched.to_dict())

        # .. and to finally return it
        return serialized

    def enrich(self, msg:'ClientToServerModel') -> 'ClientToServerModel':
        """ Implemented by subclasses that need to add extra information.
        """
        return msg

# ################################################################################################################################
# ################################################################################################################################

class AuthRequest(ClientToServerMessage):
    """ Logs a client into a WebSocket connection.
    """
    action = 'create-session'

    def enrich(self, msg:'ClientToServerModel') -> 'ClientToServerModel':
        msg.meta.username = self.config.username
        msg.meta.secret = self.config.secret

        # Client attributes can be optionally provided via environment variables
        if client_attrs := os.environ.get('Zato_WSX_Client_Attrs'):
            msg.meta.attrs = client_attrs

        return msg

# ################################################################################################################################
# ################################################################################################################################

class ServiceInvocationRequest(ClientToServerMessage):
    """ Encapsulates information about an invocation of a Zato service.
    """
    action = 'invoke-service'

    def __init__(self, request_id:'str', data:'any_', *args:'any_', **kwargs:'any_') -> 'None':
        self.data = data
        super(ServiceInvocationRequest, self).__init__(request_id, *args, **kwargs)

    def enrich(self, msg:'ClientToServerModel') -> 'ClientToServerModel':
        msg.data.update(self.data)
        return msg

# ################################################################################################################################
# ################################################################################################################################

class ResponseToServer(ClientToServerMessage):
    """ A response from this client to a previous request from Zato.
    """
    action = 'client-response'

    def __init__(self, in_reply_to:'str', data:'any_', *args:'any_', **kwargs:'any_') -> 'None':
        self.in_reply_to = in_reply_to
        self.data = data
        super(ResponseToServer, self).__init__(*args, **kwargs)

    def enrich(self, msg:'ClientToServerModel') -> 'ClientToServerModel':
        msg.meta.in_reply_to = self.in_reply_to
        msg.data['response'] = self.data
        return msg

# ################################################################################################################################
# ################################################################################################################################

class MessageFromServer:
    """ A message from server, either a server-initiated request or a response to our own previous request.
    """
    id: 'str'
    timestamp: 'str'
    data: 'any_'
    msg_impl: 'any_'

    @staticmethod
    def from_json(msg:'anydict') -> 'MessageFromServer':
        raise NotImplementedError('Must be implemented in subclasses')

# ################################################################################################################################

    def to_dict(self):
        return {'id':self.id, 'timestamp':self.timestamp, 'data':self.data}

# ################################################################################################################################
# ################################################################################################################################

class ResponseFromServer(MessageFromServer):
    """ A response from Zato to a previous request by this client.
    """
    in_reply_to: 'strnone'
    status: 'str'
    is_ok: 'bool'

    @staticmethod
    def from_json(msg:'anydict') -> 'ResponseFromServer':
        response = ResponseFromServer()
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

class RequestFromServer(MessageFromServer):
    """ A request from Zato to this client.
    """
    @staticmethod
    def from_json(msg:'anydict') -> 'RequestFromServer':
        request = RequestFromServer()
        request.msg_impl = msg
        request.id = msg['meta']['id']
        request.timestamp = msg['meta']['timestamp']
        request.data = msg['data']

        return request

# ################################################################################################################################
# ################################################################################################################################

class WSXHeartbeat(Thread):
    def __init__(self, websocket:'any_', frequency:'float'=2.0) -> 'None':
        Thread.__init__(self)
        self.websocket = websocket
        self.frequency = frequency

    def __enter__(self) -> 'WSXHeartbeat':
        if self.frequency:
            self.start()
        return self

    def __exit__(self, exc_type:'any_', exc_value:'any_', exc_tb:'any_') -> 'None':
        self.stop()

    def stop(self) -> 'None':
        self.running = False

    def run(self) -> 'None':
        self.running = True
        while self.running:
            sleep(self.frequency)
            if self.websocket.terminated:
                break

            try:
                self.websocket.send(PingControlMessage(data='beep'))
            except socket.error:
                logger.info('Heartbeat failed')
                self.websocket.server_terminated = True
                self.websocket.close_connection()
                break

# ################################################################################################################################
# ################################################################################################################################

class _WebSocketClientImpl(WebSocketClient):
    """ A low-level subclass of ws4py's WebSocket client functionality.
    """
    def __init__(
        self,
        config:'Config',
        on_connected_callback:'callable_',
        on_message_callback:'callable_',
        on_error_callback:'callable_',
        on_closed_callback:'callable_'
    ) -> 'None':

        # Assign our own pieces of configuration ..
        self.config = config
        self.on_connected_callback = on_connected_callback
        self.on_message_callback = on_message_callback
        self.on_error_callback = on_error_callback
        self.on_closed_callback = on_closed_callback

        # .. call the parent ..
        super(_WebSocketClientImpl, self).__init__(url=self.config.address)

        # .. adjust parent's configuration ..
        self.heartbeat_freq = 5.0

# ################################################################################################################################

    def close_connection(self):
        """ Overridden from ws4py.websocket.WebSocket.
        """
        if self.sock:
            try:
                self.sock.shutdown(socket.SHUT_RDWR)
            except Exception:
                pass
            try:
                self.sock.close()
            except Exception:
                pass
            finally:
                self.sock = None

    def opened(self) -> 'None':
        _ = spawn(self.on_connected_callback)

# ################################################################################################################################

    def received_message(self, msg:'anydict') -> 'None':
        self.on_message_callback(msg)

# ################################################################################################################################

    def unhandled_error(self, error:'any_') -> 'None':
        _ = spawn(self.on_error_callback, error)

# ################################################################################################################################

    def closed(self, code:'int', reason:'strnone'=None) -> 'None':
        super(_WebSocketClientImpl, self).closed(code, reason)
        self.on_closed_callback(code, reason)

# ################################################################################################################################

    def send(self, payload:'any_', binary:'bool'=False) -> 'None':
        """ Overloaded from the parent class.
        """
        if not self.stream:
            logger.info('Could not send message without self.stream -> %s -> %s (%s -> %s) ',
                self.config.client_name,
                self.config.address,
                self.config.username,
                self.config.client_id,
            )
            return

        message_sender = self.stream.binary_message if binary else self.stream.text_message # type: any_

        if isinstance(payload, str) or isinstance(payload, bytearray):
            m = message_sender(payload).single(mask=self.stream.always_mask)
            self._write(m)

        elif isinstance(payload, ws4py_Message):
            data = payload.single(mask=self.stream.always_mask)
            self._write(data)

        elif type(payload) == GeneratorType:
            bytes = next(payload)
            first = True
            for chunk in payload:
                self._write(message_sender(bytes).fragment(first=first, mask=self.stream.always_mask))
                bytes = chunk
                first = False

            self._write(message_sender(bytes).fragment(last=True, mask=self.stream.always_mask))

        else:
            raise ValueError('Unsupported type `%s` passed to send()' % type(payload))

# ################################################################################################################################

    def _write(self, data:'bytes') -> 'None':
        """ Overloaded from the parent class.
        """
        if self.terminated or self.sock is None:
            logger.info('Could not send message on a terminated socket; `%s` -> %s (%s)',
                self.config.client_name, self.config.address, self.config.client_id)
        else:
            self.sock.settimeout(60)
            self.sock.sendall(data)

# ################################################################################################################################

    def run(self):
        self.sock.setblocking(True) # type: ignore
        with WSXHeartbeat(self, frequency=self.heartbeat_freq):
            try:
                self.opened()
                while not self.terminated:
                    if not self.once():
                        break
            finally:
                self.terminate()

# ################################################################################################################################
# ################################################################################################################################

class Client:
    """ A WebSocket client that knows how to invoke Zato services.
    """
    max_connect_attempts: 'int'
    conn: '_WebSocketClientImpl'

    def __init__(self, config:'Config') -> 'None':
        self.config = config
        self.conn = self.create_conn(self.config)
        self.keep_running = True
        self.is_authenticated = False
        self.is_connected = False
        self.is_auth_needed = bool(self.config.username)
        self.auth_token = ''
        self.on_request_callback = self.config.on_request_callback
        self.on_closed_callback = self.config.on_closed_callback
        self.needs_auth = bool(self.config.username)
        self.max_connect_attempts = self.config.max_connect_attempts
        self._marshal_api = MarshalAPI()
        self.logger = getLogger('zato_web_socket')

        # Keyed by IDs of requests sent from this client to Zato
        self.requests_sent = {}

        # Same key as self.requests_sent but the dictionary contains responses to previously sent requests
        self.responses_received = {}

        # Requests initiated by Zato, keyed by their IDs
        self.requests_received = {}

        # Log information that we are about to become available
        self.logger.info('Starting WSX client: %s -> name:`%s`; id:`%s`; u:`%s`',
            self.config.address, self.config.client_name, self.config.client_id, self.config.username)

    def create_conn(self, config:'Config') -> '_WebSocketClientImpl':
        conn = _WebSocketClientImpl(
            config,
            self.on_connected,
            self.on_message,
            self.on_error,
            self.on_closed,
        )
        return conn

# ################################################################################################################################

    def send(self, msg_id:'str', msg:'ClientToServerMessage', wait_time:'int'=2) -> 'None':
        """ Spawns a greenlet to send a message to Zato.
        """
        _ = spawn(self._send, msg_id, msg, msg.serialize(), wait_time)

# ################################################################################################################################

    def _send(self, msg_id:'str', msg:'anydict', serialized:'str', wait_time:'int') -> 'None':
        """ Sends a request to Zato and waits up to wait_time or self.config.wait_time seconds for a reply.
        """
        self.logger.info('Sending msg `%s`', serialized)

        # So that it can be correlated with a future response
        self.requests_sent[msg_id] = msg

        # Actually send the message as string now
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

            response = self.responses_received.get(request_id) # type: any_
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

        request_id = MsgPrefix.SendAuth.format(new_cid())
        self.authenticate(request_id)

        response = self._wait_for_response(request_id)

        if not response:
            self.logger.warning('No response to authentication request `%s`; (%s %s -> %s)',
                request_id, self.config.username, self.config.client_name, self.config.client_id)
            self.keep_running = False
        else:
            self.auth_token = response.data['token']
            self.is_authenticated = True
            del self.responses_received[request_id]

            self.logger.info('Authenticated successfully as `%s` (%s %s)',
                self.config.username, self.config.client_name, self.config.client_id)

# ################################################################################################################################

    def _on_message(self, msg:'TextMessage') -> 'None':
        """ Invoked for each message received from Zato, both for responses to previous requests and for incoming requests.
        """
        _msg = JSONParser().parse(msg.data) # type: anydict
        self.logger.info('Received message `%s`', _msg)

        in_reply_to = _msg['meta'].get('in_reply_to')

        # Reply from Zato to one of our requests
        if in_reply_to:
            self.responses_received[in_reply_to] = ResponseFromServer.from_json(_msg)

        # Request from Zato
        else:
            data = self.on_request_callback(RequestFromServer.from_json(_msg))
            response_id = MsgPrefix.SendResponse.format(new_cid())
            self.send(response_id, ResponseToServer(_msg['meta']['id'], data, response_id, self.config, self.auth_token))

# ################################################################################################################################

    def on_message(self, msg:'TextMessage') -> 'None':
        try:
            return self._on_message(msg)
        except Exception:
            self.logger.info('Exception in on_message -> %s', format_exc())

# ################################################################################################################################

    def on_closed(self, code:'int', reason:'strnone'=None) -> 'None':
        self.logger.info('Closed WSX client connection to `%s` (remote code:%s reason:%s)', self.config.address, code, reason)
        if self.on_closed_callback:
            self.on_closed_callback(code, reason)

# ################################################################################################################################

    def on_error(self, error:'any_') -> 'None':
        """ Invoked for each unhandled error in the lower-level ws4py library.
        """
        self.logger.warning('Caught error `%s`', error)

# ################################################################################################################################

    def _run(self, max_wait:'int'=10, _sleep_time:'int'=2) -> 'None':
        """ Attempts to connects to a remote WSX server or raises an exception if max_wait time is exceeded.
        """

        # We are just starting out
        num_connect_attempts = 0
        needs_connect = True
        start = now = datetime.utcnow()

        # Initially, do not warn about socket errors in case
        # the other end is intrinsically slow to connect to.
        warn_from = start + timedelta(hours=24)
        use_warn = False

        # Wait for max_wait seconds until we have the connection
        until = now + timedelta(seconds=max_wait)

        while self.keep_running and needs_connect and now < until:

            # Check whether our connection definition is still active ..
            is_active = self.config.check_is_active_func()

            # .. if it is not, we can break out of the loop.
            if not is_active:
                self.logger.info('Skipped building an inactive WSX connection -> %s', self.config.client_name)
                self.keep_running = False
                break

            # Check if we have already run out of attempts.
            if num_connect_attempts >= self.max_connect_attempts:
                self.logger.warning('Max. connect attempts reached, quitting; %s/%s -> %s (%s)',
                    num_connect_attempts,
                    self.max_connect_attempts,
                    self.config.address,
                    now - start)

                # .. and quit if we have reached the limit.
                break

            # If we are here, it means that we have not reached the limit yet
            # so we can increase the counter as the first thing ..
            num_connect_attempts += 1

            try:

                # The underlying TCP socket may have been deleted ..
                if not self.conn.sock:

                    # .. and we need to recreate it .
                    self.conn = self.create_conn(self.config)

                # If we are here, it means that we likely have a TCP socket to use ..
                try:
                    self.conn.connect()

                # .. however, we still need to catch the broken pipe error
                # .. and, in such a case, forcibly close the connection
                # .. to let it be opened in the next iteration of this loop.
                except BrokenPipeError:
                    self.conn.close_connection()
                    raise

            except Exception as e:
                if use_warn:
                    log_func = self.logger.warning
                else:
                    if now >= warn_from:
                        log_func = self.logger.warning
                        use_warn = True
                    else:
                        log_func = self.logger.info

                log_func('Exception caught in iter %s/%s `%s` while connecting to WSX `%s (%s)`',
                    num_connect_attempts,
                    self.max_connect_attempts,
                    e,
                    self.config.address,
                    self.conn.sock,
                )

                # .. this is needed to ensure that the next attempt will not reuse the current TCP socket ..
                # .. which, under Windows, would make it impossible to establish the connection ..
                # .. even if the remote endpoint existed. I.e. this would result in the error below:
                # .. [Errno 10061] [WinError 10061] No connection could be made because the target machine actively refused it.
                self.conn.close_connection()

                # .. now, we can sleep a bit ..
                sleep(_sleep_time)
                now = utcnow()
            else:
                needs_connect = False
                self.is_connected = True

# ################################################################################################################################

    def _wait_until_flag_is_true(self, get_flag_func:'callable_', max_wait:'int'=Default.MaxWaitTime) -> 'bool':

        # .. wait for the connection for that much time ..
        now = utcnow()
        until = now + timedelta(seconds=max_wait)

        # .. wait and return if max. wait time is exceeded ..
        while not get_flag_func():
            sleep(0.1)
            now = utcnow()
            if now >= until:
                return True

        # If we are here, it means that we did not exceed the max_wait time
        return False

# ################################################################################################################################

    def run(self, max_wait:'int'=Default.MaxWaitTime) -> 'None':

        # Actually try to connect ..
        self._run(max_wait)

        def get_flag_func():
            return self.is_connected

        # .. wait and potentially return if max. wait time is exceeded ..
        has_exceeded = self._wait_until_flag_is_true(get_flag_func)
        if has_exceeded:
            return

        # .. otherwise, if we are here, it means that we are connected,
        # .. although we may be still not authenticated as the authentication step
        # .. is carried out by the on_connected_callback method.
        pass

# ################################################################################################################################

    def wait_until_authenticated(self, max_wait:'int'=Default.MaxWaitTime) -> 'bool':

        def get_flag_func():
            return self.is_authenticated

        # Wait until we are authenticated or until the max. wait_time is exceeded
        _ = self._wait_until_flag_is_true(get_flag_func)

        # Return the flag to the caller for it to decide what to do next
        return self.is_authenticated

# ################################################################################################################################

    def stop(self, reason:'str'='') -> 'None':
        self.keep_running = False
        self.conn.close(reason=reason)
        self.is_connected = False

# ################################################################################################################################

    def invoke(self, data:'any_', timeout:'int'=Default.ResponseWaitTime) -> 'any_':
        if self.needs_auth and (not self.is_authenticated):
            raise Exception('Client is not authenticated')

        request_id = MsgPrefix.InvokeService.format(new_cid())
        _ = spawn(self.send, request_id, ServiceInvocationRequest(request_id, data, self.config, self.auth_token))

        response = self._wait_for_response(request_id, wait_time=timeout)

        if not response:
            self.logger.warning('No response to invocation request `%s`', request_id)
        else:
            return response

# ################################################################################################################################

    def invoke_service(self, service_name:'str', request:'any_', timeout:'int'=Default.ResponseWaitTime) -> 'any_':
        return self.invoke({
            'service':service_name,
            'request': request
        }, timeout=timeout)

# ################################################################################################################################

    def subscribe(self, topic_name:'str') -> 'None':

        service_name = 'zato.pubsub.subscription.create-wsx-subscription'
        request = {
            'topic_name': topic_name
        }

        return self.invoke_service(service_name, request)

# ################################################################################################################################

    def publish(
        self,
        topic_name, # type: str
        data        # type: any_
    ) -> 'None':

        service_name = 'zato.pubsub.pubapi.publish-message'

        response = self.invoke_service(service_name, {
            'topic_name': topic_name,
            'data':data
        })

        response

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # First thing in the process
    from gevent import monkey
    _ = monkey.patch_all()

    # stdlib
    import logging
    import sys

    log_format = '%(asctime)s - %(levelname)s - %(name)s:%(lineno)d - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_format)

    _cli_logger = logging.getLogger('zato')

    def on_request_from_zato(msg:'RequestFromServer') -> 'any_':
        try:
            _cli_logger.info('*' * 80)
            _cli_logger.debug('Message from Zato received -> %s', msg.to_dict())
            return [elem['data'] for elem in msg.data]
        except Exception:
            return format_exc()

    def check_is_active_func():
        return True

    address = 'ws://127.0.0.1:47043/zato.wsx.apitests'
    client_id = '123456'
    client_name = 'My Client'
    on_request_callback = on_request_from_zato

    # Test topic to use
    topic_name1 = '/zato/demo/sample'

    config = Config()
    config.address = address
    config.client_id = client_id
    config.client_name = client_name
    config.on_request_callback = on_request_callback
    config.check_is_active_func = check_is_active_func
    config.username = 'user1'
    config.secret = 'secret1'

    # Create a client ..
    client = Client(config)

    # .. start it ..
    client.run()

    # .. wait until it is authenticated ..
    _ = client.wait_until_authenticated()

    # .. and run sample code now ..

    is_subscriber = 'sub' in sys.argv

    if is_subscriber:
        client.subscribe(topic_name1)
    else:
        idx = 0
        while idx < 100_000_000:
            idx += 1
            client.invoke({'service':'zato.ping'})
            client.publish(topic_name1, f'{idx}')
            # sleep(1)

    _cli_logger.info('Press Ctrl-C to quit')

    try:
        x = 0
        while x < 100_000_000 and client.keep_running:
            sleep(0.2)
    except KeyboardInterrupt:
        client.stop()


# ################################################################################################################################
# ################################################################################################################################
