# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import re
import shutil
import socket
import socketserver
import subprocess
import tempfile
import threading
import time
from pathlib import Path
from typing import Generator

# pytest
import pytest

# Zato
from mllp_live_util import end_sequence, sample_wellness_oru, start_sequence
from rest_echo_server import HTTPEchoHandler
from zato.common.hl7.mllp.haproxy import reload_haproxy, update_mllp_backend_port

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

routing_env_gen = Generator['RoutingEnv', None, None]

_haproxy_cfg_source = Path(__file__).resolve().parents[4] / 'zato-common' / 'src' / 'zato' / 'common' / 'pubsub' / 'server' / 'haproxy.cfg'

_haproxy_startup_timeout_seconds  = 5
_haproxy_shutdown_timeout_seconds = 3
_connect_timeout_seconds          = 3.0
_recv_timeout_seconds             = 3.0
_recv_buffer_size                 = 8192

# ################################################################################################################################
# ################################################################################################################################

_wellness_message_bytes = sample_wellness_oru()

# ################################################################################################################################
# ################################################################################################################################

def _find_free_port() -> 'int':
    """ Binds to port 0 to get an OS-assigned free port, then releases it.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('127.0.0.1', 0))
    port = sock.getsockname()[1]
    sock.close()
    return port

# ################################################################################################################################
# ################################################################################################################################

def _build_ack(control_id:'str') -> 'bytes':
    """ Builds a minimal MSA-only ACK for the given control ID.
    """
    ack = (
        f'MSH|^~\\&|EHR|Hospital|VitalMon|ICU|20260525100001||ACK^R01^ACK|ACK001|P|2.9\r'
        f'MSA|AA|{control_id}'
    )
    return ack.encode('utf-8')

# ################################################################################################################################
# ################################################################################################################################
# MLLP echo backend
# ################################################################################################################################
# ################################################################################################################################

class _MllpEchoHandler(socketserver.BaseRequestHandler):
    """ Reads MLLP-framed messages, records them, and responds with an MLLP-framed ACK.
    """

    def handle(self) -> 'None':

        data = b''

        while True:
            chunk = self.request.recv(_recv_buffer_size)
            if not chunk:
                break
            data += chunk

            # .. look for the end sequence ..
            end_pos = data.find(end_sequence)

            if end_pos != -1:

                # .. extract the payload, stripping 0x0B if present ..
                payload = data[:end_pos]

                if payload.startswith(start_sequence):
                    payload = payload[len(start_sequence):]

                # .. record the received message ..
                self.server.received_messages.append(payload)  # type: ignore[attr-defined]
                self.server.request_count += 1                 # type: ignore[attr-defined]

                # .. extract the control ID from MSH-10 ..
                msh_line = payload.split(b'\r')[0]
                msh_fields = msh_line.split(b'|')
                control_id = msh_fields[9].decode('utf-8') if len(msh_fields) > 9 else 'UNKNOWN'

                # .. send the ACK wrapped in MLLP framing ..
                ack_payload = _build_ack(control_id)
                framed_ack = start_sequence + ack_payload + end_sequence
                self.request.sendall(framed_ack)
                break

# ################################################################################################################################
# ################################################################################################################################

class _TrackingTCPServer(socketserver.TCPServer):
    """ TCP server with request counting and message recording.
    """

    allow_reuse_address = True

    def __init__(self, *args:'any_', **kwargs:'any_') -> 'None':
        super().__init__(*args, **kwargs)
        self.request_count = 0
        self.last_body = b''
        self.received_messages:'list[bytes]' = []

# ################################################################################################################################
# ################################################################################################################################
# HAProxy config builder
# ################################################################################################################################
# ################################################################################################################################

def _build_test_haproxy_cfg(
    tmp_dir:'str',
    frontend_port:'int',
    http_loopback_port:'int',
    http_backend_port:'int',
    mllp_backend_port:'int',
) -> 'str':
    """ Reads the production haproxy.cfg and rewrites ports for the test.
    Returns the path to the temp config file.
    """

    config_text = _haproxy_cfg_source.read_text()

    # .. strip sections we don't need ..
    config_text = re.sub(r'(?m)^# Dashboard frontend.*?(?=^# |\Z)', '', config_text, flags=re.DOTALL)
    config_text = re.sub(r'(?m)^backend dashboard_backend.*?(?=^# |\Z)', '', config_text, flags=re.DOTALL)
    config_text = re.sub(r'(?m)^userlist .*?(?=^# |\Z)', '', config_text, flags=re.DOTALL)
    config_text = re.sub(r'(?m)^listen stats.*', '', config_text, flags=re.DOTALL)

    # .. replace the main frontend port ..
    config_text = config_text.replace('bind 0.0.0.0:${Zato_Port_Load_Balancer}', f'bind 127.0.0.1:{frontend_port}')

    # .. replace the inspect delay placeholder with the production default ..
    config_text = config_text.replace('${Zato_Load_Balancer_Inspect_Delay}', '5s')

    # .. replace the http_internal loopback port ..
    config_text = config_text.replace('127.0.0.1:11225 send-proxy', f'127.0.0.1:{http_loopback_port} send-proxy')
    config_text = config_text.replace('127.0.0.1:11225 accept-proxy', f'127.0.0.1:{http_loopback_port} accept-proxy')

    # .. replace the HTTP backend server port ..
    config_text = re.sub(
        r'server server1 127\.0\.0\.1:\S+ check.*',
        f'server server1 127.0.0.1:{http_backend_port}',
        config_text,
    )

    # .. replace the MLLP backend server port ..
    config_text = re.sub(
        r'server mllp1 127\.0\.0\.1:\d+',
        f'server mllp1 127.0.0.1:{mllp_backend_port}',
        config_text,
    )

    # .. replace the blocked-paths file reference with /dev/null ..
    config_text = config_text.replace('/opt/zato/env/qs-1/blocked-paths.txt', '/dev/null')

    # .. drop the cpu-map line (may fail in unprivileged containers) ..
    config_text = re.sub(r'(?m)^\s+cpu-map.*\n', '', config_text)

    # .. reduce thread count to 1 for tests ..
    config_text = config_text.replace('nbthread 4', 'nbthread 1')

    config_path = os.path.join(tmp_dir, 'haproxy.cfg')

    with open(config_path, 'w') as config_file:
        _ = config_file.write(config_text)

    return config_path

# ################################################################################################################################
# ################################################################################################################################
# Test environment fixture
# ################################################################################################################################
# ################################################################################################################################

class RoutingEnv:
    """ Holds all the ports and server references for a test run.
    """
    frontend_port:'int'
    config_path:'str'
    http_backend:'_TrackingTCPServer'
    mllp_backend:'_TrackingTCPServer'
    haproxy_process:'subprocess.Popen[bytes]'

# ################################################################################################################################

@pytest.fixture(scope='module')
def haproxy_routing_env() -> 'routing_env_gen':
    """ Spins up HTTP and MLLP backends, writes a test haproxy.cfg, starts HAProxy,
    and yields a RoutingEnv with all ports. Tears everything down afterward.
    """

    env = RoutingEnv()
    tmp_dir = tempfile.mkdtemp(prefix='haproxy-routing-test-')

    # .. allocate all ports up front ..
    frontend_port      = _find_free_port()
    http_loopback_port = _find_free_port()
    http_backend_port  = _find_free_port()
    mllp_backend_port  = _find_free_port()

    env.frontend_port = frontend_port

    # .. start the HTTP echo backend ..
    http_server = _TrackingTCPServer(('127.0.0.1', http_backend_port), HTTPEchoHandler)
    http_thread = threading.Thread(target=http_server.serve_forever, daemon=True)
    http_thread.start()
    env.http_backend = http_server

    # .. start the MLLP echo backend ..
    mllp_server = _TrackingTCPServer(('127.0.0.1', mllp_backend_port), _MllpEchoHandler)
    mllp_thread = threading.Thread(target=mllp_server.serve_forever, daemon=True)
    mllp_thread.start()
    env.mllp_backend = mllp_server

    # .. write the test HAProxy config ..
    config_path = _build_test_haproxy_cfg(
        tmp_dir, frontend_port, http_loopback_port, http_backend_port, mllp_backend_port,
    )
    env.config_path = config_path

    # .. start HAProxy in master-worker mode, the same way production does,
    # so that configuration reloads via SIGHUP work ..
    haproxy_process = subprocess.Popen(
        ['haproxy', '-W', '-f', config_path, '-db'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    env.haproxy_process = haproxy_process

    # .. wait until HAProxy is accepting connections on the frontend port ..
    deadline = time.monotonic() + _haproxy_startup_timeout_seconds

    while time.monotonic() < deadline:
        try:
            probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            probe.settimeout(0.5)
            probe.connect(('127.0.0.1', frontend_port))
            probe.close()
            break
        except (ConnectionRefusedError, OSError):
            time.sleep(0.1)
    else:
        haproxy_process.kill()
        raise RuntimeError(f'HAProxy did not start within {_haproxy_startup_timeout_seconds}s')

    yield env

    # .. tear down ..
    haproxy_process.terminate()
    try:
        _ = haproxy_process.wait(timeout=_haproxy_shutdown_timeout_seconds)
    except subprocess.TimeoutExpired:
        haproxy_process.kill()
        _ = haproxy_process.wait()

    http_server.shutdown()
    mllp_server.shutdown()

    shutil.rmtree(tmp_dir, ignore_errors=True)

# ################################################################################################################################
# ################################################################################################################################
# Tests
# ################################################################################################################################
# ################################################################################################################################

class TestProtocolRouting:
    """ Verifies that HAProxy correctly routes REST and MLLP traffic
    arriving on the same port based on the first bytes of each connection.
    """

# ################################################################################################################################

    def test_http_post_routed_to_http_backend(self, haproxy_routing_env:'RoutingEnv') -> 'None':
        """ A POST request sent to the frontend port must reach the HTTP backend
        and the body must be echoed back byte-for-byte.
        """

        body = b'{"test": "hello"}'

        request = (
            f'POST /test HTTP/1.1\r\n'
            f'Host: 127.0.0.1:{haproxy_routing_env.frontend_port}\r\n'
            f'Content-Length: {len(body)}\r\n'
            f'Content-Type: application/json\r\n'
            f'Connection: close\r\n'
            f'\r\n'
        ).encode('utf-8') + body

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(_connect_timeout_seconds)
        sock.connect(('127.0.0.1', haproxy_routing_env.frontend_port))
        sock.sendall(request)

        response = b''
        while True:
            chunk = sock.recv(_recv_buffer_size)
            if not chunk:
                break
            response += chunk
        sock.close()

        # .. verify the response ..
        response_text = response.decode('utf-8', errors='replace')
        assert 'HTTP/1.1 200' in response_text, f'Expected 200 OK, got: {response_text[:200]}'
        assert response.endswith(body), f'Body not echoed back: {response[-100:]}'

# ################################################################################################################################

    def test_mllp_framed_routed_to_mllp_backend(self, haproxy_routing_env:'RoutingEnv') -> 'None':
        """ An MLLP-framed HL7v2 message sent to the frontend port must reach the MLLP backend.
        The ACK must contain MSA|AA and the original control ID.
        """

        framed = start_sequence + _wellness_message_bytes + end_sequence

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(_connect_timeout_seconds)
        sock.connect(('127.0.0.1', haproxy_routing_env.frontend_port))
        sock.sendall(framed)

        response = b''
        sock.settimeout(_recv_timeout_seconds)

        while True:
            try:
                chunk = sock.recv(_recv_buffer_size)
                if not chunk:
                    break
                response += chunk
                if end_sequence in response:
                    break
            except socket.timeout:
                break
        sock.close()

        # .. verify the ACK ..
        assert start_sequence in response, 'ACK missing start sequence'
        assert end_sequence in response, 'ACK missing end sequence'

        ack_start = response.index(start_sequence) + len(start_sequence)
        ack_end = response.index(end_sequence)
        ack_text = response[ack_start:ack_end].decode('utf-8')

        assert 'MSA|AA|WLN001' in ack_text, f'ACK does not contain MSA|AA|WLN001: {ack_text}'

        # .. verify the MLLP backend recorded the full message ..
        mllp_backend = haproxy_routing_env.mllp_backend
        assert mllp_backend.request_count >= 1, 'MLLP backend did not receive any messages'

        received = mllp_backend.received_messages[-1]
        assert b'MSH|' in received
        assert b'OBX|1|NM|8310-5^Body temperature^LN||36.8|Cel|36.1-37.2|N|||F' in received

# ################################################################################################################################

    def test_mllp_delayed_first_byte_routed_to_mllp_backend(self, haproxy_routing_env:'RoutingEnv') -> 'None':
        """ A client that connects and only sends its first byte after a delay,
        as any remote sender does after one network round-trip, must still be
        routed to the MLLP backend rather than falling through to HTTP.
        """

        framed = start_sequence + _wellness_message_bytes + end_sequence

        count_before = haproxy_routing_env.mllp_backend.request_count

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(_connect_timeout_seconds)
        sock.connect(('127.0.0.1', haproxy_routing_env.frontend_port))

        # .. wait a full second before sending anything, which is far beyond
        # the previous 10ms inspect delay but well within the current one ..
        time.sleep(1)
        sock.sendall(framed)

        response = b''
        sock.settimeout(_recv_timeout_seconds)

        while True:
            try:
                chunk = sock.recv(_recv_buffer_size)
                if not chunk:
                    break
                response += chunk
                if end_sequence in response:
                    break
            except socket.timeout:
                break
        sock.close()

        # .. verify the MLLP backend received the message despite the delay ..
        assert haproxy_routing_env.mllp_backend.request_count > count_before, \
            'MLLP backend did not receive the delayed message'

        # .. verify we got a valid ACK back ..
        ack_start = response.find(start_sequence)
        ack_end = response.find(end_sequence)

        assert ack_start != -1 and ack_end != -1, f'No MLLP-framed ACK received: {response!r}'

        ack_text = response[ack_start + len(start_sequence):ack_end].decode('utf-8')
        assert 'MSA|AA|WLN001' in ack_text, f'ACK missing MSA|AA|WLN001: {ack_text}'

# ################################################################################################################################

    def test_mllp_bare_msh_routed_to_mllp_backend(self, haproxy_routing_env:'RoutingEnv') -> 'None':
        """ A bare MSH message (no 0x0B prefix) sent to the frontend port
        must still be routed to the MLLP backend and produce a valid ACK.
        """

        bare_message = _wellness_message_bytes + end_sequence

        count_before = haproxy_routing_env.mllp_backend.request_count

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(_connect_timeout_seconds)
        sock.connect(('127.0.0.1', haproxy_routing_env.frontend_port))
        sock.sendall(bare_message)

        response = b''
        sock.settimeout(_recv_timeout_seconds)

        while True:
            try:
                chunk = sock.recv(_recv_buffer_size)
                if not chunk:
                    break
                response += chunk
                if end_sequence in response:
                    break
            except socket.timeout:
                break
        sock.close()

        # .. verify the MLLP backend received the message ..
        assert haproxy_routing_env.mllp_backend.request_count > count_before, \
            'MLLP backend did not receive the bare MSH message'

        # .. verify we got a valid ACK back ..
        ack_start = response.find(start_sequence)
        ack_end = response.find(end_sequence)

        assert ack_start != -1 and ack_end != -1, f'No MLLP-framed ACK received: {response!r}'

        ack_text = response[ack_start + len(start_sequence):ack_end].decode('utf-8')
        assert 'MSA|AA|WLN001' in ack_text, f'ACK missing MSA|AA|WLN001: {ack_text}'

# ################################################################################################################################

    def test_mllp_message_content_preserved(self, haproxy_routing_env:'RoutingEnv') -> 'None':
        """ The MLLP backend must receive exactly the same bytes that were sent,
        with all segments (MSH, PID, OBR, OBX) present and intact.
        """

        framed = start_sequence + _wellness_message_bytes + end_sequence

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(_connect_timeout_seconds)
        sock.connect(('127.0.0.1', haproxy_routing_env.frontend_port))
        sock.sendall(framed)

        sock.settimeout(_recv_timeout_seconds)

        # .. drain the ACK so the connection completes cleanly ..
        response = b''
        while True:
            try:
                chunk = sock.recv(_recv_buffer_size)
                if not chunk:
                    break
                response += chunk
                if end_sequence in response:
                    break
            except socket.timeout:
                break
        sock.close()

        # .. verify the backend received the exact bytes ..
        received = haproxy_routing_env.mllp_backend.received_messages[-1]
        assert received == _wellness_message_bytes, (
            f'Message content mismatch.\n'
            f'Sent:     {_wellness_message_bytes!r}\n'
            f'Received: {received!r}'
        )

        # .. verify all segments are present ..
        received_text = received.decode('utf-8')
        segments = received_text.split('\r')

        segment_ids = [seg.split('|')[0] for seg in segments if seg]
        assert 'MSH' in segment_ids
        assert 'PID' in segment_ids
        assert 'OBR' in segment_ids
        assert 'OBX' in segment_ids

# ################################################################################################################################

    def test_http_not_seen_by_mllp_backend(self, haproxy_routing_env:'RoutingEnv') -> 'None':
        """ After sending an HTTP request, the MLLP backend request count must not increase.
        """

        count_before = haproxy_routing_env.mllp_backend.request_count

        body = b'isolation-check'
        request = (
            f'GET /isolation HTTP/1.1\r\n'
            f'Host: 127.0.0.1:{haproxy_routing_env.frontend_port}\r\n'
            f'Content-Length: {len(body)}\r\n'
            f'Connection: close\r\n'
            f'\r\n'
        ).encode('utf-8') + body

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(_connect_timeout_seconds)
        sock.connect(('127.0.0.1', haproxy_routing_env.frontend_port))
        sock.sendall(request)

        # .. drain the response ..
        while True:
            chunk = sock.recv(_recv_buffer_size)
            if not chunk:
                break
        sock.close()

        assert haproxy_routing_env.mllp_backend.request_count == count_before, \
            'MLLP backend received traffic from an HTTP request'

# ################################################################################################################################

    def test_mllp_not_seen_by_http_backend(self, haproxy_routing_env:'RoutingEnv') -> 'None':
        """ After sending an MLLP message, the HTTP backend request count must not increase.
        """

        count_before = haproxy_routing_env.http_backend.request_count

        framed = start_sequence + _wellness_message_bytes + end_sequence

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(_connect_timeout_seconds)
        sock.connect(('127.0.0.1', haproxy_routing_env.frontend_port))
        sock.sendall(framed)

        sock.settimeout(_recv_timeout_seconds)

        # .. drain the ACK ..
        while True:
            try:
                chunk = sock.recv(_recv_buffer_size)
                if not chunk:
                    break
                if end_sequence in chunk:
                    break
            except socket.timeout:
                break
        sock.close()

        assert haproxy_routing_env.http_backend.request_count == count_before, \
            'HTTP backend received traffic from an MLLP message'

# ################################################################################################################################
# ################################################################################################################################

class TestConfigReload:
    """ Verifies the runtime reload path used by MLLP channels - the configuration file
    is rewritten with a new backend port and the HAProxy master process is signaled
    to reload, after which MLLP traffic must reach the new backend.

    This class must run after TestProtocolRouting because it modifies
    the shared HAProxy configuration.
    """

# ################################################################################################################################

    def test_reload_switches_mllp_backend(self, haproxy_routing_env:'RoutingEnv') -> 'None':
        """ After update_mllp_backend_port and reload_haproxy, new MLLP connections
        must be forwarded to the new backend port.
        """

        # Start a second MLLP backend on a fresh port ..
        new_backend_port = _find_free_port()

        new_backend = _TrackingTCPServer(('127.0.0.1', new_backend_port), _MllpEchoHandler)
        new_backend_thread = threading.Thread(target=new_backend.serve_forever, daemon=True)
        new_backend_thread.start()

        # .. rewrite the configuration the same way the channel code does at runtime ..
        update_mllp_backend_port(haproxy_routing_env.config_path, new_backend_port)

        # .. signal the HAProxy master to reload ..
        was_signaled = reload_haproxy(haproxy_routing_env.config_path)
        assert was_signaled, 'reload_haproxy did not signal any process'

        framed = start_sequence + _wellness_message_bytes + end_sequence

        # .. keep sending until the new backend sees the message - the reload
        # takes a moment and the frontend may briefly refuse connections ..
        deadline = time.monotonic() + _haproxy_startup_timeout_seconds

        while time.monotonic() < deadline:

            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(_connect_timeout_seconds)
                sock.connect(('127.0.0.1', haproxy_routing_env.frontend_port))
                sock.sendall(framed)

                # .. drain the ACK so the connection completes cleanly ..
                sock.settimeout(_recv_timeout_seconds)
                response = b''

                while True:
                    try:
                        chunk = sock.recv(_recv_buffer_size)
                        if not chunk:
                            break
                        response += chunk
                        if end_sequence in response:
                            break
                    except socket.timeout:
                        break
                sock.close()

            except (ConnectionRefusedError, OSError):
                pass

            if new_backend.request_count >= 1:
                break

            time.sleep(0.2)

        assert new_backend.request_count >= 1, 'New MLLP backend did not receive any messages after the reload'

        new_backend.shutdown()

# ################################################################################################################################
# ################################################################################################################################
