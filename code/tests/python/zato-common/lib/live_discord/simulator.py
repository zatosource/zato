# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# A simulated Discord - the REST endpoints a bot uses to send messages and the gateway websocket
# a bot completes the HELLO, IDENTIFY and READY handshake with. Each fault a test needs is an attribute
# set on the simulator and cleared by reset.

# stdlib
import json
import socket
import threading
import time
from dataclasses import dataclass, field
from email.parser import BytesParser
from email.policy import HTTP
from http.client import FORBIDDEN, NOT_FOUND, OK, TOO_MANY_REQUESTS, UNAUTHORIZED
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from itertools import count
from typing import cast as cast_

# websockets
from websockets.exceptions import ConnectionClosed
from websockets.sync.server import serve

# Zato
from zato.common.api import Discord

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from websockets.sync.server import Server, ServerConnection
    from zato.common.typing_ import any_, anydict, anylist, intlist, strdict, strlist

# ################################################################################################################################
# ################################################################################################################################

_gateway = Discord.Gateway

# The address every simulator binds to
Host = '127.0.0.1'

# The environment variables the enmasse templates of the suites read the simulator's details from
Env_Address = 'Zato_Test_Discord_Address'
Env_Token = 'Zato_Test_Discord_Token'

# The bot the simulator answers GET /users/@me and READY with
Bot_User_ID = '100000000000000001'
Bot_Username = 'zato-test-bot'

# The channel each DM channel request opens, built from the recipient's ID
DM_Channel_Prefix = 'dm-'

# Discord's error codes and messages
Error_Code_Unauthorized = 0
Error_Code_Unknown_Channel = 10003
Error_Message_Unauthorized = '401: Unauthorized'
Error_Message_Unknown_Channel = 'Unknown Channel'
Error_Message_Rate_Limited = 'You are being rate limited.'
Error_Message_Forbidden_User_Agent = 'Access denied'

# The close code the gateway uses for a token it does not accept
Close_Code_Invalid_Token = 4004

# What the gateway sends in HELLO
Heartbeat_Interval = 41250

# ################################################################################################################################
# ################################################################################################################################

def find_free_port() -> 'int':
    """ Returns a TCP port that is free at the moment of the call.
    """
    with socket.socket() as probe:
        probe.bind((Host, 0))
        out = probe.getsockname()[1]

    return out

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class ReceivedMessage:
    """ One message a POST /channels/{id}/messages call delivered.
    """
    id: 'str'
    channel_id: 'str'
    content: 'str'
    embeds: 'anylist'
    allowed_mentions: 'anydict'
    files: 'list[ReceivedFile]'
    headers: 'strdict'
    is_multipart: 'bool'

# ################################################################################################################################

@dataclass
class ReceivedFile:
    """ One file part of a multipart message.
    """
    field_name: 'str'
    file_name: 'str'
    data: 'bytes'

# ################################################################################################################################

@dataclass
class Rejection:
    """ One request the REST part refused, with the reason it gave.
    """
    method: 'str'
    path: 'str'
    status: 'int'
    reason: 'str'

# ################################################################################################################################

@dataclass
class Identify:
    """ One IDENTIFY the gateway received.
    """
    token: 'str'
    intents: 'int'
    properties: 'anydict'
    close_code: 'int' = 0
    is_ready_sent: 'bool' = False
    received_at: 'float' = field(default_factory=time.monotonic)

# ################################################################################################################################
# ################################################################################################################################

class _RESTHandler(BaseHTTPRequestHandler):
    """ The HTTP part - the handler of each REST request, dispatching to the simulator the server belongs to.
    """
    server:'any_'

    def log_message(self, message_format:'str', *args:'object') -> 'None':
        pass

    def do_GET(self) -> 'None':
        self.server.simulator.handle_rest(self)

    def do_POST(self) -> 'None':
        self.server.simulator.handle_rest(self)

# ################################################################################################################################
# ################################################################################################################################

class DiscordSimulator:
    """ The REST API and the gateway of a simulated Discord, each on a port of its own, with the record of what
    each received and the faults a test configures.
    """

    def __init__(self, token:'str') -> 'None':

        self.token = token

        self.rest_port = find_free_port()
        self.gateway_port = find_free_port()

        # The address a connection is pointed at and the address GET /gateway/bot answers with
        self.address = f'http://{Host}:{self.rest_port}'
        self.gateway_url = f'ws://{Host}:{self.gateway_port}'

        # Every message accepted, in order of arrival
        self.messages:'list[ReceivedMessage]' = []

        # Every REST request refused
        self.rejections:'list[Rejection]' = []

        # Every IDENTIFY the gateway received
        self.identifies:'list[Identify]' = []

        # The number of gateway/bot calls answered
        self.gateway_info_calls = 0

        # The number of DM channel requests answered
        self.dm_channel_calls = 0

        # The close codes the gateway answers the next IDENTIFY calls with, one per call, in order.
        # An empty list means every IDENTIFY is answered with READY.
        self.identify_close_codes:'intlist' = []

        # How long the gateway waits after IDENTIFY before it sends READY, in seconds
        self.ready_delay = 0.0

        # When set, the gateway accepts IDENTIFY and never sends READY, leaving the websocket open
        self.never_send_ready = False

        # The number of REST calls answered with 429 before the simulator accepts them again,
        # and the retry_after each such response reports, in seconds
        self.rate_limited_calls_left = 0
        self.rate_limit_retry_after = 0.2

        # Channels a message to which is answered with 404 Unknown Channel
        self.unknown_channels:'strlist' = []

        # What GET /gateway/bot reports under session_start_limit
        self.session_start_remaining = 1000
        self.session_start_reset_after_ms = 100

        self._message_ids = count(900000000000000001)
        self._lock = threading.Lock()

        self._rest_server:'any_' = None
        self._rest_thread:'threading.Thread | None' = None
        self._gateway_server:'Server | None' = None
        self._gateway_thread:'threading.Thread | None' = None

# ################################################################################################################################

    def start(self) -> 'None':
        """ Starts the REST server and the gateway on their ports. The ports are unchanged across a stop and a start.
        """
        rest_server = cast_('any_', ThreadingHTTPServer((Host, self.rest_port), _RESTHandler))
        rest_server.simulator = self
        self._rest_server = rest_server

        self._rest_thread = threading.Thread(target=rest_server.serve_forever, daemon=True)
        self._rest_thread.start()

        gateway_server = serve(self._handle_gateway_connection, Host, self.gateway_port)
        self._gateway_server = gateway_server

        self._gateway_thread = threading.Thread(target=gateway_server.serve_forever, daemon=True)
        self._gateway_thread.start()

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Stops both servers.
        """
        if self._gateway_server is not None:
            self._gateway_server.shutdown()
            self._gateway_server = None

        if self._rest_server is not None:
            self._rest_server.shutdown()
            self._rest_server.server_close()
            self._rest_server = None

# ################################################################################################################################

    def reset(self) -> 'None':
        """ Clears every record and every fault. The token and the ports are kept.
        """
        with self._lock:
            self.messages.clear()
            self.rejections.clear()
            self.identifies.clear()
            self.gateway_info_calls = 0
            self.dm_channel_calls = 0
            self.identify_close_codes.clear()
            self.ready_delay = 0.0
            self.never_send_ready = False
            self.rate_limited_calls_left = 0
            self.rate_limit_retry_after = 0.2
            self.unknown_channels.clear()
            self.session_start_remaining = 1000
            self.session_start_reset_after_ms = 100

# ################################################################################################################################

    def environment(self) -> 'strdict':
        """ The variables an enmasse template reads the simulator's address and token from.
        """
        out = {
            Env_Address: self.address,
            Env_Token: self.token,
        }
        return out

# ################################################################################################################################

    def wait_for_identifies(self, min_count:'int', timeout:'float') -> 'list[Identify]':
        """ Waits until the gateway has received at least that many IDENTIFY calls.
        """
        deadline = time.monotonic() + timeout

        while True:
            with self._lock:
                out = list(self.identifies)

            if len(out) >= min_count:
                return out

            if time.monotonic() > deadline:
                raise AssertionError(f'Expected {min_count} IDENTIFY call(s) within {timeout}s, the gateway has {len(out)}')

            time.sleep(0.05)

# ################################################################################################################################

    def wait_for_messages(self, min_count:'int', timeout:'float') -> 'list[ReceivedMessage]':
        """ Waits until the REST part has received at least that many messages.
        """
        deadline = time.monotonic() + timeout

        while True:
            with self._lock:
                out = list(self.messages)

            if len(out) >= min_count:
                return out

            if time.monotonic() > deadline:
                raise AssertionError(f'Expected {min_count} message(s) within {timeout}s, the simulator has {len(out)}')

            time.sleep(0.05)

# ################################################################################################################################
# ################################################################################################################################

    def handle_rest(self, handler:'_RESTHandler') -> 'None':
        """ Answers one REST request - validates the headers, applies the faults and dispatches on the path.
        """
        method = handler.command
        path = handler.path

        # Every call carries the bot token ..
        authorization = handler.headers.get('Authorization', '')
        if authorization != f'Bot {self.token}':
            self._reject(handler, method, path, UNAUTHORIZED, {
                'message': Error_Message_Unauthorized,
                'code': Error_Code_Unauthorized,
            })
            return

        # .. and identifies the library it comes from.
        user_agent = handler.headers.get('User-Agent', '')
        if not user_agent.startswith('DiscordBot'):
            self._reject(handler, method, path, FORBIDDEN, {
                'message': Error_Message_Forbidden_User_Agent,
            })
            return

        # A rate limit applies to each call until the configured number of them has been refused
        with self._lock:
            is_rate_limited = self.rate_limited_calls_left > 0
            if is_rate_limited:
                self.rate_limited_calls_left -= 1

        if is_rate_limited:
            self._reject(handler, method, path, TOO_MANY_REQUESTS, {
                'message': Error_Message_Rate_Limited,
                'retry_after': self.rate_limit_retry_after,
                'global': False,
            }, {'Retry-After': str(self.rate_limit_retry_after)})
            return

        if method == 'GET' and path == '/gateway/bot':
            self._handle_gateway_info(handler)

        elif method == 'GET' and path == '/users/@me':
            self._send_json(handler, OK, {
                'id': Bot_User_ID,
                'username': Bot_Username,
                'bot': True,
            })

        elif method == 'POST' and path == '/users/@me/channels':
            self._handle_dm_channel(handler)

        elif method == 'POST' and path.startswith('/channels/') and path.endswith('/messages'):
            channel_id = path[len('/channels/'):-len('/messages')]
            self._handle_message(handler, channel_id)

        else:
            self._reject(handler, method, path, NOT_FOUND, {
                'message': '404: Not Found',
                'code': 0,
            })

# ################################################################################################################################

    def _handle_gateway_info(self, handler:'_RESTHandler') -> 'None':

        with self._lock:
            self.gateway_info_calls += 1

        self._send_json(handler, OK, {
            'url': self.gateway_url,
            'shards': 1,
            'session_start_limit': {
                'total': 1000,
                'remaining': self.session_start_remaining,
                'reset_after': self.session_start_reset_after_ms,
                'max_concurrency': 1,
            },
        })

# ################################################################################################################################

    def _handle_dm_channel(self, handler:'_RESTHandler') -> 'None':

        data = self._read_json(handler)
        recipient_id = data['recipient_id']

        with self._lock:
            self.dm_channel_calls += 1

        self._send_json(handler, OK, {
            'id': DM_Channel_Prefix + recipient_id,
            'type': 1,
            'recipients': [{'id': recipient_id}],
        })

# ################################################################################################################################

    def _handle_message(self, handler:'_RESTHandler', channel_id:'str') -> 'None':

        if channel_id in self.unknown_channels:
            self._reject(handler, 'POST', handler.path, NOT_FOUND, {
                'message': Error_Message_Unknown_Channel,
                'code': Error_Code_Unknown_Channel,
            })
            return

        content_type = handler.headers.get('Content-Type', '')
        body = self._read_body(handler)

        # A message with files arrives as multipart form data with its JSON payload in a part of its own ..
        if content_type.startswith('multipart/form-data'):
            is_multipart = True
            data, files = self._parse_multipart(content_type, body)

        # .. and one without files is the JSON body itself.
        else:
            is_multipart = False
            data = json.loads(body)
            files = []

        message_id = str(next(self._message_ids))

        message = ReceivedMessage(
            id=message_id,
            channel_id=channel_id,
            content=data.get('content', ''),
            embeds=data.get('embeds', []),
            allowed_mentions=data.get('allowed_mentions', {}),
            files=files,
            headers=dict(handler.headers),
            is_multipart=is_multipart,
        )

        with self._lock:
            self.messages.append(message)

        self._send_json(handler, OK, {
            'id': message_id,
            'channel_id': channel_id,
            'content': message.content,
            'embeds': message.embeds,
        })

# ################################################################################################################################

    def _parse_multipart(self, content_type:'str', body:'bytes') -> 'tuple[anydict, list[ReceivedFile]]':
        """ Splits a multipart body into the JSON payload and the files.
        """
        raw = b'Content-Type: ' + content_type.encode('utf8') + b'\r\n\r\n' + body
        parsed = BytesParser(policy=HTTP).parsebytes(raw)

        data:'anydict' = {}
        files:'list[ReceivedFile]' = []

        for part in parsed.iter_parts():
            field_name = part.get_param('name', header='content-disposition')
            file_name = part.get_param('filename', header='content-disposition')
            payload = cast_('bytes', part.get_payload(decode=True))

            if field_name == 'payload_json':
                data = json.loads(payload)
            else:
                files.append(ReceivedFile(str(field_name), str(file_name), payload))

        return data, files

# ################################################################################################################################

    def _read_body(self, handler:'_RESTHandler') -> 'bytes':
        content_length = int(handler.headers.get('Content-Length', 0))
        out = handler.rfile.read(content_length)
        return out

# ################################################################################################################################

    def _read_json(self, handler:'_RESTHandler') -> 'anydict':
        body = self._read_body(handler)
        out = json.loads(body)
        return out

# ################################################################################################################################

    def _reject(
        self,
        handler:'_RESTHandler',
        method:'str',
        path:'str',
        status:'int',
        data:'anydict',
        headers:'strdict | None'=None,
        ) -> 'None':

        with self._lock:
            self.rejections.append(Rejection(method, path, status, data['message']))

        self._send_json(handler, status, data, headers)

# ################################################################################################################################

    def _send_json(self, handler:'_RESTHandler', status:'int', data:'anydict', headers:'strdict | None'=None) -> 'None':

        body = json.dumps(data).encode('utf8')

        handler.send_response(status)
        handler.send_header('Content-Type', 'application/json')
        handler.send_header('Content-Length', str(len(body)))

        if headers:
            for name, value in headers.items():
                handler.send_header(name, value)

        handler.end_headers()
        _ = handler.wfile.write(body)

# ################################################################################################################################
# ################################################################################################################################

    def _handle_gateway_connection(self, connection:'ServerConnection') -> 'None':
        """ Runs one gateway session - HELLO, IDENTIFY and READY, or a close code, with the configured faults.
        """
        try:
            self._run_gateway_session(connection)
        except ConnectionClosed:
            pass

# ################################################################################################################################

    def _run_gateway_session(self, connection:'ServerConnection') -> 'None':

        # The gateway speaks first ..
        connection.send(json.dumps({
            'op': _gateway.Op_Hello,
            'd': {'heartbeat_interval': Heartbeat_Interval},
        }))

        # .. and the bot identifies itself.
        message = json.loads(connection.recv())

        if message['op'] != _gateway.Op_Identify:
            connection.close(Close_Code_Invalid_Token, 'Expected IDENTIFY')
            return

        data = message['d']
        identify = Identify(data['token'], data['intents'], data['properties'])

        with self._lock:
            self.identifies.append(identify)
            if self.identify_close_codes:
                close_code = self.identify_close_codes.pop(0)
            else:
                close_code = 0

        # A token the gateway does not know is refused with 4004, whatever the configured faults
        if identify.token != self.token:
            close_code = Close_Code_Invalid_Token

        # A configured close code ends the session in place of READY
        if close_code:
            identify.close_code = close_code
            connection.close(close_code, 'Simulated close')
            return

        # A session configured to leave the bot waiting keeps the websocket open until the bot closes it
        if self.never_send_ready:
            while True:
                _ = connection.recv()

        if self.ready_delay:
            time.sleep(self.ready_delay)

        connection.send(json.dumps({
            'op': _gateway.Op_Dispatch,
            't': _gateway.Event_Ready,
            's': 1,
            'd': {
                'v': Discord.Default.Gateway_Version,
                'user': {'id': Bot_User_ID, 'username': Bot_Username, 'bot': True},
                'session_id': 'simulated-session',
                'resume_gateway_url': self.gateway_url,
                'guilds': [],
            },
        }))
        identify.is_ready_sent = True

        # The bot closes the websocket once it has READY
        while True:
            _ = connection.recv()

# ################################################################################################################################
# ################################################################################################################################
