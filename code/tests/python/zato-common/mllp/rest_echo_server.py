# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import argparse
import logging
import signal
import socket
import socketserver
import sys

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.rest_echo')

_recv_buffer_size = 8192

# ################################################################################################################################
# ################################################################################################################################

class HTTPEchoHandler(socketserver.BaseRequestHandler):
    """ Reads a full HTTP request and echoes the body back with 200 OK.
    """

    def handle(self) -> 'None':

        data = b''

        while True:
            chunk = self.request.recv(_recv_buffer_size)
            if not chunk:
                break
            data += chunk

            # .. once we have the full headers, check Content-Length ..
            if b'\r\n\r\n' in data:
                header_end = data.index(b'\r\n\r\n') + 4
                headers_text = data[:header_end].decode('utf-8', errors='replace')

                content_length = 0

                for header_line in headers_text.split('\r\n'):
                    header_line_lower = header_line.lower()
                    if header_line_lower.startswith('content-length:'):
                        content_length = int(header_line.split(':', 1)[1].strip())
                        break

                body = data[header_end:]

                # .. read remaining body bytes if needed ..
                while len(body) < content_length:
                    chunk = self.request.recv(_recv_buffer_size)
                    if not chunk:
                        break
                    body += chunk

                # .. extract the request line for logging ..
                request_line = headers_text.split('\r\n')[0]
                logger.info('Request: %s, body_length=%d', request_line, len(body))

                # .. record the request on the server if it supports tracking ..
                if hasattr(self.server, 'request_count'):
                    self.server.request_count += 1  # type: ignore[attr-defined]
                    self.server.last_body = body    # type: ignore[attr-defined]

                # .. send the echo response ..
                body_length = len(body)

                response_headers = (
                    f'HTTP/1.1 200 OK\r\n'
                    f'Content-Length: {body_length}\r\n'
                    f'Content-Type: application/octet-stream\r\n'
                    f'Connection: close\r\n'
                    f'\r\n'
                ).encode('utf-8')

                response = response_headers + body

                self.request.sendall(response)
                logger.info('Response: 200 OK, body_length=%d', body_length)
                break

# ################################################################################################################################
# ################################################################################################################################

def _find_free_port(host:'str') -> 'int':
    """ Binds to port 0 to get an OS-assigned free port, then releases it.
    """
    temporary_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    temporary_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    temporary_socket.bind((host, 0))

    _, port = temporary_socket.getsockname()

    temporary_socket.close()

    return port

# ################################################################################################################################
# ################################################################################################################################

def _build_argument_parser() -> 'argparse.ArgumentParser':
    """ Builds the CLI argument parser with all server configuration options.
    """

    parser = argparse.ArgumentParser(description='Standalone HTTP echo server')

    _ = parser.add_argument('--host', default='127.0.0.1')
    _ = parser.add_argument('--port', type=int, default=0)
    _ = parser.add_argument('--log', action='store_true', default=False)

    return parser

# ################################################################################################################################
# ################################################################################################################################

def main() -> 'None':
    """ Entry point. Parses CLI args, starts the HTTP echo server, prints the READY signal.
    """

    parser = _build_argument_parser()
    args = parser.parse_args()

    # Configure logging if requested
    if args.log:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s %(name)s %(levelname)s %(message)s',
        )

    host = args.host

    # Resolve the port (0 means pick a free one)
    if args.port == 0:
        port = _find_free_port(host)
    else:
        port = args.port

    server = socketserver.TCPServer((host, port), HTTPEchoHandler)
    server.allow_reuse_address = True

    # Register SIGTERM handler for clean shutdown
    def _on_sigterm(signum:'int', frame:'any_') -> 'None':
        server.shutdown()

    _ = signal.signal(signal.SIGTERM, _on_sigterm)

    # Print the readiness signal
    _ = sys.stdout.write(f'READY:{port}\n')
    _ = sys.stdout.flush()

    logger.info('HTTP echo server listening on %s:%d', host, port)

    # Block on the server loop
    server.serve_forever()

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()
