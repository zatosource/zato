# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The endpoint of a REST push subscription that receives several messages per request. It records the message ID
# and the delivery attempt of each message in the order of arrival and responds with the list of the message IDs
# that it accepts. A test can hold the next request until it releases it, or accept only the first messages of it.

# stdlib
import errno
import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# Zato
from ha_push_delivery.server import ModuleCtx as ServerCtx
from zato.common.test.reservation import PortInUse, start_on_reserved_port
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.reservation import ReservedStart
    from zato.common.typing_ import any_, anylist, intlist, intnone, strlist

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How long a held request waits for its release, in seconds
    Hold_Timeout = 20.0

    # How long a test waits for the requests that it expects, in seconds, and how often it checks them
    Request_Timeout = 20.0
    Poll_Interval = 0.05

# ################################################################################################################################
# ################################################################################################################################

class _Server(ThreadingHTTPServer):
    """ The HTTP server of the receiver, which waits for the threads of its requests when it closes.
    A request whose client disconnected before its response was written, as a killed Zato server does,
    is not reported as an error.
    """
    daemon_threads = False
    block_on_close = True
    receiver: 'ListReceiver'

    def handle_error(self, request:'any_', client_address:'any_') -> 'None':
        _ = request
        _ = client_address

# ################################################################################################################################
# ################################################################################################################################

class _Handler(BaseHTTPRequestHandler):
    """ Hands the envelopes of each request to the receiver and responds with the message IDs that it accepted,
    closing the connection after each response, so no thread of a request outlives the receiver.
    """
    def do_POST(self) -> 'None':
        server = cast_('_Server', self.server)

        length = int(self.headers['Content-Length'])
        envelopes = json.loads(self.rfile.read(length))

        accepted = server.receiver.on_request(envelopes)
        body = json.dumps(accepted).encode('utf8')

        try:
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', f'{len(body)}')
            self.end_headers()
            _ = self.wfile.write(body)
        except ConnectionError:
            self.close_connection = True

    def log_message(self, format:'str', *args:'any_') -> 'None':
        _ = format
        _ = args

# ################################################################################################################################
# ################################################################################################################################

class ListReceiver:
    """ Receives the push requests of one subscription on a port of its own.
    """
    def __init__(self, port:'int') -> 'None':

        self.port = port

        # The message ID and the delivery attempt of each message received, in the order of arrival ..
        self.received:'list[tuple[str, int]]' = []

        # .. and the message IDs of each request.
        self.requests:'list[strlist]' = []

        self._lock = threading.Lock()

        # What the next request is subject to - a hold until the test releases it,
        # and the number of its first messages that are accepted, or None if all of them are.
        self._next_hold:'threading.Event | None' = None
        self._next_accept_count:'intnone' = None

        self._server = _Server((ServerCtx.Host, port), _Handler)
        self._server.receiver = self

        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)

# ################################################################################################################################

    def start(self) -> 'None':
        self._thread.start()

# ################################################################################################################################

    def stop(self) -> 'None':
        self._server.shutdown()
        self._server.server_close()

# ################################################################################################################################

    def reset(self) -> 'None':
        """ Forgets what was received and what the next request is subject to.
        """
        with self._lock:
            self.received.clear()
            self.requests.clear()
            self._next_hold = None
            self._next_accept_count = None

# ################################################################################################################################

    def hold_next(self) -> 'threading.Event':
        """ Makes the next request wait until the event that this returns is set.
        """
        out = threading.Event()

        with self._lock:
            self._next_hold = out

        return out

# ################################################################################################################################

    def accept_next(self, count:'int') -> 'None':
        """ Makes the next request accept only its first messages, as many as given.
        """
        with self._lock:
            self._next_accept_count = count

# ################################################################################################################################

    def on_request(self, envelopes:'anylist') -> 'strlist':
        """ Records the messages of one request and returns the message IDs that it accepts.
        """
        msg_ids:'strlist' = []

        with self._lock:

            # Each message is recorded ..
            for envelope in envelopes:
                msg_id = envelope['msg_id']
                msg_ids.append(msg_id)
                self.received.append((msg_id, envelope['delivery_attempt']))

            self.requests.append(msg_ids)

            # .. and only this request is subject to what the test asked for.
            hold = self._next_hold
            accept_count = self._next_accept_count

            self._next_hold = None
            self._next_accept_count = None

        if hold:
            _ = hold.wait(ModuleCtx.Hold_Timeout)

        if accept_count is None:
            out = msg_ids
        else:
            out = msg_ids[:accept_count]

        return out

# ################################################################################################################################

    def get_attempts(self, msg_id:'str') -> 'intlist':
        """ Returns the delivery attempt of each receipt of one message, in the order of arrival.
        """
        out:'intlist' = []

        with self._lock:
            for received_msg_id, attempt in self.received:
                if received_msg_id == msg_id:
                    out.append(attempt)

        return out

# ################################################################################################################################

    def get_order(self, attempt:'int') -> 'strlist':
        """ Returns the message IDs received with one delivery attempt, in the order of arrival.
        """
        out:'strlist' = []

        with self._lock:
            for msg_id, received_attempt in self.received:
                if received_attempt == attempt:
                    out.append(msg_id)

        return out

# ################################################################################################################################

    def wait_for_requests(self, count:'int') -> 'None':
        """ Waits until the receiver has received at least as many requests as given.
        """
        deadline = time.monotonic() + ModuleCtx.Request_Timeout

        while len(self.requests) < count:
            if time.monotonic() > deadline:
                raise Exception(f'Fewer than {count} requests received within {ModuleCtx.Request_Timeout}s')
            time.sleep(ModuleCtx.Poll_Interval)

# ################################################################################################################################
# ################################################################################################################################

def _start_receiver(port:'int') -> 'ListReceiver':
    """ Starts the receiver on the port, raising PortInUse if another process took the port before it was bound.
    """
    try:
        out = ListReceiver(port)
    except OSError as e:
        if e.errno == errno.EADDRINUSE:
            raise PortInUse(f'Port {port} of the receiver is in use') from e
        raise

    out.start()
    return out

# ################################################################################################################################

def start_list_receiver() -> 'ReservedStart':
    """ Starts the receiver of a REST push subscription on a reserved port. The result holds the reservation
    of the port and the receiver.
    """
    out = start_on_reserved_port(ServerCtx.Port_Purpose, _start_receiver)
    return out

# ################################################################################################################################
# ################################################################################################################################
