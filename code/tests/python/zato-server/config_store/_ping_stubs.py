# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import socket
import socketserver
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# ################################################################################################################################
# ################################################################################################################################

def _find_free_port() -> 'int':
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
        tcp_socket.bind(('127.0.0.1', 0))
        return tcp_socket.getsockname()[1]

# ################################################################################################################################
# ################################################################################################################################

def start_http_stub(handler=None):
    """ Starts a local HTTP server in a daemon thread and returns (port, server).

    By default every request is answered with 200 and an empty JSON object.
    A custom handler may be given as a callable (method, path, body_bytes) -> dict,
    whose result is serialized to JSON and returned with status 200.

    The caller is responsible for invoking server.shutdown().
    """

    class _StubHandler(BaseHTTPRequestHandler):

        def log_message(self, format, *args):
            pass

        def _respond(self, method):
            length = int(self.headers.get('Content-Length') or 0)
            body_bytes = self.rfile.read(length) if length else b''

            if handler:
                response_data = handler(method, self.path, body_bytes)
            else:
                response_data = {}

            body = json.dumps(response_data).encode('utf-8')

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            _ = self.wfile.write(body)

        def do_GET(self):
            self._respond('GET')

        def do_POST(self):
            self._respond('POST')

        def do_HEAD(self):
            self._respond('HEAD')

        def do_OPTIONS(self):
            self._respond('OPTIONS')

    port = _find_free_port()
    server = HTTPServer(('127.0.0.1', port), _StubHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    return port, server

# ################################################################################################################################
# ################################################################################################################################

class _ThreadingTCPServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True

# ################################################################################################################################

def _start_tcp_stub(handler_class):
    port = _find_free_port()
    server = _ThreadingTCPServer(('127.0.0.1', port), handler_class)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return port, server

# ################################################################################################################################
# ################################################################################################################################

def start_smtp_stub():
    """ Starts a minimal SMTP server good enough for smtplib to send one message.
    Returns (port, server), the caller invokes server.shutdown().
    """

    class _SMTPHandler(socketserver.StreamRequestHandler):

        def _send(self, line):
            self.wfile.write((line + '\r\n').encode('ascii'))

        def handle(self):
            self._send('220 ping-stub ESMTP')

            in_data = False

            while True:
                line = self.rfile.readline()
                if not line:
                    break
                text = line.decode('utf-8', 'replace').rstrip('\r\n')

                if in_data:
                    # The message body ends with a lone dot
                    if text == '.':
                        in_data = False
                        self._send('250 OK message accepted')
                    continue

                verb = text.split(' ')[0].upper()

                if verb in ('EHLO', 'HELO'):
                    self._send('250-ping-stub')
                    self._send('250 AUTH PLAIN LOGIN')
                elif verb == 'AUTH':
                    self._send('235 Authentication successful')
                elif verb in ('MAIL', 'RCPT', 'NOOP', 'RSET'):
                    self._send('250 OK')
                elif verb == 'DATA':
                    in_data = True
                    self._send('354 End data with <CR><LF>.<CR><LF>')
                elif verb == 'QUIT':
                    self._send('221 Bye')
                    break
                else:
                    self._send('250 OK')

    return _start_tcp_stub(_SMTPHandler)

# ################################################################################################################################
# ################################################################################################################################

def start_imap_stub():
    """ Starts a minimal IMAP server that greets the client and answers
    every tagged command with OK, which satisfies imaplib LOGIN/NOOP/LOGOUT.
    Returns (port, server), the caller invokes server.shutdown().
    """

    class _IMAPHandler(socketserver.StreamRequestHandler):

        def _send(self, line):
            self.wfile.write((line + '\r\n').encode('ascii'))

        def handle(self):
            self._send('* OK ping-stub IMAP4rev1 ready')

            while True:
                line = self.rfile.readline()
                if not line:
                    break
                text = line.decode('utf-8', 'replace').rstrip('\r\n')
                parts = text.split(' ')
                tag = parts[0]
                command = parts[1].upper() if len(parts) > 1 else ''

                if command == 'CAPABILITY':
                    self._send('* CAPABILITY IMAP4rev1')
                    self._send(f'{tag} OK CAPABILITY completed')
                elif command == 'LIST':
                    self._send('* LIST () "/" "INBOX"')
                    self._send(f'{tag} OK LIST completed')
                elif command == 'SELECT':
                    self._send('* 0 EXISTS')
                    self._send('* 0 RECENT')
                    self._send(f'{tag} OK [READ-WRITE] SELECT completed')
                elif command == 'LOGOUT':
                    self._send('* BYE ping-stub logging out')
                    self._send(f'{tag} OK LOGOUT completed')
                    break
                else:
                    # LOGIN, NOOP and anything else succeed generically
                    self._send(f'{tag} OK {command} completed')

    return _start_tcp_stub(_IMAPHandler)

# ################################################################################################################################
# ################################################################################################################################

# The BER-encoded body of a bindResponse(success), appended after the echoed message ID.
_LDAP_BIND_RESPONSE_BODY = bytes([
    0x61, 0x07,             # bindResponse, 7 bytes
    0x0a, 0x01, 0x00,       # resultCode success (0)
    0x04, 0x00,             # matchedDN, empty
    0x04, 0x00,             # diagnosticMessage, empty
])

# The BER tag of an LDAP bindRequest.
_LDAP_BIND_REQUEST_TAG = 0x60

def start_ldap_stub():
    """ Starts a TCP server that answers every LDAP bindRequest with a success
    bindResponse carrying the same message ID. Abandon and unbind requests
    expect no response so they are read and discarded.
    Returns (port, server), the caller invokes server.shutdown().
    """

    class _LDAPHandler(socketserver.StreamRequestHandler):

        def handle(self):
            while True:
                data = self.request.recv(4096)
                if not data:
                    break

                # Skip past the outer sequence header, whose length may use the long form
                offset = 2
                if data[1] & 0x80:
                    offset += data[1] & 0x7f

                # The message ID is a BER integer right after the sequence header
                msgid_len = data[offset + 1]
                msgid_bytes = data[offset + 2:offset + 2 + msgid_len]
                op_tag = data[offset + 2 + msgid_len]

                # Only bind requests expect a response
                if op_tag == _LDAP_BIND_REQUEST_TAG:
                    payload = bytes([0x02, msgid_len]) + msgid_bytes + _LDAP_BIND_RESPONSE_BODY
                    response = bytes([0x30, len(payload)]) + payload
                    self.request.sendall(response)

    return _start_tcp_stub(_LDAPHandler)

# ################################################################################################################################
# ################################################################################################################################
