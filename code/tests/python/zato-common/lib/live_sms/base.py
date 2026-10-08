# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import threading
import time
from base64 import b64encode
from dataclasses import dataclass, field
from datetime import datetime, timezone
from http.client import BAD_REQUEST, NOT_FOUND, OK, SERVICE_UNAVAILABLE
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from json import dumps, loads
from typing import NamedTuple
from urllib.parse import parse_qsl, urlencode, urlsplit

# requests
import requests

# Zato
from live_sms.ports import find_free_port, Host
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, strdict, stranydict
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

# The kinds of events a simulator's log holds
Kind_Message = 'message'
Kind_Status = 'status'

# Content types a simulator answers and pushes with
Content_Type_JSON = 'application/json'
Content_Type_Form = 'application/x-www-form-urlencoded'
Content_Type_Text = 'text/plain'

# The compressed schedule a simulator resends a callback on when the receiver does not accept it, in seconds
Callback_Retry_Delays = (0.1, 0.3, 0.6)

# How long a callback push waits for the receiver
_callback_timeout = 10.0

# ################################################################################################################################
# ################################################################################################################################

class SimRequest(NamedTuple):
    """ One HTTP request as a simulator saw it.
    """
    method: 'str'
    path: 'str'
    query: 'strdict'
    headers: 'strdict'
    body: 'bytes'

    def form(self) -> 'strdict':
        out = dict(parse_qsl(self.body.decode('utf8'), keep_blank_values=True))
        return out

    def json(self) -> 'any_':
        out = loads(self.body.decode('utf8'))
        return out

# ################################################################################################################################

class SimResponse(NamedTuple):
    """ What a simulator answers one request with.
    """
    status: 'int'
    content_type: 'str'
    body: 'str'

# ################################################################################################################################

class ReceivedSend(NamedTuple):
    """ One send request a simulator accepted.
    """
    message_id: 'str'
    to: 'str'
    from_: 'str'
    body: 'str'
    callback_url: 'str'
    arrived_at: 'float'
    raw: 'stranydict'

# ################################################################################################################################

class CallbackAttempt(NamedTuple):
    """ One push of a callback to the receiver and what the receiver answered.
    """
    url: 'str'
    status: 'int'
    body: 'str'
    headers: 'strdict'
    error: 'str'

# ################################################################################################################################

@dataclass
class SimEvent:
    """ One entry of a simulator's event log - an incoming text or a change of an outgoing message's status.
    """
    seq: 'int'
    kind: 'str'
    message_id: 'str'
    from_: 'str'
    to: 'str'
    body: 'str'
    status: 'str'
    error_code: 'str'
    at: 'datetime'
    raw: 'stranydict' = field(default_factory=dict)

# ################################################################################################################################
# ################################################################################################################################

def json_response(status:'int', payload:'any_') -> 'SimResponse':
    out = SimResponse(status, Content_Type_JSON, dumps(payload))
    return out

# ################################################################################################################################

def not_found(path:'str') -> 'SimResponse':
    out = json_response(NOT_FOUND, {'error': f'No such path: {path}'})
    return out

# ################################################################################################################################

def bad_request(text:'str') -> 'SimResponse':
    out = json_response(BAD_REQUEST, {'error': text})
    return out

# ################################################################################################################################

def utc_now() -> 'datetime':
    out = datetime.now(timezone.utc)
    return out

# ################################################################################################################################
# ################################################################################################################################

class _SimulatorHandler(BaseHTTPRequestHandler):
    """ Reads each request into a SimRequest and answers with what the simulator returns for it.
    """

    def _handle(self) -> 'None':

        server = cast_('any_', self.server)
        simulator = server.simulator

        content_length = self.headers['Content-Length']

        if content_length:
            body = self.rfile.read(int(content_length))
        else:
            body = b''

        parts = urlsplit(self.path)
        query = dict(parse_qsl(parts.query, keep_blank_values=True))

        headers = {}
        for name, value in self.headers.items():
            headers[name.lower()] = value

        request = SimRequest(self.command, parts.path, query, headers, body)
        response = simulator.handle(request)

        response_body = response.body.encode('utf8')

        self.send_response(response.status)
        self.send_header('Content-Type', response.content_type)
        self.send_header('Content-Length', str(len(response_body)))
        self.end_headers()
        _ = self.wfile.write(response_body)

    def do_GET(self) -> 'None':
        self._handle()

    def do_POST(self) -> 'None':
        self._handle()

    def log_message(self, message_format:'str', *args:'object') -> 'None':
        pass

# ################################################################################################################################
# ################################################################################################################################

class SMSSimulator:
    """ The common part of every provider simulator - the HTTP server, the record of accepted sends, the event log
    that pull endpoints read from and the pushing of callbacks to a registered URL.
    """
    provider = ''

    def __init__(self, username:'str', password:'str') -> 'None':

        self.username = username
        self.password = password

        self.port = find_free_port()
        self.url = f'http://{Host}:{self.port}'

        # Every send accepted, in order of arrival
        self.sends:'list[ReceivedSend]' = []

        # Every request that did not match any endpoint or failed its checks
        self.rejections:'list[SimRequest]' = []

        # The account's event log, incoming texts and status changes alike
        self.events:'list[SimEvent]' = []

        # Every callback pushed and what came back
        self.callbacks:'list[CallbackAttempt]' = []

        # Numbers a send to which is rejected, each with the reason the provider gives - Twilio's test credentials
        # have their documented magic numbers instead and its simulator leaves this empty
        self.rejected_numbers:'dict[str, str]' = {}

        # Where callbacks go when a send did not name a URL of its own, and the URL they are signed over
        self.callback_url = ''
        self.callback_sign_url = ''

        # How long each request takes before it is answered, for a test of a timing out send
        self.delay = 0.0

        # How many entries one page of a listing has at most, which a test lowers to exercise paging
        self.page_size = 1000

        # How many requests are answered before the simulator fails, and how many it then fails in a row -
        # a test of a poll that fails midway sets both
        self.successes_before_failure = 0
        self.failures_left = 0

        self._seq = 0
        self._lock = threading.Lock()
        self._server:'any_' = None
        self._thread:'threading.Thread | None' = None

# ################################################################################################################################

    def start(self) -> 'None':
        """ Starts the simulator on its port, which stays the same across a stop and a start.
        """
        server = cast_('any_', ThreadingHTTPServer((Host, self.port), _SimulatorHandler))
        server.simulator = self
        self._server = server

        self._thread = threading.Thread(target=server.serve_forever, daemon=True)
        self._thread.start()

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Stops the simulator, leaving its port free for a later start.
        """
        if self._server is None:
            return

        self._server.shutdown()
        self._server.server_close()
        self._server = None

# ################################################################################################################################

    def reset(self) -> 'None':
        """ Forgets everything received and pushed, keeping the account and the callback registration.
        """
        with self._lock:
            self.sends.clear()
            self.rejections.clear()
            self.events.clear()
            self.callbacks.clear()
            self.delay = 0.0
            self.page_size = 1000
            self.successes_before_failure = 0
            self.failures_left = 0

# ################################################################################################################################

    def register_callback(self, url:'str', sign_url:'str'='') -> 'None':
        """ Registers where callbacks go - the way a user enters a webhook URL in a provider's console. The signature,
        where the provider has one, is computed over the sign URL when one is given, the push URL otherwise.
        """
        self.callback_url = url

        if sign_url:
            self.callback_sign_url = sign_url
        else:
            self.callback_sign_url = url

# ################################################################################################################################

    def handle(self, request:'SimRequest') -> 'SimResponse':
        """ Answers one request - a slow simulator takes its time first, then the provider's own routing runs.
        """
        if self.delay:
            time.sleep(self.delay)

        if self.failures_left:
            if self.successes_before_failure > 0:
                self.successes_before_failure -= 1
            else:
                self.failures_left -= 1
                out = SimResponse(SERVICE_UNAVAILABLE, Content_Type_Text, 'Service unavailable')
                return out

        if not self.check_auth(request):
            self.rejections.append(request)
            out = self.auth_failure()
            return out

        out = self.route(request)

        if out.status >= BAD_REQUEST:
            self.rejections.append(request)

        return out

# ################################################################################################################################

    def next_seq(self) -> 'int':
        with self._lock:
            self._seq += 1
            out = self._seq

        return out

# ################################################################################################################################

    def add_send(self, message_id:'str', to:'str', from_:'str', body:'str', callback_url:'str', raw:'stranydict') -> 'ReceivedSend':
        """ Records one accepted send along with the status event every provider's log opens it with.
        """
        out = ReceivedSend(message_id, to, from_, body, callback_url, time.monotonic(), raw)
        self.sends.append(out)

        event = SimEvent(self.next_seq(), Kind_Status, message_id, from_, to, body, self.initial_status, '', utc_now())
        self.events.append(event)

        return out

# ################################################################################################################################

    def find_send(self, message_id:'str') -> 'ReceivedSend':
        for item in self.sends:
            if item.message_id == message_id:
                out = item
                break
        else:
            raise Exception(f'No send with ID `{message_id}` among {self.sends}')

        return out

# ################################################################################################################################

    def deliver(self, message_id:'str', status:'str', error_code:'str'='') -> 'list[CallbackAttempt]':
        """ Moves one sent message to the given status, in the provider's own vocabulary, and pushes
        the provider's delivery report when a callback URL is known.
        """
        send = self.find_send(message_id)

        event = SimEvent(self.next_seq(), Kind_Status, message_id, send.from_, send.to, send.body, status, error_code, utc_now())
        self.events.append(event)

        url = send.callback_url
        if not url:
            url = self.callback_url

        out = self.push_callback(url, event)
        return out

# ################################################################################################################################

    def receive(self, from_:'str', to:'str', body:'str') -> 'SimEvent':
        """ An incoming text arrives at the account - it enters the log and goes out through the callback URL.
        """
        message_id = self.new_incoming_id()
        out = SimEvent(self.next_seq(), Kind_Message, message_id, from_, to, body, '', '', utc_now())
        self.events.append(out)

        _ = self.push_callback(self.callback_url, out)
        return out

# ################################################################################################################################

    def push_callback(self, url:'str', event:'SimEvent') -> 'list[CallbackAttempt]':
        """ Pushes one event to the URL the way the provider does, resending on the compressed schedule
        while the receiver does not accept it. Without a URL there is nothing to push.
        """
        out:'list[CallbackAttempt]' = []

        if not url:
            return out

        sign_url = url
        if url == self.callback_url:
            sign_url = self.callback_sign_url

        content_type, body = self.callback_body(event)
        headers = self.callback_headers(sign_url, body, event)
        headers['Content-Type'] = content_type

        delays = (0.0,) + Callback_Retry_Delays

        for delay in delays:
            if delay:
                time.sleep(delay)

            attempt = self._post_callback(url, headers, body)
            out.append(attempt)
            self.callbacks.append(attempt)

            if self.is_callback_accepted(attempt):
                break

        return out

# ################################################################################################################################

    def _post_callback(self, url:'str', headers:'strdict', body:'bytes') -> 'CallbackAttempt':
        try:
            response = requests.post(url, headers=headers, data=body, timeout=_callback_timeout)
        except Exception as e:
            out = CallbackAttempt(url, 0, '', {}, str(e))
        else:
            response_headers = {}
            for name, value in response.headers.items():
                response_headers[name.lower()] = value
            out = CallbackAttempt(url, response.status_code, response.text, response_headers, '')

        return out

# ################################################################################################################################

    def is_callback_accepted(self, attempt:'CallbackAttempt') -> 'bool':
        """ Whether the receiver honored the provider's response contract - a 2xx status.
        """
        out = OK <= attempt.status < 300
        return out

# ################################################################################################################################

    def accepted_callbacks(self) -> 'list[CallbackAttempt]':
        out = []
        for item in self.callbacks:
            if self.is_callback_accepted(item):
                out.append(item)
        return out

# ################################################################################################################################

    def events_of_kind(self, kind:'str') -> 'list[SimEvent]':
        out = []
        for item in self.events:
            if item.kind == kind:
                out.append(item)
        return out

# ################################################################################################################################

    def wait_for_sends(self, count:'int', timeout:'float'=10.0) -> 'list[ReceivedSend]':
        """ Waits until at least that many sends arrived, which a send through a queue needs.
        """
        deadline = time.monotonic() + timeout

        while len(self.sends) < count:
            if time.monotonic() > deadline:
                raise Exception(f'Expected {count} send(s) within {timeout}s, found {len(self.sends)}: {self.sends}')
            time.sleep(0.05)

        out = list(self.sends)
        return out

# ################################################################################################################################

    # What each provider simulator implements

    # The status a provider's log opens every accepted send with, in the provider's own vocabulary
    initial_status = ''

    def check_auth(self, request:'SimRequest') -> 'bool':
        raise NotImplementedError()

    def auth_failure(self) -> 'SimResponse':
        raise NotImplementedError()

    def route(self, request:'SimRequest') -> 'SimResponse':
        raise NotImplementedError()

    def new_incoming_id(self) -> 'str':
        raise NotImplementedError()

    def callback_body(self, event:'SimEvent') -> 'tuple[str, bytes]':
        raise NotImplementedError()

    def callback_headers(self, sign_url:'str', body:'bytes', event:'SimEvent') -> 'strdict':
        raise NotImplementedError()

# ################################################################################################################################
# ################################################################################################################################

def form_encode(params:'strdict') -> 'bytes':
    """ The body of a form-encoded callback.
    """
    out = urlencode(params).encode('utf8')
    return out

# ################################################################################################################################

def basic_auth_matches(request:'SimRequest', username:'str', password:'str') -> 'bool':
    """ Whether the request's Basic credentials are the account's.
    """
    expected = 'Basic ' + b64encode(f'{username}:{password}'.encode('utf8')).decode('ascii')
    given = request.headers.get('authorization', '')

    out = given == expected
    return out

# ################################################################################################################################

def paginate(items:'list[anydict]', page_size:'int', offset:'int') -> 'tuple[list[anydict], int]':
    """ One page of a listing and the offset of the next one, which is -1 when this was the last page.
    """
    page = items[offset:offset + page_size]
    next_offset = offset + page_size

    if next_offset >= len(items):
        next_offset = -1

    out = (page, next_offset)
    return out

# ################################################################################################################################
# ################################################################################################################################
