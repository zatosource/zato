# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import re
import socket
import socketserver
import ssl
import subprocess
import sys
import threading
import time
from pathlib import Path

# colorama
from colorama import Fore, Style, init as colorama_init

# Zato
from mllp_proxy_header import build_proxy_header
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

colorama_init(autoreset=True)

# ################################################################################################################################
# ################################################################################################################################

# Standard MLLP framing bytes
start_sequence = b'\x0b'
end_sequence   = b'\x1c\x0d'

# Path to the test server script
_test_server_script = str(Path(__file__).parent / 'mllp_test_server.py')

# How long to wait for the server to print READY
_server_startup_timeout_seconds = 10

# How long to wait for the server process to terminate after SIGTERM
_server_shutdown_timeout_seconds = 5

# What the stand-in load balancer reports about a sender unless a test asks for something else
default_sender_ip          = '203.0.113.10'
default_sender_common_name = ''

_relay_buffer_size = 65536

# ################################################################################################################################
# ################################################################################################################################
# Load balancer stand-in
# ################################################################################################################################
# ################################################################################################################################

class _RelayHandler(socketserver.BaseRequestHandler):
    """ Carries one connection through to the listener, announcing the sender first, which is
    the whole of what the load balancer does for MLLP. Where it was given a TLS context it
    terminates TLS too and reports the name on the certificate it verified.
    """

    def handle(self) -> 'None':

        server = cast_('any_', self.server)
        common_name = server.sender_common_name
        downstream = self.request

        if server.ssl_context:

            try:
                downstream = server.ssl_context.wrap_socket(downstream, server_side=True)
            except ssl.SSLError:

                # A sender that cannot be verified never reaches the listener at all
                return

            # The name on the verified certificate is the sender's identity from here on
            peer_certificate = downstream.getpeercert()

            if peer_certificate:
                common_name = _common_name_from_certificate(peer_certificate)

        upstream = socket.create_connection(('127.0.0.1', server.listener_port))

        # The listener has no other way of knowing who is calling
        upstream.sendall(build_proxy_header(server.sender_ip, self.client_address[1], common_name))

        # Each direction runs on its own thread so neither has to wait on the other
        downstream_thread = threading.Thread(target=_pump, args=(upstream, downstream), daemon=True)
        downstream_thread.start()

        _pump(downstream, upstream)
        downstream_thread.join()

        upstream.close()

# ################################################################################################################################

def _common_name_from_certificate(peer_certificate:'any_') -> 'str':
    """ Digs the common name out of the subject of a verified certificate.
    """

    for part in peer_certificate['subject']:
        for name, value in part:
            if name == 'commonName':
                return value

    return ''

# ################################################################################################################################

def _pump(source:'socket.socket', destination:'socket.socket') -> 'None':
    """ Moves bytes one way until the source has no more, then tells the destination as much.
    """

    while True:

        try:
            chunk = source.recv(_relay_buffer_size)
        except OSError:
            break

        if not chunk:
            break

        try:
            destination.sendall(chunk)
        except OSError:
            break

    # Without this the far side waits out its own timeout instead of seeing the close
    try:
        destination.shutdown(socket.SHUT_WR)
    except OSError:
        pass

# ################################################################################################################################

class _Relay(socketserver.ThreadingTCPServer):
    """ Stands in for the load balancer in front of a listener under test.
    """

    allow_reuse_address = True
    daemon_threads = True

    def __init__(
        self,
        listener_port:'int',
        sender_ip:'str',
        sender_common_name:'str',
        ssl_context:'ssl.SSLContext | None'=None,
    ) -> 'None':
        super().__init__(('127.0.0.1', 0), _RelayHandler)
        self.listener_port = listener_port
        self.sender_ip = sender_ip
        self.sender_common_name = sender_common_name
        self.ssl_context = ssl_context

# ################################################################################################################################

# Which relay fronts which server process, so that stopping the one stops the other
_relays:'dict[int, _Relay]' = {}

# ################################################################################################################################

def announce_sender(sock:'socket.socket', sender_ip:'str'=default_sender_ip, common_name:'str'='') -> 'None':
    """ Says who is calling on a connection made straight to a listener, which is what a load
    balancer would otherwise have done.
    """
    sock.sendall(build_proxy_header(sender_ip, sock.getsockname()[1], common_name))

# ################################################################################################################################
# ################################################################################################################################
# Server process helpers
# ################################################################################################################################
# ################################################################################################################################

def start_server(**overrides:'object') -> 'tuple[subprocess.Popen, int]':
    """ Starts the MLLP test server as a subprocess and waits for the READY signal. Puts a
    stand-in for the load balancer in front of it and returns that port, since a listener is
    never reached directly.
    """

    # What the stand-in says about the sender, which is not the server's own business
    sender_ip = cast_('str', overrides.pop('sender_ip', default_sender_ip))
    sender_common_name = cast_('str', overrides.pop('sender_common_name', default_sender_common_name))
    ssl_context = cast_('any_', overrides.pop('ssl_context', None))

    # Measuring the listener means not measuring anything put in front of it
    use_relay = cast_('bool', overrides.pop('use_relay', True))

    # What the listener reads its own settings from, as against what any one channel brings
    listener_env = cast_('any_', overrides.pop('listener_env', None))

    command = [sys.executable, _test_server_script, '--port', '0']

    for key, value in overrides.items():

        # Convert a Python snake_case kwarg to a CLI --kebab-case argument ..
        key_dashed = key.replace('_', '-')
        cli_key = '--' + key_dashed

        # .. boolean toggles use the --no- prefix for False ..
        if isinstance(value, bool):
            if not value:
                cli_key = '--no-' + key_dashed
            command.append(cli_key)

        # .. while everything else is passed as a value following its key.
        else:
            value_text = str(value)
            command.append(cli_key)
            command.append(value_text)

    process_env = dict(os.environ)

    if listener_env:
        process_env.update(listener_env)

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env=process_env,
    )

    # Read stdout until we see the READY line
    deadline = time.monotonic() + _server_startup_timeout_seconds
    port = 0
    stdout = cast_('any_', process.stdout)

    for line in stdout:

        stripped_line = line.strip()
        match = re.match(r'^READY:(\d+)$', stripped_line)

        if match:
            port_text = match.group(1)
            port = int(port_text)
            break

        if time.monotonic() > deadline:
            process.kill()
            raise Exception(f'MLLP test server did not print READY within {_server_startup_timeout_seconds}s')

    if port == 0:
        process.kill()
        raise Exception('MLLP test server exited before printing READY')

    if not use_relay:
        return process, port

    relay = _Relay(port, sender_ip, sender_common_name, ssl_context)
    relay_thread = threading.Thread(target=relay.serve_forever, daemon=True)
    relay_thread.start()

    _relays[id(process)] = relay

    return process, relay.server_address[1]

# ################################################################################################################################

def stop_server(process:'subprocess.Popen') -> 'None':
    """ Sends SIGTERM to the server process and waits for it to exit.
    Sends SIGKILL if it does not exit in time.
    """

    relay = _relays.pop(id(process), None)

    if relay:
        relay.shutdown()
        relay.server_close()

    process.terminate()

    try:
        _ = process.wait(timeout=_server_shutdown_timeout_seconds)
    except subprocess.TimeoutExpired:
        process.kill()
        _ = process.wait()

# ################################################################################################################################
# ################################################################################################################################
# Sample HL7 messages
# ################################################################################################################################
# ################################################################################################################################

def sample_adt_a01(control_id:'str'='CTRL001') -> 'bytes':
    """ Returns a well-formed ADT^A01 message as bytes.
    """
    message = (
        f'MSH|^~\\&|SendApp|SendFac|RecvApp|RecvFac|20230101120000||ADT^A01|{control_id}|P|2.5\r'
        'EVN|A01|20230101120000\r'
        'PID|||12345^^^MRN||Doe^John||19800101|M\r'
        'PV1||I|ICU^Room1'
    )

    out = message.encode('utf-8')
    return out

# ################################################################################################################################

def sample_oru_r01(control_id:'str'='CTRL002') -> 'bytes':
    """ Returns a well-formed ORU^R01 message as bytes.
    """
    message = (
        f'MSH|^~\\&|LabSys|LabFac|OrderSys|OrderFac|20230101130000||ORU^R01|{control_id}|P|2.5\r'
        'PID|||67890^^^MRN||Smith^Jane||19900515|F\r'
        'OBR|1||LAB001|CBC^Complete Blood Count\r'
        'OBX|1|NM|WBC^White Blood Count||7.5|10*3/uL|4.5-11.0|N|||F'
    )

    out = message.encode('utf-8')
    return out

# ################################################################################################################################

def sample_wellness_oru() -> 'bytes':
    """ Returns a wellness ORU^R01 message with body temperature as bytes.
    """
    message = (
        'MSH|^~\\&|VitalMon|ICU|EHR|Hospital|20260525100000||ORU^R01^ORU_R01|WLN001|P|2.9\r'
        'PID|1||PAT001^^^Hosp^MR||Garcia^Maria||19750812|F\r'
        'OBR|1||VIT001|VS^Vital Signs\r'
        'OBX|1|NM|8310-5^Body temperature^LN||36.8|Cel|36.1-37.2|N|||F'
    )

    out = message.encode('utf-8')
    return out

# ################################################################################################################################
# ################################################################################################################################
# Performance logging helper
# ################################################################################################################################
# ################################################################################################################################

# How wide the dot-padded label column is
_perf_label_width = 40

# The minimum number of dots between a label and its value
_perf_min_dots = 3

# ################################################################################################################################

def perf_log(label:'str', value:'float', unit:'str', threshold:'float'=0.0) -> 'None':
    """ Prints a colorama-formatted performance result line.

    Format: [PERF] Label ............. Value unit [PASS/FAIL]
    """

    # Build the dot-padded label ..
    dots_needed = _perf_label_width - len(label)

    if dots_needed < _perf_min_dots:
        dots_needed = _perf_min_dots

    dots = '.' * dots_needed

    prefix = f'{Fore.CYAN}{Style.BRIGHT}[PERF]{Style.RESET_ALL}'
    padded_label = f' {label} {Fore.WHITE}{Style.DIM}{dots}{Style.RESET_ALL} '

    # .. color the value red or green depending on the threshold ..
    if threshold > 0.0:

        if value < threshold:
            colored_value = f'{Fore.RED}{Style.BRIGHT}{value:,.1f}{Style.RESET_ALL}'
            suffix = f' {Fore.RED}{Style.BRIGHT}[FAIL]{Style.RESET_ALL}'
        else:
            colored_value = f'{Fore.GREEN}{Style.BRIGHT}{value:,.1f}{Style.RESET_ALL}'
            suffix = f' {Fore.GREEN}{Style.BRIGHT}[PASS]{Style.RESET_ALL}'

    # .. without a threshold, there is no pass or fail indicator ..
    else:
        colored_value = f'{Fore.GREEN}{Style.BRIGHT}{value:,.1f}{Style.RESET_ALL}'
        suffix = ''

    # .. and now we can print the whole line.
    unit_display = f' {Fore.WHITE}{unit}{Style.RESET_ALL}'
    print(f'{prefix}{padded_label}{colored_value}{unit_display}{suffix}')

# ################################################################################################################################
# ################################################################################################################################
