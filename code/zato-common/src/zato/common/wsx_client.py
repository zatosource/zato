# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

"""
Copyright (C) 2019 Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import subprocess
from datetime import datetime, timedelta
from traceback import format_exc
from uuid import uuid4

# gevent
from gevent import sleep, spawn

# six
from six import binary_type
from six.moves.http_client import OK

# ws4py
from ws4py.client.geventclient import WebSocketClient

# Zato
from zato.common.json_ import dumps
from zato.common.json_internal import loads

# ################################################################################################################################

logger = logging.getLogger('zato.wsx_client')

# ################################################################################################################################

class MSG_PREFIX:
    _COMMON = 'zato.ws.client.{}'
    INVOKE_SERVICE = _COMMON.format('invs.{}')
    SEND_AUTH = _COMMON.format('auth.{}')
    SEND_RESP = _COMMON.format('resp.{}')

# ################################################################################################################################

zato_keep_alive_ping = 'zato-keep-alive-ping'
_invalid = '_invalid.' + uuid4().hex

# ################################################################################################################################

class Config(object):
    def __init__(self, client_name=None, client_id=None, address=None, username=None, secret=None, on_request_callback=None,
                 wait_time=5):
        self.client_name = client_name
        self.client_id = client_id
        self.address = address
        self.username = username
        self.secret = secret
        self.on_request_callback = on_request_callback
        self.wait_time = wait_time
        self.needs_auth = bool(self.username)

# ################################################################################################################################

class MessageToZato(object):
    """ An individual message from a WebSocket client to Zato, either request or response to a previous request from Zato.
    """
    action = _invalid

    def __init__(self, msg_id, config, token=None):
        self.config = config
        self.msg_id = msg_id
        self.token = token

    def serialize(self, _now=datetime.utcnow):
        return dumps(self.enrich({
            'data': {},
            'meta': {
                'action': self.action,
                'id': self.msg_id,
                'timestamp': _now().isoformat(),
                'token': self.token,
                'client_id': self.config.client_id,
                'client_name': self.config.client_name,
            }
        }))

    def enrich(self, msg):
        """ Implemented by subclasses that need to add extra information.
        """
        return msg

# ################################################################################################################################

class AuthRequest(MessageToZato):
    """ Logs a client into a WebSocket connection.
    """
    action = 'create-session'

    def enrich(self, msg):
        msg['meta']['username'] = self.config.username
        msg['meta']['secret'] = self.config.secret
        return msg

# ################################################################################################################################

class ServiceInvokeRequest(MessageToZato):
    """ Encapsulates information about an invocation of a Zato service.
    """
    action = 'invoke-service'

    def __init__(self, request_id, data, *args, **kwargs):
        self.data = data
        super(ServiceInvokeRequest, self).__init__(request_id, *args, **kwargs)

    def enrich(self, msg):
        msg['data'].update(self.data)
        return msg

# ################################################################################################################################

class ResponseFromZato(object):
    """ A response from Zato to a previous request by this client.
    """
    __slots__ = ('id', 'timestamp', 'in_reply_to', 'status', 'is_ok', 'data', 'msg_impl')

    def __init__(self):
        self.id = None
        self.timestamp = None
        self.in_reply_to = None
        self.status = None
        self.is_ok = None
        self.data = None
        self.msg_impl = None

    @staticmethod
    def from_json(msg):
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

class RequestFromZato(object):
    """ A request from Zato to this client.
    """
    __slots__ = ('id', 'timestamp', 'data', 'msg_impl')

    def __init__(self):
        self.id = None
        self.timestamp = None
        self.data = None
        self.msg_impl = None

    @staticmethod
    def from_json(msg):
        request = RequestFromZato()
        request.msg_impl = msg
        request.id = msg['meta']['id']
        request.timestamp = msg['meta']['timestamp']
        request.data = msg['data']

        return request

# ################################################################################################################################

class ResponseToZato(MessageToZato):
    """ A response from this client to a previous request from Zato.
    """
    action = 'client-response'

    def __init__(self, in_reply_to, data, *args, **kwargs):
        self.in_reply_to = in_reply_to
        self.data = data
        super(ResponseToZato, self).__init__(*args, **kwargs)

    def enrich(self, msg):
        msg['meta']['in_reply_to'] = self.in_reply_to
        msg['data']['response'] = self.data
        return msg

# ################################################################################################################################

class _WSClient(WebSocketClient):
    """ A low-level subclass of around ws4py's WebSocket client functionality.
    """
    def __init__(self, on_connected_callback, on_message_callback, on_error_callback, on_closed_callback, *args, **kwargs):
        self.on_connected_callback = on_connected_callback
        self.on_message_callback = on_message_callback
        self.on_error_callback = on_error_callback
        self.on_closed_callback = on_closed_callback
        super(_WSClient, self).__init__(*args, **kwargs)

    def opened(self):
        spawn(self.on_connected_callback)

    def received_message(self, msg):
        self.on_message_callback(msg)

    def unhandled_error(self, error):
        spawn(self.on_error_callback, error)

    def closed(self, code, reason=None):
        super(_WSClient, self).closed(code, reason)
        self.on_closed_callback(code, reason)

# ################################################################################################################################

class Client(object):
    """ A WebSocket client that knows how to invoke Zato services.
    """
    def __init__(self, config):
        # type: (Config)
        self.config = config
        self.conn = _WSClient(self.on_connected, self.on_message, self.on_error, self.on_closed, self.config.address)
        self.keep_running = True
        self.is_authenticated = False
        self.is_connected = False
        self.is_auth_needed = bool(self.config.username)
        self.auth_token = None
        self.on_request_callback = self.config.on_request_callback
        self.on_closed_callback = self.config.on_closed_callback
        self.needs_auth = self.config.needs_auth

        # Keyed by IDs of requests sent from this client to Zato
        self.requests_sent = {}

        # Same key as self.requests_sent but the dictionary contains responses to previously sent requests
        self.responses_received = {}

        # Requests initiated by Zato, keyed by their IDs
        self.requests_received = {}

# ################################################################################################################################

    def send(self, msg_id, msg, wait_time=2):
        """ Spawns a greenlet to send a message to Zato.
        """
        spawn(self._send, msg_id, msg, msg.serialize(), wait_time)

# ################################################################################################################################

    def _send(self, msg_id, msg, serialized, wait_time):
        """ Sends a request to Zato and waits up to wait_time or self.config.wait_time seconds for a reply.
        """
        logger.info('Sending msg `%s`', serialized)

        # So that it can be correlated with a future response
        self.requests_sent[msg_id] = msg

        # Actually send the messageas string now
        self.conn.send(serialized)

# ################################################################################################################################

    def _wait_for_response(self, request_id, wait_time=None, _now=datetime.utcnow, _delta=timedelta, _sleep=sleep):
        """ Wait until a response arrives and return it
        or return None if there is no response up to wait_time or self.config.wait_time.
        """
        now = _now()
        until = now + _delta(seconds=wait_time or self.config.wait_time)

        while now < until:

            response = self.responses_received.get(request_id)
            if response:
                return response
            else:
                _sleep(0.01)
                now = _now()

# ################################################################################################################################

    def authenticate(self, request_id):
        """ Authenticates the client with Zato.
        """
        logger.info('Authenticating as `%s` (%s %s)', self.config.username, self.config.client_name, self.config.client_id)
        spawn(self.send, request_id, AuthRequest(request_id, self.config, self.auth_token))

# ################################################################################################################################

    def on_connected(self):
        """ Invoked upon establishing an initial connection - logs the client in with self.config's credentials
        """
        logger.info('Connected to `%s` %s (%s %s)',
            self.config.address,
            'as `{}`'.format(self.config.username) if self.config.username else 'without credentials',
            self.config.client_name, self.config.client_id)

        request_id = MSG_PREFIX.SEND_AUTH.format(uuid4().hex)
        self.authenticate(request_id)

        response = self._wait_for_response(request_id)

        if not response:
            logger.warn('No response to authentication request `%s`', request_id)
        else:
            self.auth_token = response.data['token']
            self.is_authenticated = True
            del self.responses_received[request_id]

            logger.info('Authenticated successfully as `%s` (%s %s)',
                self.config.username, self.config.client_name, self.config.client_id)

# ################################################################################################################################

    def on_message(self, msg, _uuid4=uuid4):
        """ Invoked for each message received from Zato, both for responses to previous requests and for incoming requests.
        """
        _msg = loads(msg.data.decode('utf-8') if isinstance(msg.data, binary_type) else msg.data)
        logger.info('Received message `%s`', _msg)

        in_reply_to = _msg['meta'].get('in_reply_to')

        # Reply from Zato to one of our requests
        if in_reply_to:
            self.responses_received[in_reply_to] = ResponseFromZato.from_json(_msg)

        # Request from Zato
        else:
            data = self.on_request_callback(RequestFromZato.from_json(_msg))
            response_id = MSG_PREFIX.SEND_RESP.format(_uuid4().hex)
            self.send(response_id, ResponseToZato(_msg['meta']['id'], data, response_id, self.config, self.auth_token))

# ################################################################################################################################

    def on_closed(self, code, reason=None):
        logger.info('Closed WSX client connection to `%s` (remote code:%s reason:%s)', self.config.address, code, reason)
        if self.on_closed_callback:
            self.on_closed_callback(code, reason)

# ################################################################################################################################

    def on_error(self, error):
        """ Invoked for each unhandled error in the lower-level ws4py library.
        """
        logger.warn('Caught error %s', error)

# ################################################################################################################################

    def _run(self, max_wait=10, _sleep_time=2):

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
                    log_func = logger.warn
                else:
                    if now >= warn_from:
                        log_func = logger.warn
                        use_warn = True
                    else:
                        log_func = logger.debug

                log_func('Exception caught `%s` while connecting to WSX `%s (%s)`', e, self.config.address, format_exc())
                sleep(_sleep_time)
                now = datetime.utcnow()
            else:
                needs_connect = False
                self.is_connected = True

# ################################################################################################################################

    def run(self, max_wait=20):
        self._run()

        now = datetime.utcnow()
        until = now + timedelta(seconds=max_wait)

        while not self.is_connected:
            sleep(0.01)
            now = datetime.utcnow()
            if now >= until:
                return

# ################################################################################################################################

    def stop(self, reason=''):
        self.keep_running = False
        self.conn.close(reason=reason)
        self.is_connected = False

# ################################################################################################################################

    def invoke(self, request, timeout=5):
        if self.needs_auth and (not self.is_authenticated):
            raise Exception('Client is not authenticated')

        request_id = MSG_PREFIX.INVOKE_SERVICE.format(uuid4().hex)
        spawn(self.send, request_id, ServiceInvokeRequest(request_id, request, self.config, self.auth_token))

        response = self._wait_for_response(request_id, wait_time=timeout)

        if not response:
            logger.warn('No response to invocation request `%s`', request_id)
        else:
            return response

# ################################################################################################################################

if __name__ == '__main__':

    def on_request_from_zato(msg):
        try:
            return subprocess.check_output(msg.data['cmd'])
        except Exception as e:
            return format_exc(e)

    config = Config()

    config.client_name = 'My Client'
    config.client_id = '32351b3f5d16'
    address = 'ws://127.0.0.1:47043/zato.ws.apitests'

    config.address = address
    config.username = 'user1'
    config.secret = 'secret1'
    config.on_request_callback = on_request_from_zato

    client = Client(config)
    client.run()
    client.invoke({'service':'zato.ping'})

    logger.info('Press Ctrl-C to quit')

    try:
        x = 0
        while x < 1000 and client.keep_running:
            sleep(0.2)
    except KeyboardInterrupt:
        client.stop()

# ################################################################################################################################
