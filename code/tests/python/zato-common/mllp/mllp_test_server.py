# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import argparse
import signal
import socket
import sys
import time

# Zato
from zato.common.hl7.mllp.router import HL7MessageRouter
from zato.common.hl7.mllp.server import HL7MLLPServer
from zato.common.hl7.mllp.tls import build_server_ssl_context

# ################################################################################################################################
# ################################################################################################################################

# Module-level variable set by --callback-delay for the slow callback
_slow_callback_delay_seconds = 5.0

# ################################################################################################################################
# ################################################################################################################################

def _callback_ok(message_text:'str') -> 'None':
    """ Accepts the message, does nothing. Server will auto-ACK with AA.
    """
    return None

# ################################################################################################################################

def _callback_echo(message_text:'str') -> 'None':
    """ Logs the message text to stdout for debugging. Server still auto-ACKs with AA.
    """
    sys.stdout.write(f'ECHO:{message_text}\n')
    sys.stdout.flush()
    return None

# ################################################################################################################################

def _callback_error(message_text:'str') -> 'None':
    """ Raises an exception so the server will auto-ACK with AE.
    """
    raise RuntimeError('Intentional test error')

# ################################################################################################################################

def _callback_slow(message_text:'str') -> 'None':
    """ Sleeps for the configured delay before returning. Server auto-ACKs with AA after the sleep.
    """
    time.sleep(_slow_callback_delay_seconds)
    return None

# ################################################################################################################################
# ################################################################################################################################

_callback_map = {
    'ok':    _callback_ok,
    'echo':  _callback_echo,
    'error': _callback_error,
    'slow':  _callback_slow,
}

# ################################################################################################################################
# ################################################################################################################################

_start_sequence = b'\x0b'
_end_sequence   = b'\x1c\x0d'

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

    parser = argparse.ArgumentParser(description='Standalone MLLP test server')

    # Network
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=0)

    # Callback
    parser.add_argument('--callback-mode', choices=list(_callback_map), default='ok')
    parser.add_argument('--callback-delay', type=float, default=5.0)

    # Server tuning
    parser.add_argument('--max-msg-size', type=int, default=2_000_000)
    parser.add_argument('--read-buffer-size', type=int, default=4096)
    parser.add_argument('--recv-timeout', type=float, default=30.0)
    parser.add_argument('--log-messages', action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument('--should-return-errors', action=argparse.BooleanOptionalAction, default=False)

    # TLS
    parser.add_argument('--tls-cert', default='')
    parser.add_argument('--tls-key', default='')
    parser.add_argument('--tls-ca', default='')
    parser.add_argument('--tls-verify', choices=['none', 'optional', 'required'], default='none')

    # Pre-processing toggles (each has a --no- variant via BooleanOptionalAction)
    parser.add_argument('--normalize-line-endings', action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument('--repair-truncated-msh', action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument('--split-concatenated-messages', action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument('--force-standard-delimiters', action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument('--use-msh18-encoding', action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument('--default-character-encoding', default='utf-8')

    # Deduplication
    parser.add_argument('--dedup-ttl-value', type=int, default=0)
    parser.add_argument('--dedup-ttl-unit', default='')

    return parser

# ################################################################################################################################
# ################################################################################################################################

def main() -> 'None':
    """ Entry point. Parses CLI args, starts the MLLP server, prints the READY signal.
    """

    global _slow_callback_delay_seconds

    parser = _build_argument_parser()
    args = parser.parse_args()

    # Wire the slow callback delay from the CLI arg
    _slow_callback_delay_seconds = args.callback_delay

    # Resolve the callback function
    callback_func = _callback_map[args.callback_mode]

    # Resolve the port (0 means pick a free one)
    host = args.host

    if args.port == 0:
        port = _find_free_port(host)
    else:
        port = args.port

    address = f'{host}:{port}'

    # Build TLS context if cert is provided (not yet wired to HL7MLLPServer)
    _ssl_context = None

    if args.tls_cert:
        _ssl_context = build_server_ssl_context(
            cert_file=args.tls_cert,
            key_file=args.tls_key,
            ca_file=args.tls_ca,
            verify_mode=args.tls_verify,
        )

    # Wrap the callback in a default-route router
    router = HL7MessageRouter()
    router.add_route(
        channel_name='test',
        service_name='test',
        callback=callback_func,
        is_default=True,
    )

    # Instantiate the server with all config
    server = HL7MLLPServer(
        address,
        router,
        _start_sequence,
        _end_sequence,
        receive_timeout=args.recv_timeout,
        max_message_size=args.max_msg_size,
        read_buffer_size=args.read_buffer_size,
        should_log_messages=args.log_messages,
        should_return_errors=args.should_return_errors,
        should_normalize_line_endings=args.normalize_line_endings,
        should_repair_truncated_msh=args.repair_truncated_msh,
        should_split_concatenated_messages=args.split_concatenated_messages,
        should_force_standard_delimiters=args.force_standard_delimiters,
        should_use_msh18_encoding=args.use_msh18_encoding,
        default_character_encoding=args.default_character_encoding,
        dedup_ttl_value=args.dedup_ttl_value,
        dedup_ttl_unit=args.dedup_ttl_unit,
    )

    # Register SIGTERM handler for clean shutdown
    def _on_sigterm(signum:'int', frame:'object') -> 'None':
        server.stop()

    signal.signal(signal.SIGTERM, _on_sigterm)

    # Print the readiness signal that the test harness waits for
    sys.stdout.write(f'READY:{port}\n')
    sys.stdout.flush()

    # Block on the server loop
    server.start()

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()
