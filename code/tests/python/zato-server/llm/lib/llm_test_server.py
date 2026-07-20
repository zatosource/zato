# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
import threading
import time
from http.client import OK
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, stranydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# The replies the server produces when a test did not configure its own
Default_Reply_OpenAI = 'Hello from OpenAI'
Default_Reply_Claude = 'Hello from Claude'
Default_Reply_Gemini = 'Hello from Gemini'

# The token usage every default response reports
Input_Tokens  = 12
Output_Tokens = 7

# ################################################################################################################################
# ################################################################################################################################

class _Handler(BaseHTTPRequestHandler):
    """ Parses each incoming request, records it, and answers according to the per-path configuration
    the test set up - canned provider responses, configured reply texts, error statuses and delays.
    """

    protocol_version = 'HTTP/1.1'

    def _read_body(self) -> 'bytes':
        if 'Content-Length' in self.headers:
            length = int(self.headers['Content-Length'])
            out = self.rfile.read(length)
        else:
            out = b''
        return out

# ################################################################################################################################

    def _record(self, raw_body:'bytes') -> 'stranydict':
        """ Parses one request into a record tests can assert on - the raw bytes, headers and the parsed JSON body.
        """
        record:'stranydict' = {
            'path': self.path,
            'method': self.command,
            'headers': dict(self.headers.items()),
            'raw_body': raw_body,
            'body': None,
        }

        # A body that is not JSON is recorded as-is, which is enough for the ping paths.
        if raw_body:
            try:
                record['body'] = json.loads(raw_body)
            except ValueError:
                pass

        return record

# ################################################################################################################################

    def _handle(self) -> 'None':

        server:'any_' = self.server

        raw_body = self._read_body()
        record = self._record(raw_body)

        server.recorded_requests.append(record)
        server.last_request = record

        config = server.path_config.get(self.path, {})

        status, body = server.build_response(record, config)
        self._send(status, body)

# ################################################################################################################################

    def _send(self, status:'int', body:'anydict') -> 'None':

        serialized = json.dumps(body).encode('utf-8')

        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(serialized)))
        self.end_headers()

        _ = self.wfile.write(serialized)

# ################################################################################################################################

    do_GET  = _handle
    do_POST = _handle

# ################################################################################################################################

    def log_message(self, format:'str', *args:'any_') -> 'None':
        logger.info('[llm_test_server] %s', format % args)

# ################################################################################################################################
# ################################################################################################################################

class _Server(ThreadingHTTPServer):
    """ A threading HTTP server holding the recorded requests and per-path response configuration,
    plus the response-building logic every scenario shares.
    """
    daemon_threads = True

    def __init__(self, *args:'any_', **kwargs:'any_') -> 'None':
        super().__init__(*args, **kwargs)

        self.recorded_requests:'anylist' = []
        self.last_request:'anydict | None' = None
        self.path_config:'anydict' = {}

# ################################################################################################################################

    def build_response(self, record:'stranydict', config:'stranydict') -> 'any_':
        """ Builds the response for one request from its per-path configuration.
        """

        # An optional delay simulates a slow provider for timeout tests.
        if delay := config.get('delay'):
            time.sleep(delay)

        # A path may answer with a prepared status and body - the way error scenarios
        # and in-band errors such as Gemini's blocked prompts are set up.
        if raw := config.get('respond_raw'):
            status, body = raw
            out = (status, body)
            return out

        path = record['path']

        # The OpenAI chat completions endpoint
        if path.endswith('/chat/completions'):
            out = (OK, self._openai_response(record, config))
            return out

        # The Claude messages endpoint
        if path.endswith('/messages'):
            out = (OK, self._claude_response(record, config))
            return out

        # The Gemini generate-content endpoint
        if ':generateContent' in path:
            out = (OK, self._gemini_response(config))
            return out

        # Everything else, including the model-listing ping paths, gets an empty list body.
        out = (OK, {'object': 'list', 'data': [], 'models': []})
        return out

# ################################################################################################################################

    def _openai_response(self, record:'stranydict', config:'stranydict') -> 'anydict':

        reply_text = config.get('reply_text', Default_Reply_OpenAI)
        model = record['body']['model']

        out = {
            'id': 'chatcmpl-test-1',
            'object': 'chat.completion',
            'created': 1700000000,
            'model': model,
            'choices': [{
                'index': 0,
                'message': {'role': 'assistant', 'content': reply_text},
                'finish_reason': 'stop',
            }],
            'usage': {
                'prompt_tokens': Input_Tokens,
                'completion_tokens': Output_Tokens,
                'total_tokens': Input_Tokens + Output_Tokens,
            },
        }
        return out

# ################################################################################################################################

    def _claude_response(self, record:'stranydict', config:'stranydict') -> 'anydict':

        reply_text = config.get('reply_text', Default_Reply_Claude)
        model = record['body']['model']

        out = {
            'id': 'msg_test_1',
            'type': 'message',
            'role': 'assistant',
            'model': model,
            'content': [{'type': 'text', 'text': reply_text}],
            'stop_reason': 'end_turn',
            'usage': {
                'input_tokens': Input_Tokens,
                'output_tokens': Output_Tokens,
            },
        }
        return out

# ################################################################################################################################

    def _gemini_response(self, config:'stranydict') -> 'anydict':

        reply_text = config.get('reply_text', Default_Reply_Gemini)

        out = {
            'candidates': [{
                'content': {'role': 'model', 'parts': [{'text': reply_text}]},
                'finishReason': 'STOP',
            }],
            'usageMetadata': {
                'promptTokenCount': Input_Tokens,
                'candidatesTokenCount': Output_Tokens,
                'totalTokenCount': Input_Tokens + Output_Tokens,
            },
        }
        return out

# ################################################################################################################################
# ################################################################################################################################

class LLMTestServer:
    """ A live LLM provider simulator for client tests. It records every request and answers per-path
    with canned OpenAI, Claude and Gemini responses over plain HTTP.
    """
    def __init__(self) -> 'None':
        self.host = '127.0.0.1'
        self.port = 0

        self._httpd:'any_' = None
        self._thread:'any_' = None

# ################################################################################################################################

    def start(self) -> 'None':
        """ Binds to an ephemeral port and serves in a background thread.
        """
        self._httpd = _Server((self.host, 0), _Handler)
        self.port = self._httpd.server_address[1]

        self._thread = threading.Thread(target=self._httpd.serve_forever, daemon=True)
        self._thread.start()

        logger.info('[LLMTestServer] started on %s', self.address)

# ################################################################################################################################

    def stop(self) -> 'None':
        self._httpd.shutdown()
        self._httpd.server_close()

        logger.info('[LLMTestServer] stopped on %s', self.address)

# ################################################################################################################################

    @property
    def address(self) -> 'str':
        out = f'http://{self.host}:{self.port}'
        return out

# ################################################################################################################################

    def url(self, path:'str') -> 'str':
        """ Returns the full URL of a path on this server.
        """
        out = f'{self.address}{path}'
        return out

# ################################################################################################################################

    def configure(self, path:'str', **config:'any_') -> 'None':
        """ Sets the per-path response configuration - reply_text, respond_raw, delay.
        """
        self._httpd.path_config[path] = config

# ################################################################################################################################

    @property
    def last_request(self) -> 'anydict':
        out = self._httpd.last_request
        return out

# ################################################################################################################################

    @property
    def recorded_requests(self) -> 'anylist':
        out = self._httpd.recorded_requests
        return out

# ################################################################################################################################

    def clear_requests(self) -> 'None':
        self._httpd.recorded_requests.clear()
        self._httpd.last_request = None
        self._httpd.path_config.clear()

# ################################################################################################################################
# ################################################################################################################################
