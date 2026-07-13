# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time
from base64 import b64decode, b64encode

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.soap.common import NS
from zato.common.util.xml_.core import qname
from certs import build_tls_material
from soap_outconn import create_soap_outconn, delete_soap_outconn, invoke_soap_outconn_from_ide, \
    wait_for_soap_invoker_service
from wss_definition import change_wss_password, create_wss_definition, delete_wss_definition

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

_Test_Name_Prefix = 'test.soap.end.to.end.' + CryptoManager.generate_hex_string(32) + '.'

# How long to keep retrying an invocation while a UI change propagates to the server
_Propagation_Timeout = 30

# How long to sleep between the attempts above
_Propagation_Poll_Interval = 1.0

# ################################################################################################################################
# ################################################################################################################################

def _invoke_with_retry(page:'Page', base_url:'str', outconn_name:'str', operation:'str', **kwargs:'any_') -> 'anydict':
    """ Invokes an outgoing connection through the pre-deployed service, driven from
    the IDE in the browser, retrying while the connection configured a moment ago
    in the browser propagates to the server.
    """

    deadline = time.monotonic() + _Propagation_Timeout
    last_error = None

    while time.monotonic() < deadline:
        try:
            out = invoke_soap_outconn_from_ide(page, base_url, outconn_name, operation, **kwargs)
        except Exception as invoke_error:
            last_error = invoke_error
            time.sleep(_Propagation_Poll_Interval)
        else:
            # The service reports errors as a reply field, e.g. while the connection
            # configured a moment ago is still propagating to the server. A fault is
            # retried too - the test endpoints reject stale credentials with one until
            # a password changed in the browser reaches the connection.
            if error := (out.get('error') or out.get('fault_code')):
                last_error = error
                time.sleep(_Propagation_Poll_Interval)
                continue

            return out

    raise Exception(f'Could not invoke `{outconn_name}` within {_Propagation_Timeout}s, last error: {last_error}')

# ################################################################################################################################
# ################################################################################################################################

class TestSOAPOutconnEndToEnd:
    """ End-to-end scenarios - every connection is configured through the browser
    and then exercised by a pre-deployed service against the live test SOAP server,
    with assertions on both what the server received and what the service got back.
    """

# ################################################################################################################################

    def test_body_credentials(
        self, logged_in_page:'Page', zato_dashboard:'anydict', soap_test_server:'any_') -> 'None':
        """ Credentials of the attached security definition travel inside the message body,
        in mapping order, ahead of the business fields.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        wait_for_soap_invoker_service(page, base_url)

        name = _Test_Name_Prefix + 'body-credentials'
        username = 'user.' + name
        password = 'password.' + CryptoManager.generate_hex_string(32)

        # The server-side endpoint requires these exact credentials in the body.
        path = '/end-to-end-body-credentials'
        soap_test_server.configure(path, expect_credentials={'username': username, 'password': password})

        # Create the security definition in the browser and give it a known password ..
        wss_id = create_wss_definition(page, base_url, name, username, 'username_token')
        change_wss_password(page, wss_id, password)

        # .. create the connection with the body-credential mappings ..
        outconn_id = create_soap_outconn(page, base_url, name, soap_test_server.address, {
            'url_path': path,
            'soap_version': '1.2',
            'security': f'WS-Security/{name}',
            'body_credentials': [
                {'name': 'username'},
                {'name': 'password'},
            ],
        })

        # .. invoke it from the IDE in the browser ..
        result = _invoke_with_retry(page, base_url, name, 'submitSingleMessage',
            namespace='urn:cdc:iisb:2014',
            fields={'facilityID': 'FAC-01', 'hl7Message': 'MSH|...'},
            response_fields=['status'],
        )

        # .. the endpoint accepted the credentials and answered ..
        assert result['fields']['status'] == 'ok', f'Expected an ok response, got: {result}'

        # .. and the credentials really arrived as the first body elements, in order.
        operation = soap_test_server.last_request['body'].submitSingleMessage
        assert list(operation._children) == ['username', 'password', 'facilityID', 'hl7Message']

        # Clean up.
        delete_soap_outconn(page, outconn_id)
        delete_wss_definition(page, wss_id)

# ################################################################################################################################

    def test_username_token(
        self, logged_in_page:'Page', zato_dashboard:'anydict', soap_test_server:'any_') -> 'None':
        """ The attached WS-Security definition produces a UsernameToken header
        the endpoint verifies.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        wait_for_soap_invoker_service(page, base_url)

        name = _Test_Name_Prefix + 'token'
        username = 'user.' + name
        password = 'password.' + CryptoManager.generate_hex_string(32)

        # The server-side endpoint enforces this exact UsernameToken.
        path = '/end-to-end-username-token'
        soap_test_server.configure(path, enforce_wss={
            'mode': 'username_token',
            'username': username,
            'password': password,
            'use_digest': False,
        })

        # Create the security definition in the browser and give it a known password ..
        wss_id = create_wss_definition(page, base_url, name, username, 'username_token')
        change_wss_password(page, wss_id, password)

        # .. create the connection with that definition attached ..
        outconn_id = create_soap_outconn(page, base_url, name, soap_test_server.address, {
            'url_path': path,
            'soap_version': '1.2',
            'security': f'WS-Security/{name}',
        })

        # .. and invoke it - the endpoint rejects the message unless the token checks out.
        result = _invoke_with_retry(page, base_url, name, 'submitSingleMessage',
            namespace='urn:cdc:iisb:2014',
            fields={'facilityID': 'FAC-01'},
            response_fields=['status'],
        )

        assert result['fields']['status'] == 'ok', f'Expected an ok response, got: {result}'

        # Clean up.
        delete_soap_outconn(page, outconn_id)
        delete_wss_definition(page, wss_id)

# ################################################################################################################################

    def test_signed_saml(
        self, logged_in_page:'Page', zato_dashboard:'anydict', soap_test_server:'any_') -> 'None':
        """ The attached SAML definition produces a signed assertion with an audience
        restriction the endpoint verifies against its trust anchors.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        wait_for_soap_invoker_service(page, base_url)

        # Real signing material - a CA-signed certificate and its key, kept in PEM files.
        material = build_tls_material('127.0.0.1')

        name = _Test_Name_Prefix + 'saml'
        issuer = 'urn:issuer:' + name
        audience = 'urn:audience:' + name

        # The server-side endpoint requires a signed assertion from this issuer,
        # chaining up to the test CA.
        path = '/end-to-end-saml'
        soap_test_server.configure(path, enforce_wss={
            'mode': 'saml',
            'issuer': issuer,
            'sign': True,
            'trust_anchors': material.ca_path,
        })

        # Create the SAML definition in the browser, signing on, with the paths to its material ..
        wss_id = create_wss_definition(page, base_url, name, 'user.' + name, 'saml', {
            'issuer': issuer,
            'subject': 'CN=Test Subject',
            'audience': audience,
            'sign': True,
            'signing_key': material.client_key_path,
            'signing_certificate_chain': material.client_certificate_path,
        })

        # .. create the connection with that definition attached ..
        outconn_id = create_soap_outconn(page, base_url, name, soap_test_server.address, {
            'url_path': path,
            'soap_version': '1.2',
            'security': f'WS-Security/{name}',
        })

        # .. and invoke it - the endpoint verifies the assertion's signature.
        result = _invoke_with_retry(page, base_url, name, 'DocumentQuery',
            namespace='urn:ihe:iti:xds-b:2007',
            fields={'patientID': 'PID-123'},
            response_fields=['status'],
        )

        assert result['fields']['status'] == 'ok', f'Expected an ok response, got: {result}'

        # The assertion carried the definition's audience restriction on the wire.
        audience_element = soap_test_server.last_request['envelope'].find(f'.//{qname(NS.SAML2, "Audience")}')

        assert audience_element is not None, 'Expected an Audience element in the assertion'
        assert audience_element.text == audience, f'Expected the audience, got: {audience_element.text}'

        # Clean up.
        delete_soap_outconn(page, outconn_id)
        delete_wss_definition(page, wss_id)

# ################################################################################################################################

    def test_x509_signed(
        self, logged_in_page:'Page', zato_dashboard:'anydict', soap_test_server:'any_') -> 'None':
        """ The attached X.509 definition signs outgoing messages and the endpoint
        pins the connection's certificate to verify them.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        wait_for_soap_invoker_service(page, base_url)

        # Real signing material - a CA-signed certificate and its key, kept in PEM files.
        material = build_tls_material('127.0.0.1')

        name = _Test_Name_Prefix + 'x509-signed'

        # The server-side endpoint requires a signature from exactly this certificate.
        path = '/end-to-end-x509-signed'
        soap_test_server.configure(path, enforce_wss={
            'mode': 'x509',
            'sign': True,
            'encrypt': False,
            'peer_certificate': material.client_certificate_path,
        })

        # Create the X.509 definition in the browser, signing on, with the paths to its material ..
        wss_id = create_wss_definition(page, base_url, name, 'user.' + name, 'x509', {
            'sign': True,
            'encrypt': False,
            'signing_key': material.client_key_path,
            'signing_certificate_chain': material.client_certificate_path,
        })

        # .. create the connection with that definition attached ..
        outconn_id = create_soap_outconn(page, base_url, name, soap_test_server.address, {
            'url_path': path,
            'soap_version': '1.2',
            'security': f'WS-Security/{name}',
        })

        # .. and invoke it - the endpoint rejects the message unless the signature checks out.
        result = _invoke_with_retry(page, base_url, name, 'submitSingleMessage',
            namespace='urn:cdc:iisb:2014',
            fields={'facilityID': 'FAC-01'},
            response_fields=['status'],
        )

        assert result['fields']['status'] == 'ok', f'Expected an ok response, got: {result}'

        # Clean up.
        delete_soap_outconn(page, outconn_id)
        delete_wss_definition(page, wss_id)

# ################################################################################################################################

    def test_x509_encrypted(
        self, logged_in_page:'Page', zato_dashboard:'anydict', soap_test_server:'any_') -> 'None':
        """ The attached X.509 definition encrypts the body to the endpoint's certificate -
        no plaintext leaves the connection and the endpoint decrypts with its own key.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        wait_for_soap_invoker_service(page, base_url)

        # Real encryption material - the endpoint's own key pair, kept in PEM files.
        material = build_tls_material('127.0.0.1')

        name = _Test_Name_Prefix + 'x509-encrypted'

        # The server-side endpoint requires an encrypted body it decrypts with its own key.
        path = '/end-to-end-x509-encrypted'
        soap_test_server.configure(path, enforce_wss={
            'mode': 'x509',
            'sign': False,
            'encrypt': True,
            'decryption_key': material.server_key_path,
        })

        # Create the X.509 definition in the browser, encryption on, with the path to the endpoint's certificate ..
        wss_id = create_wss_definition(page, base_url, name, 'user.' + name, 'x509', {
            'sign': False,
            'encrypt': True,
            'peer_certificate': material.server_certificate_path,
        })

        # .. create the connection with that definition attached ..
        outconn_id = create_soap_outconn(page, base_url, name, soap_test_server.address, {
            'url_path': path,
            'soap_version': '1.2',
            'security': f'WS-Security/{name}',
        })

        # .. and invoke it with a field value unique to this test.
        facility_id = 'FAC-' + CryptoManager.generate_hex_string()

        result = _invoke_with_retry(page, base_url, name, 'submitSingleMessage',
            namespace='urn:cdc:iisb:2014',
            fields={'facilityID': facility_id},
            response_fields=['status'],
        )

        # The endpoint decrypted the body and answered ..
        assert result['fields']['status'] == 'ok', f'Expected an ok response, got: {result}'

        # .. and the wire carried no plaintext.
        raw_body = soap_test_server.last_request['raw_body']
        assert facility_id.encode() not in raw_body, 'The plaintext leaked to the wire'

        # Clean up.
        delete_soap_outconn(page, outconn_id)
        delete_wss_definition(page, wss_id)

# ################################################################################################################################

    def test_x509_signed_and_encrypted(
        self, logged_in_page:'Page', zato_dashboard:'anydict', soap_test_server:'any_') -> 'None':
        """ The attached X.509 definition both signs and encrypts - the endpoint decrypts
        with its own key and validates the signer through its trust anchors.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        wait_for_soap_invoker_service(page, base_url)

        # Real crypto material - the connection's own key pair and the endpoint's,
        # both chaining up to the same test CA, all kept in PEM files.
        material = build_tls_material('127.0.0.1')

        name = _Test_Name_Prefix + 'x509-full'

        # The server-side endpoint decrypts with its own key and trusts any signer under the CA.
        path = '/end-to-end-x509-full'
        soap_test_server.configure(path, enforce_wss={
            'mode': 'x509',
            'sign': True,
            'encrypt': True,
            'decryption_key': material.server_key_path,
            'trust_anchors': material.ca_path,
        })

        # Create the X.509 definition in the browser, signing and encryption on, with the paths to all its material ..
        wss_id = create_wss_definition(page, base_url, name, 'user.' + name, 'x509', {
            'sign': True,
            'encrypt': True,
            'signing_key': material.client_key_path,
            'signing_certificate_chain': material.client_certificate_path,
            'peer_certificate': material.server_certificate_path,
        })

        # .. create the connection with that definition attached ..
        outconn_id = create_soap_outconn(page, base_url, name, soap_test_server.address, {
            'url_path': path,
            'soap_version': '1.2',
            'security': f'WS-Security/{name}',
        })

        # .. and invoke it with a field value unique to this test.
        facility_id = 'FAC-' + CryptoManager.generate_hex_string()

        result = _invoke_with_retry(page, base_url, name, 'submitSingleMessage',
            namespace='urn:cdc:iisb:2014',
            fields={'facilityID': facility_id},
            response_fields=['status'],
        )

        # The endpoint decrypted the body and verified the signature ..
        assert result['fields']['status'] == 'ok', f'Expected an ok response, got: {result}'

        # .. and the wire carried no plaintext.
        raw_body = soap_test_server.last_request['raw_body']
        assert facility_id.encode() not in raw_body, 'The plaintext leaked to the wire'

        # Clean up.
        delete_soap_outconn(page, outconn_id)
        delete_wss_definition(page, wss_id)

# ################################################################################################################################

    def test_mutual_tls(
        self, logged_in_page:'Page', zato_dashboard:'anydict', soap_test_server_mtls:'any_') -> 'None':
        """ The client certificate paths configured in the browser let the connection
        reach an endpoint that requires client certificates.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        wait_for_soap_invoker_service(page, base_url)

        material = soap_test_server_mtls.tls_material

        name = _Test_Name_Prefix + 'mtls'
        path = '/end-to-end-mutual-tls'
        soap_test_server_mtls.configure(path)

        # The test CA is not in the system trust store, so validation is off -
        # the client certificate is still presented during the handshake.
        outconn_id = create_soap_outconn(page, base_url, name, soap_test_server_mtls.address, {
            'url_path': path,
            'soap_version': '1.2',
            'validate_tls': 'False',
            'tls_client_cert': material.client_certificate_path,
            'tls_client_key': material.client_key_path,
        })

        result = _invoke_with_retry(page, base_url, name, 'submitSingleMessage',
            namespace='urn:cdc:iisb:2014',
            fields={'facilityID': 'FAC-01'},
            response_fields=['status'],
        )

        assert result['fields']['status'] == 'ok', f'Expected an ok response, got: {result}'

        # Clean up.
        delete_soap_outconn(page, outconn_id)

# ################################################################################################################################

    def test_mtom_with_ws_addressing(
        self, logged_in_page:'Page', zato_dashboard:'anydict', soap_test_server:'any_') -> 'None':
        """ Bytes travel as MTOM parts, WS-Addressing headers ride along, and the
        response's attachment and addressing come back to the service.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        wait_for_soap_invoker_service(page, base_url)

        name = _Test_Name_Prefix + 'mtom-wsa'
        document_bytes = ('BINARY-DOCUMENT-' + CryptoManager.generate_hex_string()).encode()
        response_bytes = ('RETRIEVED-BYTES-' + CryptoManager.generate_hex_string()).encode()

        path = '/end-to-end-mtom-addressing'
        soap_test_server.configure(path, respond_attachment=response_bytes)

        outconn_id = create_soap_outconn(page, base_url, name, soap_test_server.address, {
            'url_path': path,
            'soap_version': '1.2',
            'soap_action': 'urn:ihe:iti:2007:ProvideAndRegisterDocumentSet-b',
            'use_ws_addressing': True,
            'use_mtom': True,
        })

        result = _invoke_with_retry(page, base_url, name, 'ProvideAndRegisterDocumentSet',
            namespace='urn:ihe:iti:xds-b:2007',
            bytes_fields={'Document': b64encode(document_bytes).decode()},
            response_fields=['status'],
        )

        assert result['fields']['status'] == 'ok', f'Expected an ok response, got: {result}'

        # The request went out as an MTOM package the server resolved back into the bytes ..
        request = soap_test_server.last_request
        assert request['body'].ProvideAndRegisterDocumentSet.Document == document_bytes

        # .. with the WS-Addressing headers in place ..
        request_addressing = request['addressing']
        assert request_addressing.action == 'urn:ihe:iti:2007:ProvideAndRegisterDocumentSet-b'
        assert request_addressing.message_id, 'The request should carry a MessageID'

        # .. the reply relates back to the request's MessageID ..
        assert result['addressing']['relates_to'] == request_addressing.message_id

        # .. and the response attachment landed back in the service.
        assert len(result['attachments']) == 1
        assert b64decode(result['attachments'][0]['data']) == response_bytes

        # Clean up.
        delete_soap_outconn(page, outconn_id)

# ################################################################################################################################
# ################################################################################################################################
