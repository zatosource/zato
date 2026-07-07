# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import socketserver
import threading

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class IMAPTestRequestHandler(socketserver.StreamRequestHandler):
    """ Speaks just enough IMAP4 for imaplib-based clients to log in, select a folder, issue NOOP and log out.
    """

    def _respond(self, data:'bytes') -> 'None':
        self.wfile.write(data + b'\r\n')

# ################################################################################################################################

    def _handle_capability(self, tag:'str') -> 'bool':
        self._respond(b'* CAPABILITY IMAP4rev1')
        self._respond(tag.encode('utf-8') + b' OK CAPABILITY completed')
        return True

# ################################################################################################################################

    def _handle_select(self, tag:'str') -> 'bool':
        self._respond(b'* 0 EXISTS')
        self._respond(b'* 0 RECENT')
        self._respond(tag.encode('utf-8') + b' OK [READ-WRITE] SELECT completed')
        return True

# ################################################################################################################################

    def _handle_logout(self, tag:'str') -> 'bool':
        self._respond(b'* BYE IMAP test server signing off')
        self._respond(tag.encode('utf-8') + b' OK LOGOUT completed')
        return False

# ################################################################################################################################

    def _handle_any_other(self, tag:'str', command:'str') -> 'bool':
        message = f'{tag} OK {command} completed'
        self._respond(message.encode('utf-8'))
        return True

# ################################################################################################################################

    def handle(self) -> 'None':

        # Send the greeting first, advertising capabilities so the client does not need to ask for them
        self._respond(b'* OK [CAPABILITY IMAP4rev1] IMAP test server ready')

        # Keep serving commands until the client logs out or disconnects
        while True:

            line = self.rfile.readline()

            # An empty read means the client disconnected
            if not line:
                break

            text = line.strip().decode('utf-8', errors='replace')

            # Ignore keep-alive empty lines
            if not text:
                continue

            # Every received command is recorded for tests to assert on
            self.server.received_commands.append(text)
            logger.info('IMAP test server received: %s', text)

            parts = text.split(' ')
            tag = parts[0]
            command = parts[1].upper()

            if command == 'CAPABILITY':
                should_continue = self._handle_capability(tag)

            elif command == 'SELECT':
                should_continue = self._handle_select(tag)

            elif command == 'LOGOUT':
                should_continue = self._handle_logout(tag)

            # LOGIN, NOOP and anything else simply succeed
            else:
                should_continue = self._handle_any_other(tag, command)

            if not should_continue:
                break

# ################################################################################################################################
# ################################################################################################################################

class IMAPTestServer(socketserver.ThreadingTCPServer):
    """ A minimal IMAP server listening on 127.0.0.1 on a random port, for use in live tests.
    """
    allow_reuse_address = True
    daemon_threads = True

    def __init__(self) -> 'None':

        # Binding to port 0 makes the operating system pick a random free port
        super().__init__(('127.0.0.1', 0), IMAPTestRequestHandler)

        self.received_commands = []
        self.host, self.port = self.server_address

# ################################################################################################################################

    def start(self) -> 'None':
        thread = threading.Thread(target=self.serve_forever, daemon=True)
        thread.start()
        logger.info('IMAP test server listening on %s:%s', self.host, self.port)

# ################################################################################################################################

    def stop(self) -> 'None':
        self.shutdown()
        self.server_close()

# ################################################################################################################################

    def has_received(self, command:'str') -> 'bool':
        """ Returns True if any of the received lines contains the given IMAP command.
        """
        for line in self.received_commands:
            if command in line.upper():
                out = True
                break
        else:
            out = False

        return out

# ################################################################################################################################
# ################################################################################################################################
