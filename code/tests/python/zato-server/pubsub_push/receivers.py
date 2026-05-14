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
from threading import Thread

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

class _ReceiverHandler(BaseHTTPRequestHandler):
    """ Handles incoming push-delivered pub/sub messages by writing them to disk.
    """

    def do_POST(self) -> 'None':

        # Read the incoming message body ..
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)

        # .. parse it as JSON ..
        message = json.loads(body)

        # .. build a unique file name from the monotonic clock ..
        file_name = f'{time.monotonic_ns()}.json'
        file_path = os.path.join(self.server.output_directory, file_name) # type: ignore[attr-defined]

        # .. write the message to disk ..
        with open(file_path, 'w') as output_file:
            json.dump(message, output_file)

        # .. and confirm receipt.
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
    """

    def __init__(self, port:'int', output_directory:'str') -> 'None':
        self.port = port
        self.output_directory = output_directory
        self._server = HTTPServer(('127.0.0.1', port), _ReceiverHandler)
        self._server.output_directory = output_directory # type: ignore[attr-defined]
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
        self._thread.join(timeout=5)

# ################################################################################################################################
# ################################################################################################################################
