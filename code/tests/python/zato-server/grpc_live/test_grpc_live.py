# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.grpc_live')

_test_customer = 'Test Customer Inc.'
_invoice_amount_cents = 12500

# ################################################################################################################################
# ################################################################################################################################

def _reset_server_expectations() -> 'None':
    """ Makes the test server accept calls without credentials.
    """
    from _grpc_server import TestServerConfig

    TestServerConfig.expected_authorization = None
    TestServerConfig.expected_apikey_header = None
    TestServerConfig.expected_apikey_value = None

# ################################################################################################################################
# ################################################################################################################################

class _AdminClient:
    """ Minimal admin client for invoking Zato services.
    """

    def __init__(self, base_url:'str', password:'str') -> 'None':
        self.base_url = base_url
        self.password = password

    def invoke(self, service_name:'str', payload:'anydict') -> 'anydict':
        from base64 import b64encode
        from urllib.error import HTTPError
        from urllib.request import Request, urlopen

        url = f'{self.base_url}/zato/api/invoke/{service_name}'
        body = json.dumps(payload).encode()

        credentials = f'admin.invoke:{self.password}'
        auth = b64encode(credentials.encode()).decode()

        request = Request(url, data=body, method='POST')
        request.add_header('Authorization', f'Basic {auth}')
        request.add_header('Content-Type', 'application/json')

        try:
            with urlopen(request) as response:
                raw = response.read()
        except HTTPError as error:
            raw = error.read()
            error_text = raw.decode('utf-8', errors='replace')
            raise Exception(f'{service_name} returned HTTP {error.code}: {error_text}')

        if not raw:
            return {}

        out = json.loads(raw)
        return out

# ################################################################################################################################
# ################################################################################################################################

class TestGRPCCallShapes:

    def _get_client(self, zato_server:'anydict') -> '_AdminClient':
        return _AdminClient(zato_server['base_url'], zato_server['invoke_password'])

# ################################################################################################################################

    def test_unary_with_own_stub_modules(self, zato_server:'anydict') -> 'None':
        """ Unary call through the connection that uses the user's pre-generated stub modules.
        """
        _reset_server_expectations()

        client = self._get_client(zato_server)
        result = client.invoke('test.grpc.get-invoice', {
            'conn_name': 'test.grpc.stubs',
            'invoice_id': 'inv-123',
        })

        assert result['invoice_id'] == 'inv-123'
        assert result['customer'] == _test_customer
        assert result['amount_cents'] == _invoice_amount_cents

# ################################################################################################################################

    def test_unary_with_proto_path_codegen(self, zato_server:'anydict') -> 'None':
        """ Unary call through the connection whose stubs the server generated out of the .proto file.
        """
        _reset_server_expectations()

        client = self._get_client(zato_server)
        result = client.invoke('test.grpc.get-invoice', {
            'conn_name': 'test.grpc.proto',
            'invoice_id': 'inv-456',
        })

        assert result['invoice_id'] == 'inv-456'
        assert result['customer'] == _test_customer

# ################################################################################################################################

    def test_server_streaming(self, zato_server:'anydict') -> 'None':
        """ A server-streaming call yields responses through a generator, never a list.
        """
        _reset_server_expectations()

        client = self._get_client(zato_server)
        result = client.invoke('test.grpc.list-invoices', {
            'conn_name': 'test.grpc.stubs',
            'max_items': 5,
        })

        assert result['is_generator'] is True

        invoices = result['invoices']
        assert len(invoices) == 5
        assert invoices[0]['invoice_id'] == 'inv-0'
        assert invoices[4]['invoice_id'] == 'inv-4'
        assert invoices[4]['amount_cents'] == _invoice_amount_cents + 4

# ################################################################################################################################

    def test_client_streaming(self, zato_server:'anydict') -> 'None':
        """ A client-streaming call sends a generator of requests and gets one response back.
        """
        _reset_server_expectations()

        client = self._get_client(zato_server)
        result = client.invoke('test.grpc.submit-payments', {
            'conn_name': 'test.grpc.stubs',
            'payments': [
                {'invoice_id': 'inv-1', 'amount_cents': 100},
                {'invoice_id': 'inv-2', 'amount_cents': 250},
                {'invoice_id': 'inv-3', 'amount_cents': 400},
            ],
        })

        assert result['payment_count'] == 3
        assert result['total_cents'] == 750

# ################################################################################################################################

    def test_bidirectional_streaming(self, zato_server:'anydict') -> 'None':
        """ A bidirectional call streams both ways.
        """
        _reset_server_expectations()

        client = self._get_client(zato_server)
        result = client.invoke('test.grpc.reconcile-payments', {
            'conn_name': 'test.grpc.stubs',
            'payments': [
                {'invoice_id': 'inv-1', 'amount_cents': 100},
                {'invoice_id': 'inv-2', 'amount_cents': 250},
            ],
        })

        receipts = result['receipts']
        assert len(receipts) == 2
        assert receipts[0] == {'invoice_id': 'inv-1', 'is_settled': True}
        assert receipts[1] == {'invoice_id': 'inv-2', 'is_settled': True}

# ################################################################################################################################
# ################################################################################################################################

class TestGRPCSecurity:

    def _get_client(self, zato_server:'anydict') -> '_AdminClient':
        return _AdminClient(zato_server['base_url'], zato_server['invoke_password'])

# ################################################################################################################################

    def test_basic_auth(self, zato_server:'anydict') -> 'None':
        """ The basic_auth connection sends the correct authorization metadata.
        """
        from _grpc_server import TestServerConfig

        _reset_server_expectations()
        TestServerConfig.expected_authorization = zato_server['basic_auth_header']

        client = self._get_client(zato_server)
        result = client.invoke('test.grpc.get-invoice', {
            'conn_name': 'test.grpc.basic_auth',
            'invoice_id': 'inv-ba',
        })

        assert result['invoice_id'] == 'inv-ba'

# ################################################################################################################################

    def test_apikey(self, zato_server:'anydict') -> 'None':
        """ The apikey connection sends the API key in the header the definition names.
        """
        from _grpc_server import TestServerConfig

        _reset_server_expectations()
        TestServerConfig.expected_apikey_header = 'X-API-Key'
        TestServerConfig.expected_apikey_value = zato_server['apikey_value']

        client = self._get_client(zato_server)
        result = client.invoke('test.grpc.get-invoice', {
            'conn_name': 'test.grpc.apikey',
            'invoice_id': 'inv-ak',
        })

        assert result['invoice_id'] == 'inv-ak'

# ################################################################################################################################

    def test_no_credentials_is_unauthenticated(self, zato_server:'anydict') -> 'None':
        """ A connection without a security definition fails when the server demands credentials.
        """
        from _grpc_server import TestServerConfig

        _reset_server_expectations()
        TestServerConfig.expected_authorization = zato_server['basic_auth_header']

        client = self._get_client(zato_server)

        try:
            _ = client.invoke('test.grpc.get-invoice', {
                'conn_name': 'test.grpc.stubs',
                'invoice_id': 'inv-noauth',
            })
        except Exception as error:
            assert 'UNAUTHENTICATED' in str(error)
        else:
            raise AssertionError('Expected an UNAUTHENTICATED error')
        finally:
            _reset_server_expectations()

# ################################################################################################################################
# ################################################################################################################################

class TestGRPCTLS:

    def _get_client(self, zato_server:'anydict') -> '_AdminClient':
        return _AdminClient(zato_server['base_url'], zato_server['invoke_password'])

# ################################################################################################################################

    def test_tls_unary(self, zato_server:'anydict') -> 'None':
        """ A unary call over the TLS connection, verified against the test CA certificate.
        """
        _reset_server_expectations()

        client = self._get_client(zato_server)
        result = client.invoke('test.grpc.get-invoice', {
            'conn_name': 'test.grpc.tls',
            'invoice_id': 'inv-tls',
        })

        assert result['invoice_id'] == 'inv-tls'
        assert result['customer'] == _test_customer

# ################################################################################################################################
# ################################################################################################################################

class TestGRPCPing:

    def _get_client(self, zato_server:'anydict') -> '_AdminClient':
        return _AdminClient(zato_server['base_url'], zato_server['invoke_password'])

# ################################################################################################################################

    def test_ping(self, zato_server:'anydict') -> 'None':
        """ Pinging a connection waits until the channel is ready.
        """
        _reset_server_expectations()

        client = self._get_client(zato_server)
        result = client.invoke('test.grpc.ping', {
            'conn_name': 'test.grpc.stubs',
        })

        assert result['alive'] is True

# ################################################################################################################################
# ################################################################################################################################

class TestGRPCRebuild:

    def _get_client(self, zato_server:'anydict') -> '_AdminClient':
        return _AdminClient(zato_server['base_url'], zato_server['invoke_password'])

# ################################################################################################################################

    def test_rebuild_after_reimport(self, zato_server:'anydict') -> 'None':
        """ Re-importing enmasse triggers edit events that rebuild the wrappers,
        including a fresh protoc run for the proto_path connection - calls must still work afterwards.
        """
        import subprocess

        _reset_server_expectations()

        zato_bin = os.path.join(os.environ['ZATO_TEST_BASE_DIR'], 'code', 'bin', 'zato')
        server_directory = zato_server['server_directory']
        rendered_path = os.path.join(os.path.dirname(server_directory), 'enmasse.yaml')

        result = subprocess.run(
            [zato_bin, 'enmasse', '--import', '--input', rendered_path, server_directory],
            capture_output=True, text=True, check=False, timeout=180)

        assert result.returncode == 0, f'enmasse re-import failed:\nstdout: {result.stdout}\nstderr: {result.stderr}'

        client = self._get_client(zato_server)

        # Both stub sources still work after the rebuild
        for conn_name in ('test.grpc.stubs', 'test.grpc.proto'):
            invoke_result = client.invoke('test.grpc.get-invoice', {
                'conn_name': conn_name,
                'invoice_id': 'inv-rebuilt',
            })

            assert invoke_result['invoice_id'] == 'inv-rebuilt'

# ################################################################################################################################
# ################################################################################################################################

class TestGRPCExceptionMapping:
    """ Unhandled gRPC errors bubbling up through a REST channel return the HTTP status
    matching the gRPC status code, not a generic 500.
    """

    def _invoke_channel(self, zato_server:'anydict', invoice_id:'str') -> 'tuple':
        """ Calls the REST channel and returns (HTTP status, response text).
        """
        from urllib.error import HTTPError
        from urllib.request import Request, urlopen

        url = f'{zato_server["base_url"]}/test/grpc/invoice'
        body = json.dumps({'invoice_id': invoice_id}).encode()

        request = Request(url, data=body, method='POST')
        request.add_header('Content-Type', 'application/json')

        try:
            with urlopen(request) as response:
                out = (response.status, response.read().decode('utf-8', errors='replace'))
        except HTTPError as error:
            out = (error.code, error.read().decode('utf-8', errors='replace'))

        return out

# ################################################################################################################################

    def test_success_is_200(self, zato_server:'anydict') -> 'None':
        _reset_server_expectations()

        status, text = self._invoke_channel(zato_server, 'inv-ok')

        assert status == 200
        assert json.loads(text)['invoice_id'] == 'inv-ok'

# ################################################################################################################################

    def test_not_found_is_404(self, zato_server:'anydict') -> 'None':
        _reset_server_expectations()

        status, text = self._invoke_channel(zato_server, 'missing')

        assert status == 404
        assert 'NOT_FOUND' in text

# ################################################################################################################################

    def test_permission_denied_is_403(self, zato_server:'anydict') -> 'None':
        _reset_server_expectations()

        status, text = self._invoke_channel(zato_server, 'forbidden')

        assert status == 403
        assert 'PERMISSION_DENIED' in text

# ################################################################################################################################

    def test_invalid_argument_is_400(self, zato_server:'anydict') -> 'None':
        _reset_server_expectations()

        # The channel replies with a generic body for bad requests, so only the status is asserted
        status, _ = self._invoke_channel(zato_server, 'invalid')

        assert status == 400

# ################################################################################################################################

    def test_unavailable_is_503(self, zato_server:'anydict') -> 'None':
        _reset_server_expectations()

        status, text = self._invoke_channel(zato_server, 'overloaded')

        assert status == 503
        assert 'UNAVAILABLE' in text

# ################################################################################################################################
# ################################################################################################################################
