# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import socket
from json import loads
from threading import Thread

# Zato
from zato.admin.web.views.outgoing.hl7.mllp import _Probe_Action_Tcp, _Probe_Action_Tls, _Probe_Details_Lexer, \
    wizard_test_action
from zato.common.ext.bunch import Bunch
from zato.common.util.tcp import get_free_port

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strdict

# ################################################################################################################################
# ################################################################################################################################

_Host = '127.0.0.1'

# How long the listener waits for the client to say something before concluding that it never will
_Listener_Read_Timeout = 0.5
_Accept_Timeout = 2

# A CA bundle path that is not there, which is enough to say TLS was asked for
_Missing_CA_Path = '/no/such/ca-bundle.pem'

# ################################################################################################################################
# ################################################################################################################################

class _Listener:
    """ A plain TCP listener that accepts one connection and records how many bytes arrived on it.
    """

    def __init__(self) -> 'None':
        self.port = get_free_port()
        self.received = b''

        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server.bind((_Host, self.port))
        self._server.listen(1)
        self._server.settimeout(_Accept_Timeout)

        self._thread = Thread(target=self._serve, daemon=True)
        self._thread.start()

    def _serve(self) -> 'None':
        conn, _ = self._server.accept()
        conn.settimeout(_Listener_Read_Timeout)
        try:
            self.received = conn.recv(1024)
        except socket.timeout:
            pass
        finally:
            conn.close()

    def close(self) -> 'None':
        self._thread.join(_Accept_Timeout)
        self._server.close()

# ################################################################################################################################
# ################################################################################################################################

def _build_request(address:'str', ca_path:'str'='') -> 'Bunch':
    """ What the wizard posts for a live check - the address, the framing and the TLS paths.
    """
    out = Bunch()
    out.method = 'POST'
    out.POST = {
        'address': address,
        'start_seq': '0b',
        'end_seq': '1c 0d',
        'tls_ca_path': ca_path,
        'tls_cert_path': '',
        'tls_key_path': '',
    }
    return out

# ################################################################################################################################

def _body(response:'any_') -> 'strdict':
    out = loads(response.content.decode('utf-8'))
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestWizardTestAction:
    """ The live check opens a connection and reports whether it could, with the details saying
    what it did and what came of it - never a traceback and never a message on the wire.
    """

    def test_a_listening_endpoint_answers_and_gets_no_message(self) -> 'None':

        listener = _Listener()
        address = f'{_Host}:{listener.port}'

        try:
            response = wizard_test_action(_build_request(address))
        finally:
            listener.close()

        body = _body(response)

        assert body['is_ok'] is True
        assert address in body['summary']
        assert 'answered in' in body['summary']
        assert body['details_lexer'] == _Probe_Details_Lexer

        details = loads(body['details'])
        assert details['address'] == address
        assert details['action'] == _Probe_Action_Tcp
        assert isinstance(details['elapsed_ms'], int)

        assert listener.received == b'', f'The check should have sent nothing, the listener got: {listener.received!r}'

# ################################################################################################################################

    def test_nothing_listening_is_reported_without_a_traceback(self) -> 'None':

        address = f'{_Host}:{get_free_port()}'
        response = wizard_test_action(_build_request(address))
        body = _body(response)

        assert body['is_ok'] is False
        assert body['summary'].startswith(f'{address} could not be reached - ')
        assert body['details_lexer'] == _Probe_Details_Lexer

        details = loads(body['details'])
        assert details['address'] == address
        assert details['action'] == _Probe_Action_Tcp
        assert details['error'], 'The error message should be in the details'

        assert 'Traceback' not in body['details']
        assert 'File "' not in body['details']

# ################################################################################################################################

    def test_a_ca_bundle_makes_it_a_tls_check(self) -> 'None':

        address = f'{_Host}:{get_free_port()}'
        response = wizard_test_action(_build_request(address, _Missing_CA_Path))
        body = _body(response)

        # A CA bundle that is not there cannot be loaded, which is what the check then reports
        assert body['is_ok'] is False

        details = loads(body['details'])
        assert details['action'] == _Probe_Action_Tls
        assert details['error']

# ################################################################################################################################
# ################################################################################################################################
