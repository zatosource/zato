# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import socket
import ssl
import threading

# pytest
import pytest

# Zato
from zato.common.as2.common import AS2Exception

# Zato
from .outconn_helpers import certificate_to_pem, key_to_pem, make_connection

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path
    Path = Path

    from .conftest import TestParties
    TestParties = TestParties

# ################################################################################################################################
# ################################################################################################################################

# The loopback address every test endpoint listens on, with the port left to the operating system.
_listen_address = '127.0.0.1'
_any_port = 0

# ################################################################################################################################
# ################################################################################################################################

class TestPing:

    def test_ping_connects_over_plain_http(self, parties:'TestParties') -> 'None':

        # A listening socket is all a plain HTTP ping needs.
        listener = socket.socket()
        listener.bind((_listen_address, _any_port))
        listener.listen(1)

        address = listener.getsockname()
        port = address[1]

        try:
            endpoint_url = f'http://{_listen_address}:{port}/as2'
            connection, _, _, _ = make_connection(parties, endpoint_url=endpoint_url)
            connection.ping()
        finally:
            listener.close()

# ################################################################################################################################

    def test_ping_runs_the_tls_handshake(self, parties:'TestParties', tmp_path:'Path') -> 'None':

        # The endpoint presents the receiver's certificate over TLS.
        certificate_path = tmp_path / 'endpoint-cert.pem'
        key_path = tmp_path / 'endpoint-key.pem'

        receiver_certificate = parties.receiver.signing_certificate_chain[0]

        certificate_pem = certificate_to_pem(receiver_certificate)
        key_pem = key_to_pem(parties.receiver.signing_key)

        _ = certificate_path.write_text(certificate_pem)
        _ = key_path.write_text(key_pem)

        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)

        certificate_file = str(certificate_path)
        key_file = str(key_path)

        context.load_cert_chain(certificate_file, key_file)

        listener = socket.socket()
        listener.bind((_listen_address, _any_port))
        listener.listen(1)

        address = listener.getsockname()
        port = address[1]

        def _serve_one_handshake() -> 'None':
            try:
                client_socket, _ = listener.accept()
                tls_socket = context.wrap_socket(client_socket, server_side=True)
                tls_socket.close()
            except OSError:
                pass

        server_thread = threading.Thread(target=_serve_one_handshake)
        server_thread.start()

        try:
            # The endpoint's certificate is self-issued for the test,
            # which is exactly what the verification toggle is for.
            options = {
                'endpoint_url': f'https://{_listen_address}:{port}/as2',
                'verify_tls': False,
            }

            connection, _, _, _ = make_connection(parties, **options)
            connection.ping()
        finally:
            server_thread.join()
            listener.close()

# ################################################################################################################################

    def test_ping_fails_when_nothing_listens(self, parties:'TestParties') -> 'None':

        # Bind a port and close it right away so nothing listens on it.
        listener = socket.socket()
        listener.bind((_listen_address, _any_port))

        address = listener.getsockname()
        port = address[1]

        listener.close()

        endpoint_url = f'http://{_listen_address}:{port}/as2'
        connection, _, _, _ = make_connection(parties, endpoint_url=endpoint_url)

        with pytest.raises(OSError):
            connection.ping()

# ################################################################################################################################

    def test_ping_fails_without_an_endpoint(self, parties:'TestParties') -> 'None':

        connection, _, _, _ = make_connection(parties, endpoint_url='')

        with pytest.raises(AS2Exception):
            connection.ping()

# ################################################################################################################################
# ################################################################################################################################
