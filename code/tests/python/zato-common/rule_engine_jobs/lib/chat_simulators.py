# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import socket
import threading
from http.client import OK
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, dictlist, strlist, strnone

# ################################################################################################################################
# ################################################################################################################################

def find_free_port() -> 'int':
    """ Returns a TCP port that is free right now.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(('127.0.0.1', 0))
        _, port = sock.getsockname()

    return port

# ################################################################################################################################
# ################################################################################################################################

class SlackTestHandler(BaseHTTPRequestHandler):
    """ A local Slack Web API - chat.postMessage, auth.test and conversations.list over plain HTTP.
    """

    # The bot token this workspace accepts
    expected_token:'strnone' = None

    # Every chat.postMessage payload received so far
    messages:'dictlist' = []

    # What conversations.list answers with
    channel_names:'strlist' = []

    # Channels that report channel_not_found, for the failure-path tests
    broken_channels:'strlist' = []

    def log_message(self, format:'str', *args:'any_') -> 'None':
        pass

# ################################################################################################################################

    def _send_json(self, status:'int', data:'anydict') -> 'None':
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        body = json.dumps(data)
        _ = self.wfile.write(body.encode('utf-8'))

# ################################################################################################################################

    def _read_json(self) -> 'anydict':
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)

        # Methods like auth.test arrive with no body at all.
        if body:
            out = json.loads(body)
        else:
            out = {}

        return out

# ################################################################################################################################

    def do_POST(self) -> 'None':

        # Every method call carries the bot token ..
        auth_header = self.headers.get('Authorization', '')
        expected_header = f'Bearer {self.expected_token}'

        if auth_header != expected_header:
            self._send_json(OK, {'ok': False, 'error': 'invalid_auth'})
            return

        # .. and dispatches on the method name in the path.
        if self.path == '/chat.postMessage':
            data = self._read_json()
            channel = data['channel']

            # A channel configured as broken reports the same error the real API would.
            if channel in self.broken_channels:
                self._send_json(OK, {'ok': False, 'error': 'channel_not_found'})
                return

            SlackTestHandler.messages.append(data)
            self._send_json(OK, {'ok': True, 'channel': channel})
            return

        if self.path == '/auth.test':
            self._send_json(OK, {'ok': True, 'team': 'Test Workspace'})
            return

        if self.path == '/conversations.list':
            channels = []
            for name in self.channel_names:
                channels.append({'name': name})

            self._send_json(OK, {'ok': True, 'channels': channels})
            return

        self._send_json(OK, {'ok': False, 'error': 'unknown_method'})

# ################################################################################################################################
# ################################################################################################################################

def start_slack_server(port:'int', token:'str', channel_names:'strlist') -> 'ThreadingHTTPServer':
    """ Starts the simulated Slack Web API in a background thread, over plain HTTP.
    """
    SlackTestHandler.expected_token = token
    SlackTestHandler.messages = []
    SlackTestHandler.channel_names = channel_names
    SlackTestHandler.broken_channels = []

    out = ThreadingHTTPServer(('127.0.0.1', port), SlackTestHandler)

    thread = threading.Thread(target=out.serve_forever, daemon=True)
    thread.start()

    return out

# ################################################################################################################################
# ################################################################################################################################
