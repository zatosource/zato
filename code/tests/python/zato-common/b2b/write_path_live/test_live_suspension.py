# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import ssl
from http.client import SERVICE_UNAVAILABLE
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from urllib.error import HTTPError
from urllib.request import Request, urlopen

# Zato
from certificates import generate_certificates
from live_db import start_child
from zato.common.audit_log.api import AuditEvent, AuditSource, event_table
from zato.common.b2b.common.address_state import AddressRegistry, AddressState, Default_Suspend_After_Failures, \
    SuspensionReason
from zato.common.b2b.common.clock import SystemClock
from zato.common.b2b.common.commit_group import GroupCommitWriter
from zato.common.b2b.ebms2.common import MSHService
from zato.common.b2b.ebms2.inbound import receive
from zato.common.b2b.ebms2.outbound import accept_response
from zato.common.b2b.ebms2.probe import build_ping, is_pong
from zato.common.test.b2b_cpa import new_settings
from zato.common.test.b2b_ebms2 import new_exchange, resolve, Start_Time
from zato.common.test.b2b_write_path import Server

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path
    from live_db import LiveDB
    from zato.common.b2b.ebms2.outbound import OutboundMessage
    from zato.common.test.b2b_ebms2 import Exchange
    from zato.common.test.b2b_pki import TestParties
    from zato.common.typing_ import strlist, strstrdict
    Exchange = Exchange
    LiveDB = LiveDB
    OutboundMessage = OutboundMessage
    Path = Path
    strlist = strlist
    strstrdict = strstrdict
    TestParties = TestParties

# ################################################################################################################################
# ################################################################################################################################

# How long the writer of a test waits between two commits, in milliseconds.
_interval_ms = 10

# How long a child and one request are waited for, in seconds.
_wait_seconds = 60

_listener_host = '127.0.0.1'
_path = '/ebms'

# ################################################################################################################################
# ################################################################################################################################

class _Partner:
    """ A partner behind an HTTPS listener that answers with 503 while it is unavailable, and receives
    the messages of an exchange once it is available again.
    """

    def __init__(self, exchange:'Exchange', server_cert:'str', server_key:'str') -> 'None':
        self.exchange = exchange
        self.is_available = False

        partner = self

        class _Handler(BaseHTTPRequestHandler):

            def do_POST(self) -> 'None':
                length = int(self.headers['Content-Length'])
                body = self.rfile.read(length)

                if not partner.is_available:
                    self.send_response(SERVICE_UNAVAILABLE)
                    self.end_headers()
                    return

                headers:'strstrdict' = {}
                for name, value in self.headers.items():
                    headers[name] = value

                receiver = partner.exchange.receiver
                result = receive(partner.exchange.agreement, receiver.local_keys, headers, body, receiver.receive_log,
                    partner.exchange.clock)

                response = result.response

                self.send_response(response.status_code)
                self.send_header('Content-Type', response.content_type)
                self.end_headers()
                _ = self.wfile.write(response.body)

            def log_message(self, *args:'object') -> 'None':
                pass

        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(server_cert, server_key)

        self.server = ThreadingHTTPServer((_listener_host, 0), _Handler)
        self.server.socket = context.wrap_socket(self.server.socket, server_side=True)

        port = self.server.server_address[1]
        self.address = f'https://localhost:{port}{_path}'

        self.thread = Thread(target=self.server.serve_forever, daemon=True)

    def start(self) -> 'None':
        self.thread.start()

    def stop(self) -> 'None':
        self.server.shutdown()
        self.server.server_close()

# ################################################################################################################################
# ################################################################################################################################

def _post_ping(partner:'_Partner', ping:'OutboundMessage', ca_cert:'str') -> 'None':
    """ Sends a Ping to the partner and passes the response back to it.
    """
    context = ssl.create_default_context(cafile=ca_cert)

    package = ping.package
    request = Request(partner.address, data=package.body, headers=package.headers, method='POST')

    try:
        with urlopen(request, timeout=_wait_seconds, context=context) as response:
            status_code = response.status
            headers = dict(response.headers.items())
            body = response.read()

    except HTTPError as e:
        status_code = e.code
        headers = dict(e.headers.items())
        body = e.read()

    _ = accept_response(ping, status_code, headers, body, partner.exchange.clock)

# ################################################################################################################################

def _event_types(database:'LiveDB') -> 'strlist':
    statement = event_table.select().order_by(event_table.c.id)

    out:'strlist' = []

    with database.engine.connect() as connection:
        for row in connection.execute(statement):
            out.append(row.event_type)

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestSuspension:
    """ An address that answers with 503 is suspended, stays suspended across a restart, and is resumed by a probe.
    """

    def test_suspend_and_resume(self, database:'LiveDB', parties:'TestParties', tmp_path:'Path') -> 'None':
        paths = generate_certificates(str(tmp_path))

        exchange = new_exchange(parties, new_settings(parties, Start_Time))

        partner = _Partner(exchange, paths.server_cert, paths.server_key)
        partner.start()

        # A process records the failures of its deliveries and ends ..
        child = start_child(database, 'fail-address', partner.address, paths.ca_cert, str(Default_Suspend_After_Failures))
        stdout, stderr = child.communicate(timeout=_wait_seconds)

        assert child.returncode == 0, stderr

        report = json.loads(stdout.strip().splitlines()[-1])

        assert report['state'] == AddressState.Suspended
        assert report['consecutive_failures'] == Default_Suspend_After_Failures

        # .. and the process started after it finds the address suspended.
        writer = GroupCommitWriter(database.engine, interval_ms=_interval_ms)
        registry = AddressRegistry(writer, AuditSource.EbMS2, Server, SystemClock())

        assert registry.load() == 1
        assert registry.is_suspended(partner.address)

        # A probe while the partner is still unavailable is not answered ..
        binding = resolve(exchange, MSHService.Ping, is_msh=True)

        ping = build_ping(exchange.agreement, exchange.sender.local_keys, binding, exchange.clock)
        _post_ping(partner, ping, paths.ca_cert)

        assert not registry.record_probe(partner.address, is_pong(ping))
        assert registry.is_suspended(partner.address)

        # .. and once it is available, the Pong resumes the address.
        partner.is_available = True

        ping = build_ping(exchange.agreement, exchange.sender.local_keys, binding, exchange.clock)
        _post_ping(partner, ping, paths.ca_cert)

        assert registry.record_probe(partner.address, is_pong(ping))

        record = registry.get(partner.address)

        assert record.state == AddressState.Active
        assert record.consecutive_failures == 0
        assert record.reason == SuspensionReason.Probe_Answered

        assert _event_types(database) == [AuditEvent.Delivery_Suspended, AuditEvent.Delivery_Resumed]

        writer.stop()
        partner.stop()

# ################################################################################################################################
# ################################################################################################################################
