# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
import os
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import NamedTuple

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist

# ################################################################################################################################
# ################################################################################################################################

anydict_list = list['anydict']

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.pubsub_push.receiver')

# ################################################################################################################################
# ################################################################################################################################

_Mode_Accept     = 'accept'
_Mode_Reject_503 = 'reject_503'
_Mode_Hang       = 'hang'

# ################################################################################################################################
# ################################################################################################################################

class EvaluationResult(NamedTuple):
    status_code: int
    should_persist: bool

# ################################################################################################################################
# ################################################################################################################################

class ReceiverBehavior:
    """ Controls how the receiver responds to incoming requests.
    """

    def __init__(self) -> 'None':
        self.mode:'str' = _Mode_Accept
        self.hang_seconds:'float' = 0.0
        self.reject_count:'int' = 0
        self.auto_recover_after:'int' = 0
        self.rejected_bodies:'anylist' = []
        self._lock = threading.Lock()

# ################################################################################################################################

    def reset(self) -> 'None':
        """ Resets the behavior to accept mode with all counters cleared.
        """
        with self._lock:
            self.mode = _Mode_Accept
            self.hang_seconds = 0.0
            self.reject_count = 0
            self.auto_recover_after = 0
            self.rejected_bodies = []

# ################################################################################################################################

    def set_accept(self) -> 'None':
        """ Switches to accept mode.
        """
        with self._lock:
            self.mode = _Mode_Accept

# ################################################################################################################################

    def set_reject_503(self, auto_recover_after:'int'=0) -> 'None':
        """ Switches to reject mode, optionally auto-recovering after N rejections.
        """
        with self._lock:
            self.mode = _Mode_Reject_503
            self.reject_count = 0
            self.auto_recover_after = auto_recover_after
            self.rejected_bodies = []

# ################################################################################################################################

    def set_hang(self, seconds:'float') -> 'None':
        """ Switches to hang mode with the given delay.
        """
        with self._lock:
            self.mode = _Mode_Hang
            self.hang_seconds = seconds

# ################################################################################################################################

    def evaluate(self, body:'bytes') -> 'EvaluationResult':
        """ Returns an EvaluationResult for the current request.
        """
        with self._lock:

            if self.mode == _Mode_Accept:
                out = EvaluationResult(status_code=200, should_persist=True)
                return out

            if self.mode == _Mode_Reject_503:
                self.reject_count += 1
                self.rejected_bodies.append(body)

                if self.auto_recover_after > 0:
                    if self.reject_count >= self.auto_recover_after:
                        self.mode = _Mode_Accept

                out = EvaluationResult(status_code=503, should_persist=False)
                return out

            # .. mode is hang - capture the delay while under lock ..
            delay = self.hang_seconds

        # .. sleep outside the lock so other threads are not blocked ..
        time.sleep(delay)

        out = EvaluationResult(status_code=200, should_persist=True)
        return out

# ################################################################################################################################
# ################################################################################################################################

class _RequestHandler(BaseHTTPRequestHandler):
    """ Handles incoming webhook POST requests.
    """

    def log_message(self, format:'str', *arguments:'any_') -> 'None':
        """ Routes HTTP server log messages through the module logger.
        """
        message = format % arguments
        logger.debug('[HTTP] %s', message)

# ################################################################################################################################

    def do_POST(self) -> 'None': # noqa: N802
        """ Handles a POST request from a Zato push delivery.
        """

        # Read the request body ..
        content_length_header = self.headers.get('Content-Length')
        if content_length_header is None:
            content_length_header = '0'
        content_length = int(content_length_header)
        body = self.rfile.read(content_length)

        logger.info('Received POST %s (%d bytes)', self.path, content_length)

        # .. evaluate the behavior ..
        behavior:'ReceiverBehavior' = self.server.behavior # type: ignore[attr-defined]
        result = behavior.evaluate(body)

        logger.info('Evaluated -> status_code=%d, should_persist=%s', result.status_code, result.should_persist)

        # .. if we should persist, write the payload to disk ..
        if result.should_persist:
            output_directory:'str' = self.server.output_directory # type: ignore[attr-defined]
            unique_id = uuid.uuid4()
            hex_string = unique_id.hex
            file_name = f'{hex_string}.json'
            file_path = os.path.join(output_directory, file_name)

            with open(file_path, 'wb') as output_file:
                _ = output_file.write(body)

            logger.info('Persisted payload to %s', file_path)

        # .. send the response.
        self.send_response(result.status_code)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()

# ################################################################################################################################
# ################################################################################################################################

class WebhookReceiver:
    """ An HTTP receiver that runs in a background thread.
    """

    def __init__(self, port:'int', output_directory:'str', expected_path:'str'='') -> 'None':
        self.port = port
        self.output_directory = output_directory
        self.expected_path = expected_path
        self.behavior = ReceiverBehavior()
        self._server:'HTTPServer | None' = None
        self._thread:'threading.Thread | None' = None

# ################################################################################################################################

    def start(self) -> 'None':
        """ Starts the HTTP server in a daemon thread.
        """
        os.makedirs(self.output_directory, exist_ok=True)

        address = ('127.0.0.1', self.port)
        server = HTTPServer(address, _RequestHandler)
        server.behavior = self.behavior # type: ignore[attr-defined]
        server.output_directory = self.output_directory # type: ignore[attr-defined]

        self._server = server

        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self._thread = thread

        logger.info('Receiver started on port %d, output -> %s', self.port, self.output_directory)

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Shuts down the HTTP server.
        """
        if self._server:
            self._server.shutdown()
            self._server.server_close()
            self._server = None
            self._thread = None
            logger.info('Receiver stopped on port %d', self.port)

# ################################################################################################################################

    def restart(self) -> 'None':
        """ Restarts the receiver on the same port.
        """
        logger.info('Restarting receiver on port %d', self.port)
        self.stop()
        self.start()

# ################################################################################################################################

    def get_delivered_messages(self) -> 'anydict_list':
        """ Returns all delivered message payloads from disk, sorted by file creation order.
        """
        out:'anydict_list' = []

        file_names = sorted(os.listdir(self.output_directory))

        for file_name in file_names:
            if not file_name.endswith('.json'):
                continue

            file_path = os.path.join(self.output_directory, file_name)

            with open(file_path, 'r') as input_file:
                content = input_file.read()

            parsed = json.loads(content)
            out.append(parsed)

        logger.info('Read %d delivered messages from %s', len(out), self.output_directory)

        return out

# ################################################################################################################################

    def clear_output(self) -> 'None':
        """ Removes all delivered message files from the output directory.
        """
        file_names = os.listdir(self.output_directory)

        for file_name in file_names:
            file_path = os.path.join(self.output_directory, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)

        logger.debug('Cleared output directory %s', self.output_directory)

# ################################################################################################################################

    def delivered_count(self) -> 'int':
        """ Returns the number of delivered message files.
        """
        if not os.path.isdir(self.output_directory):
            logger.warning('Output directory does not exist for count: %s', self.output_directory)
            return 0

        count = 0

        for file_name in os.listdir(self.output_directory):
            if file_name.endswith('.json'):
                count += 1

        return count

# ################################################################################################################################
# ################################################################################################################################
