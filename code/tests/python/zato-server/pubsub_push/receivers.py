# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import os
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Lock, Thread

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

str_int_tuple = tuple[str, int]

# ################################################################################################################################
# ################################################################################################################################

class ReceiverBehavior:
    """ Controls how a controllable receiver responds to incoming requests.
    Thread-safe - all mutations go through the lock.
    """

    def __init__(self) -> 'None':
        self._lock = Lock()
        self._mode = 'accept'
        self._hang_seconds = 10
        self._reject_remaining = 0
        self._received_count = 0
        self._rejected_count = 0
        self._last_rejected_body = ''

# ################################################################################################################################

    def set_accept(self) -> 'None':
        with self._lock:
            self._mode = 'accept'
            self._reject_remaining = 0

# ################################################################################################################################

    def set_reject_503(self, reject_count:'int'=0) -> 'None':
        """ Switch to 503 mode. If reject_count > 0, auto-recover to accept
        after that many rejections. If 0, reject indefinitely until reset.
        """
        with self._lock:
            self._mode = 'reject_503'
            self._reject_remaining = reject_count

# ################################################################################################################################

    def set_hang(self, hang_seconds:'int'=10) -> 'None':
        with self._lock:
            self._mode = 'hang'
            self._hang_seconds = hang_seconds

# ################################################################################################################################

    def record_rejection(self, body:'str') -> 'None':
        """ Record the body of a rejected request so tests can verify
        Zato sent a real payload during rejected delivery attempts.
        """
        with self._lock:
            self._rejected_count += 1
            self._last_rejected_body = body

# ################################################################################################################################

    def get_action(self) -> 'str_int_tuple':
        """ Return the current action and update internal counters.
        Returns a tuple of (mode, hang_seconds).
        """
        with self._lock:

            # Bump the received count ..
            self._received_count += 1

            # .. if we are in reject mode, decrement the counter
            # and auto-recover when it hits zero ..
            if self._mode == 'reject_503':
                if self._reject_remaining > 0:
                    self._reject_remaining -= 1
                    if self._reject_remaining == 0:
                        self._mode = 'accept'

                out = ('reject_503', 0)
                return out

            # .. if we are in hang mode, return the hang duration ..
            if self._mode == 'hang':

                out = ('hang', self._hang_seconds)
                return out

            # .. otherwise, accept normally.
            out = ('accept', 0)
            return out

# ################################################################################################################################

    @property
    def received_count(self) -> 'int':
        with self._lock:

            out = self._received_count
            return out

# ################################################################################################################################

    @property
    def rejected_count(self) -> 'int':
        with self._lock:

            out = self._rejected_count
            return out

# ################################################################################################################################

    @property
    def last_rejected_body(self) -> 'str':
        with self._lock:

            out = self._last_rejected_body
            return out

# ################################################################################################################################
# ################################################################################################################################

class _ControllableHandler(BaseHTTPRequestHandler):
    """ Handles incoming push-delivered pub/sub messages. Checks the server's
    behavior object to decide whether to accept, reject, or hang.
    """

    def do_POST(self) -> 'None':

        # Verify that Zato is POSTing to the correct webhook path ..
        expected_path = self.server.expected_path # type: ignore[attr-defined]

        if self.path != expected_path:
            self.send_response(404)
            self.end_headers()
            return

        # .. verify Content-Type is application/json ..
        content_type = self.headers['Content-Type']

        if not content_type:
            self.send_response(415)
            self.end_headers()
            return

        if not content_type.startswith('application/json'):
            self.send_response(415)
            self.end_headers()
            return

        # .. read the request body ..
        content_length_header = self.headers['Content-Length']
        content_length = int(content_length_header)
        body = self.rfile.read(content_length)

        # .. check what action the behavior prescribes ..
        behavior = self.server.behavior # type: ignore[attr-defined]
        action, hang_seconds = behavior.get_action()

        # .. reject with 503, but record the payload so tests can
        # verify Zato sent real data during rejected attempts ..
        if action == 'reject_503':
            behavior.record_rejection(body.decode('utf-8'))
            self.send_response(503)
            self.end_headers()
            return

        # .. simulate a slow receiver if needed ..
        if action == 'hang':
            time.sleep(hang_seconds)

        # .. parse and write the message to disk ..
        message = json.loads(body)

        timestamp_ns = time.monotonic_ns()
        file_name = f'{timestamp_ns}.json'

        output_directory = self.server.output_directory # type: ignore[attr-defined]
        file_path = os.path.join(output_directory, file_name)

        with open(file_path, 'w') as output_file:
            json.dump(message, output_file)

        # .. and send back a 200.
        self.send_response(200)
        self.end_headers()

# ################################################################################################################################

    def log_message(self, format:'str', *arguments:'any_') -> 'None':
        """ Suppress default stderr logging from BaseHTTPRequestHandler.
        """
        pass

# ################################################################################################################################
# ################################################################################################################################

class ReceiverServer:
    """ An HTTP server that receives push-delivered pub/sub messages and
    writes each one as a JSON file to a dedicated output directory.
    Behavior is controllable at runtime via the attached ReceiverBehavior object.
    """

    def __init__(self, port:'int', output_directory:'str', expected_path:'str') -> 'None':
        self.port = port
        self.output_directory = output_directory
        self.expected_path = expected_path
        self.behavior = ReceiverBehavior()
        self._server = HTTPServer(('127.0.0.1', port), _ControllableHandler)
        self._server.output_directory = output_directory # type: ignore[attr-defined]
        self._server.behavior = self.behavior # type: ignore[attr-defined]
        self._server.expected_path = expected_path # type: ignore[attr-defined]
        self._thread = Thread(target=self._server.serve_forever, daemon=True)

# ################################################################################################################################

    def start(self) -> 'None':
        """ Start the HTTP server in a background daemon thread.
        """
        self._thread.start()

# ################################################################################################################################

    def shutdown(self) -> 'None':
        """ Stop the HTTP server and wait for the thread to finish.
        """
        self._server.shutdown()
        self._server.server_close()
        self._thread.join(timeout=5)

# ################################################################################################################################

    def restart(self) -> 'None':
        """ Restart the HTTP server on the same port after a shutdown.
        """
        self._server = HTTPServer(('127.0.0.1', self.port), _ControllableHandler)
        self._server.output_directory = self.output_directory # type: ignore[attr-defined]
        self._server.behavior = self.behavior # type: ignore[attr-defined]
        self._server.expected_path = self.expected_path # type: ignore[attr-defined]
        self._thread = Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()

# ################################################################################################################################
# ################################################################################################################################
