# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import NO_CONTENT, TOO_MANY_REQUESTS
from json import dumps, loads
from logging import getLogger

# gevent
from gevent import sleep, spawn
from gevent.event import Event

# Requests
import requests

# websocket-client
from websocket import ABNF, create_connection

# Zato
from zato.common.api import Discord
from zato.common.const import SECRETS

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from gevent import Greenlet
    from websocket import WebSocket
    from zato.common.typing_ import anydictnone, anylistnone, stranydict, strstrdict

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_default = Discord.Default
_gateway = Discord.Gateway

_milliseconds_per_second = 1000

# The number of bytes at the start of a close frame's payload that hold the close code
_close_code_length = 2

# ################################################################################################################################
# ################################################################################################################################

class DiscordClient:
    """ Client for the Discord bot REST API, used to send messages to channels and people.
    A bot has to identify with the gateway once before it may create messages, which is what the handshake loop does.
    """
    def __init__(self, config:'stranydict') -> 'None':

        self.config = config
        self.name = config['name']

        # The bot token lives in the secret column, except when the connection
        # was imported with the token given directly in its definition.
        token = config.get('secret')
        if (not token) or token.startswith(SECRETS.Auto_Generated_Prefix):
            token = config['token']
        self.token = token

        self.address = config['address'].rstrip('/')
        self.timeout = config['timeout']
        self.default_channel_id = config['default_channel_id']

        # A single session shared by all the requests this client makes.
        self.session = requests.Session()
        self.session.headers['Authorization'] = f'Bot {self.token}'
        self.session.headers['User-Agent'] = _default.User_Agent

        # Set once the gateway has acknowledged the bot's IDENTIFY with READY, or once the client is stopped.
        self.ready = Event()

        # The last error of the handshake loop, reported to callers that time out while waiting for READY.
        self.last_error = ''

        # Why the client was stopped, reported to callers waiting for READY when the connection goes away.
        self.stop_reason = ''

        # The websocket of the handshake in progress, if there is one, and the greenlet that runs the loop.
        self.gateway_socket:'WebSocket | None' = None
        self.handshake_greenlet:'Greenlet | None' = None

        # Direct message channels already opened, keyed by the recipient's user ID.
        self.direct_channels:'strstrdict' = {}

# ################################################################################################################################

    def start_handshake(self) -> 'None':
        """ Starts the handshake loop in the background and returns immediately.
        """
        self.handshake_greenlet = spawn(self._handshake_loop)

# ################################################################################################################################

    def stop(self, reason:'str') -> 'None':
        """ Ends the handshake loop at once, closes its websocket and releases every caller waiting for READY.
        """
        self.stop_reason = reason

        # Kill the loop first so that it does not open a new websocket after the current one is closed ..
        if self.handshake_greenlet:
            self.handshake_greenlet.kill(block=False)
            self.handshake_greenlet = None

        # .. close the websocket of the attempt in progress ..
        if self.gateway_socket:
            self.gateway_socket.close(status=_gateway.Close_Normal)
            self.gateway_socket = None

        # .. and release the callers, who check the stop reason before they proceed.
        self.ready.set()

# ################################################################################################################################

    def _handshake_loop(self) -> 'None':
        """ Runs the gateway handshake until READY arrives, pausing between attempts.
        """
        # Every failure is retried, whatever its cause - the loop ends only with READY or when the client is stopped.
        while True:
            try:
                self._handshake()
            except Exception as e:
                self.last_error = str(e)
                logger.warning('Discord gateway handshake failed (%s) -> %s, retrying in %ss',
                    self.name, self.last_error, _default.Handshake_Pause)
                sleep(_default.Handshake_Pause)
            else:
                self.ready.set()
                logger.info('Discord gateway handshake OK (%s)', self.name)
                return

# ################################################################################################################################

    def _handshake(self) -> 'None':
        """ Performs one gateway handshake - HELLO, IDENTIFY and READY - and closes the websocket afterwards.
        """

        # Ask the REST API where the gateway is and how many IDENTIFY calls remain ..
        gateway_info = self._invoke_rest('GET', 'gateway/bot')
        session_start_limit = gateway_info['session_start_limit']

        logger.info('Discord gateway (%s) -> %s, IDENTIFY calls remaining: %s/%s',
            self.name, gateway_info['url'], session_start_limit['remaining'], session_start_limit['total'])

        # .. wait for the limit to reset if none remain ..
        if session_start_limit['remaining'] == 0:
            reset_after = session_start_limit['reset_after'] / _milliseconds_per_second
            logger.info('Discord IDENTIFY limit reached (%s), waiting %ss', self.name, reset_after)
            sleep(reset_after)

        # .. connect to the gateway ..
        gateway_url = gateway_info['url']
        url = f'{gateway_url}/?v={_default.Gateway_Version}&encoding={_default.Gateway_Encoding}'
        socket = create_connection(url, timeout=self.timeout)
        self.gateway_socket = socket

        try:
            # .. the gateway speaks first with HELLO ..
            hello = self._receive_gateway_message(socket)
            if hello['op'] != _gateway.Op_Hello:
                raise Exception(f'Discord gateway error ({self.name}) -> expected HELLO, received {hello}')

            # .. the bot identifies itself ..
            identify = {
                'op': _gateway.Op_Identify,
                'd': {
                    'token': self.token,
                    'intents': _default.Intents,
                    'properties': {
                        'os': 'zato',
                        'browser': 'zato',
                        'device': 'zato',
                    },
                },
            }
            socket.send(dumps(identify))

            # .. and waits for READY, which may follow other events.
            while True:
                message = self._receive_gateway_message(socket)
                if message['op'] == _gateway.Op_Dispatch:
                    if message['t'] == _gateway.Event_Ready:
                        break

            socket.close(status=_gateway.Close_Normal)

        finally:
            self.gateway_socket = None

# ################################################################################################################################

    def _receive_gateway_message(self, socket:'WebSocket') -> 'stranydict':
        """ Returns the next gateway message as a dict, or raises an exception with the close code
        and reason if the gateway closed the websocket instead.
        """
        opcode, data = socket.recv_data()

        if opcode == ABNF.OPCODE_CLOSE:
            code = int.from_bytes(data[:_close_code_length], 'big')
            reason = data[_close_code_length:].decode('utf8')
            raise Exception(f'Discord gateway closed ({self.name}) -> {code} {reason}')

        out = loads(data)
        return out

# ################################################################################################################################

    def _wait_until_ready(self) -> 'None':
        """ Blocks until the handshake has completed, or raises an exception if it has not within the timeout
        or if the connection was stopped in the meantime.
        """
        is_ready = self.ready.wait(self.timeout)

        if self.stop_reason:
            raise Exception(f'Discord connection ({self.name}) {self.stop_reason}')

        if not is_ready:
            raise Exception(f'Discord connection ({self.name}) not ready after {self.timeout}s -> {self.last_error}')

# ################################################################################################################################

    def _invoke_rest(
        self,
        http_method:'str',
        path:'str',
        data:'anydictnone'=None,
        files:'anylistnone'=None,
        ) -> 'stranydict':
        """ Invokes a REST endpoint without waiting for the handshake, retrying when rate-limited.
        """
        url = f'{self.address}/{path}'

        # Files are sent as multipart form data with the JSON payload in its own part,
        # otherwise the payload is the body of the request.
        if files:
            form_files = {}
            for index, item in enumerate(files):
                form_files[f'files[{index}]'] = item
            request_kwargs = {'data': {'payload_json': dumps(data)}, 'files': form_files}
        else:
            request_kwargs = {'json': data}

        # Invoke the endpoint, waiting out rate limits as long as the retry limit allows ..
        for _ in range(_default.Max_Rate_Limit_Retries + 1):
            response = self.session.request(http_method, url, timeout=self.timeout, **request_kwargs)

            if response.status_code == TOO_MANY_REQUESTS:
                body = response.json()
                retry_after = body['retry_after']
                logger.info('Discord rate limit (%s) -> %s %s, global: %s, retrying in %ss',
                    self.name, http_method, path, body['global'], retry_after)
                sleep(retry_after)
            else:
                break
        else:
            raise Exception(f'Discord error ({self.name}) -> {http_method} {path}: rate limit retries exhausted')

        # .. a response with no content is a success with nothing to parse ..
        if response.status_code == NO_CONTENT:
            return {}

        # .. anything else outside 2xx is an error that Discord describes in the body ..
        if not response.ok:
            try:
                body = response.json()
                error = f'{body["code"]} {body["message"]}'
            except ValueError:
                error = repr(response.text)
            raise Exception(f'Discord error ({self.name}) -> {http_method} {path}: {response.status_code} -> {error}')

        # .. and hand back the parsed response.
        out = response.json()
        return out

# ################################################################################################################################

    def invoke(
        self,
        http_method:'str',
        path:'str',
        data:'anydictnone'=None,
        files:'anylistnone'=None,
        ) -> 'stranydict':
        """ Invokes any REST endpoint of the Discord API, returning the parsed JSON response. Files, if given,
        are a list of (file name, content) tuples sent as multipart form data.
        """
        self._wait_until_ready()

        out = self._invoke_rest(http_method, path, data, files)
        return out

# ################################################################################################################################

    def send(
        self,
        content:'str',
        channel_id:'str'='',
        embeds:'anylistnone'=None,
        files:'anylistnone'=None,
        allowed_mentions:'anydictnone'=None,
        ) -> 'stranydict':
        """ Sends a message to a channel, or to the connection's default channel if none is given.
        Mentions in the content do not notify anyone unless allowed_mentions says otherwise.
        """
        if not channel_id:
            channel_id = self.default_channel_id

        if not channel_id:
            raise Exception(f'Discord error ({self.name}) -> no channel ID given and the connection has no default channel')

        if allowed_mentions is None:
            allowed_mentions = {'parse': []}

        data = {
            'content': content,
            'allowed_mentions': allowed_mentions,
        }

        # Embeds are optional - the content above is the message when they are not given.
        if embeds:
            data['embeds'] = embeds

        out = self.invoke('POST', f'channels/{channel_id}/messages', data, files)
        return out

# ################################################################################################################################

    def send_direct(
        self,
        user_id:'str',
        content:'str',
        embeds:'anylistnone'=None,
        files:'anylistnone'=None,
        ) -> 'stranydict':
        """ Sends a direct message to a person, opening the direct message channel first if this client has not yet.
        """
        if user_id not in self.direct_channels:
            response = self.invoke('POST', 'users/@me/channels', {'recipient_id': user_id})
            self.direct_channels[user_id] = response['id']

        channel_id = self.direct_channels[user_id]

        out = self.send(content, channel_id, embeds, files)
        return out

# ################################################################################################################################

    def ping(self) -> 'None':
        """ Confirms that the connection's token is valid and the handshake has completed.
        """
        response = self.invoke('GET', 'users/@me')

        logger.info('Discord ping OK (%s) -> %s', self.name, response['username'])

# ################################################################################################################################
# ################################################################################################################################
