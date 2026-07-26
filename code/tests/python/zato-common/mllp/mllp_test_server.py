# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# gevent
# The listener serves each connection on a greenlet, so this has to happen before anything
# imports a socket, the same way a Zato server patches itself before it starts
from gevent.monkey import patch_all
_ = patch_all()

# stdlib
import argparse
import signal
import socket
import sys
import time

# Zato
from zato.common.hl7.mllp.preprocess import build_tolerance_config
from zato.common.hl7.mllp.router import HL7MessageRouter
from zato.common.hl7.mllp.server import HL7MLLPServer
from zato.common.hl7.mllp.settings import ListenerConfig, RouteSettings

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
    _ = sys.stdout.write(f'ECHO:{message_text}\n')
    _ = sys.stdout.flush()
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
    _ = parser.add_argument('--host', default='127.0.0.1')
    _ = parser.add_argument('--port', type=int, default=0)

    # Callback
    _ = parser.add_argument('--callback-mode', choices=list(_callback_map), default='ok')
    _ = parser.add_argument('--callback-delay', type=float, default=5.0)

    # Server tuning
    _ = parser.add_argument('--max-msg-size', type=int, default=2_000_000)
    _ = parser.add_argument('--read-buffer-size', type=int, default=4096)
    _ = parser.add_argument('--recv-timeout', type=float, default=30.0)
    _ = parser.add_argument('--log-messages', action=argparse.BooleanOptionalAction, default=False)
    _ = parser.add_argument('--should-return-errors', action=argparse.BooleanOptionalAction, default=False)

    # What the channel accepts a message from - the load balancer reports both on the PROXY header
    _ = parser.add_argument('--security-common-name', default='')
    _ = parser.add_argument('--allowed-networks', default='')

    # Pre-processing toggles (each has a --no- variant via BooleanOptionalAction)
    _ = parser.add_argument('--normalize-line-endings', action=argparse.BooleanOptionalAction, default=True)
    _ = parser.add_argument('--repair-truncated-msh', action=argparse.BooleanOptionalAction, default=True)
    _ = parser.add_argument('--split-concatenated-messages', action=argparse.BooleanOptionalAction, default=True)
    _ = parser.add_argument('--force-standard-delimiters', action=argparse.BooleanOptionalAction, default=True)
    _ = parser.add_argument('--use-msh18-encoding', action=argparse.BooleanOptionalAction, default=True)
    _ = parser.add_argument('--default-character-encoding', default='utf-8')

    # Deduplication
    _ = parser.add_argument('--dedup-ttl-value', type=int, default=0)
    _ = parser.add_argument('--dedup-ttl-unit', default='')

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

    # How the one channel this server serves reads its messages
    settings = RouteSettings(
        start_sequence=_start_sequence,
        end_sequence=_end_sequence,
        recv_timeout=args.recv_timeout,
        max_message_size=args.max_msg_size,
        should_log_messages=args.log_messages,
        should_return_errors=args.should_return_errors,

        # Callbacks receive the raw ER7 text so the echo mode can log it verbatim
        should_parse_on_input=False,
        should_normalize_line_endings=args.normalize_line_endings,
        should_repair_truncated_msh=args.repair_truncated_msh,
        should_split_concatenated_messages=args.split_concatenated_messages,
        should_force_standard_delimiters=args.force_standard_delimiters,
        should_use_msh18_encoding=args.use_msh18_encoding,
        default_character_encoding=args.default_character_encoding,
        tolerance_config=build_tolerance_config(),
        dedup_ttl_value=args.dedup_ttl_value,
        dedup_ttl_unit=args.dedup_ttl_unit,
        security_common_name=args.security_common_name,
        allowed_networks=args.allowed_networks,
    )

    # Wrap the callback in a default-route router
    router = HL7MessageRouter()
    router.add_route(
        channel_name='test',
        service_name='test',
        callback=callback_func,
        is_default=True,
        settings=settings,
    )

    # The listener takes its own settings from the environment, as a real server does
    listener_config = ListenerConfig.from_env(address)
    listener_config.read_buffer_size = args.read_buffer_size
    listener_config.max_message_size = args.max_msg_size

    server = HL7MLLPServer(listener_config, router)

    # Register SIGTERM handler for clean shutdown
    def _on_sigterm(signum:'int', frame:'object') -> 'None':
        server.stop()

    _ = signal.signal(signal.SIGTERM, _on_sigterm)

    # Print the readiness signal that the test harness waits for
    _ = sys.stdout.write(f'READY:{port}\n')
    _ = sys.stdout.flush()

    # Block on the server loop
    server.start()

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()
