# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import datetime
import os
import sys
from concurrent.futures import ThreadPoolExecutor

# gRPC
import grpc

sys.path.insert(0, os.path.dirname(__file__))

# Generated stubs
import billing_pb2
import billing_pb2_grpc

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

# Invoice IDs that make the server abort with a given status code -
# this is what the exception mapping tests are built around.
_error_triggers = {
    'missing':    (grpc.StatusCode.NOT_FOUND,          'No such invoice'),
    'forbidden':  (grpc.StatusCode.PERMISSION_DENIED,  'Access to this invoice is denied'),
    'invalid':    (grpc.StatusCode.INVALID_ARGUMENT,   'Invoice ID is not valid'),
    'overloaded': (grpc.StatusCode.UNAVAILABLE,        'The billing backend is not available'),
}

_test_customer = 'Test Customer Inc.'
_invoice_amount_cents = 12500

# ################################################################################################################################
# ################################################################################################################################

class TestServerConfig:
    """ What credentials, if any, the test server should expect - tests set these attributes
    and the servicer reads them on each call.
    """
    expected_authorization:'str | None' = None
    expected_apikey_header:'str | None' = None
    expected_apikey_value:'str | None' = None

    # The metadata the most recent call carried, for assertions
    received_metadata:'dict | None' = None

# ################################################################################################################################
# ################################################################################################################################

def _check_credentials(context:'any_') -> 'None':
    """ Verifies call metadata against what the tests expect, aborting with UNAUTHENTICATED on a mismatch.
    """
    metadata = dict(context.invocation_metadata())
    TestServerConfig.received_metadata = metadata

    if expected_authorization := TestServerConfig.expected_authorization:
        if metadata.get('authorization') != expected_authorization:
            context.abort(grpc.StatusCode.UNAUTHENTICATED, 'Invalid or missing authorization metadata')

    if expected_apikey_header := TestServerConfig.expected_apikey_header:
        header_name = expected_apikey_header.lower()
        if metadata.get(header_name) != TestServerConfig.expected_apikey_value:
            context.abort(grpc.StatusCode.UNAUTHENTICATED, 'Invalid or missing API key metadata')

# ################################################################################################################################
# ################################################################################################################################

class BillingServicer(billing_pb2_grpc.BillingServiceServicer):
    """ Implements all four RPC shapes for the tests to exercise.
    """

    def GetInvoice(self, request:'any_', context:'any_') -> 'any_':

        _check_credentials(context)

        # Some invoice IDs trigger errors on purpose
        if trigger := _error_triggers.get(request.invoice_id):
            code, details = trigger
            context.abort(code, details)

        out = billing_pb2.Invoice(
            invoice_id=request.invoice_id,
            customer=_test_customer,
            amount_cents=_invoice_amount_cents,
        )
        return out

# ################################################################################################################################

    def ListInvoices(self, request:'any_', context:'any_') -> 'any_':

        _check_credentials(context)

        for item_index in range(request.max_items):
            yield billing_pb2.Invoice(
                invoice_id=f'inv-{item_index}',
                customer=_test_customer,
                amount_cents=_invoice_amount_cents + item_index,
            )

# ################################################################################################################################

    def SubmitPayments(self, request_iterator:'any_', context:'any_') -> 'any_':

        _check_credentials(context)

        payment_count = 0
        total_cents = 0

        for payment in request_iterator:
            payment_count += 1
            total_cents += payment.amount_cents

        out = billing_pb2.PaymentSummary(payment_count=payment_count, total_cents=total_cents)
        return out

# ################################################################################################################################

    def ReconcilePayments(self, request_iterator:'any_', context:'any_') -> 'any_':

        _check_credentials(context)

        for payment in request_iterator:
            yield billing_pb2.PaymentReceipt(invoice_id=payment.invoice_id, is_settled=True)

# ################################################################################################################################
# ################################################################################################################################

def generate_tls_material() -> 'tuple':
    """ Generates a self-signed certificate for localhost along with its private key,
    both returned as PEM bytes - (certificate, private key).
    """

    # cryptography
    from cryptography import x509
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.x509.oid import NameOID

    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    subject = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, 'localhost')])
    now = datetime.datetime.now(datetime.timezone.utc)

    certificate = x509.CertificateBuilder() \
        .subject_name(subject) \
        .issuer_name(subject) \
        .public_key(private_key.public_key()) \
        .serial_number(x509.random_serial_number()) \
        .not_valid_before(now) \
        .not_valid_after(now + datetime.timedelta(days=1)) \
        .add_extension(x509.SubjectAlternativeName([x509.DNSName('localhost')]), critical=False) \
        .sign(private_key, hashes.SHA256())

    certificate_pem = certificate.public_bytes(serialization.Encoding.PEM)
    private_key_pem = private_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.TraditionalOpenSSL,
        serialization.NoEncryption(),
    )

    return certificate_pem, private_key_pem

# ################################################################################################################################
# ################################################################################################################################

def start_grpc_server(port:'int', certificate_pem:'bytes | None'=None, private_key_pem:'bytes | None'=None) -> 'any_':
    """ Starts the in-process gRPC test server, over TLS if certificate material is given.
    Returns the server object - stop it with server.stop(0).
    """
    server = grpc.server(ThreadPoolExecutor(max_workers=10))
    billing_pb2_grpc.add_BillingServiceServicer_to_server(BillingServicer(), server)

    if certificate_pem:
        credentials = grpc.ssl_server_credentials([(private_key_pem, certificate_pem)])
        _ = server.add_secure_port(f'localhost:{port}', credentials)
    else:
        _ = server.add_insecure_port(f'127.0.0.1:{port}')

    server.start()

    return server

# ################################################################################################################################
# ################################################################################################################################
