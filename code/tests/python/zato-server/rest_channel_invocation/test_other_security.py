# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Client certificates presented through a front proxy, services that handle rejected requests themselves
# and WS-Security on a SOAP channel.

# stdlib
from http.client import OK, UNAUTHORIZED

# lxml
import lxml.etree as etree

# Zato
from channel_client import basic_auth_header
from channel_definitions import Credentials, Paths, Security
from channel_suite import assert_unauthorized, find_text, parse_soap, SOAP_11_Envelope, SOAP_11_Headers
from zato.common.soap.security.usernametoken import add_username_token

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from channel_client import ChannelClient
    from zato.common.typing_ import strdict

# ################################################################################################################################
# ################################################################################################################################

_verify_header = 'X-Zato-SSL-Client-Verify'
_fingerprint_header = 'X-Zato-SSL-Client-SHA256'
_subject_header = 'X-Zato-SSL-Client-Subject-DN'

_verified = 'SUCCESS'

_empty_security = {'id': None, 'name': None, 'type': None, 'username': None}

# ################################################################################################################################
# ################################################################################################################################

def _certificate_headers(**headers:'str') -> 'strdict':
    out = {_verify_header: _verified}
    out.update(headers)
    return out

# ################################################################################################################################

def _wss_envelope(username:'str', password:'str', use_digest:'bool' = False) -> 'bytes':
    envelope = etree.fromstring(SOAP_11_Envelope.encode('utf-8'))
    _ = add_username_token(envelope, username, password, use_digest)

    out = etree.tostring(envelope)
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_client_certificate_fingerprint(client:'ChannelClient') -> 'None':
    fingerprint = Credentials.MTLS_Fingerprint

    for value in (fingerprint, fingerprint.lower(), fingerprint.replace(':', '')):
        response = client.get(Paths.MTLS_Fingerprint, _certificate_headers(**{_fingerprint_header: value}))
        assert response.status == OK, value

        security = response.json()['channel']['security']
        assert security['name'] == Security.MTLS_Fingerprint
        assert security['type'] == 'mtls'

# ################################################################################################################################

def test_client_certificate_fingerprint_rejected(client:'ChannelClient') -> 'None':
    fingerprint = Credentials.MTLS_Fingerprint
    other_fingerprint = '00' + fingerprint[2:]

    # A certificate the proxy did not verify ..
    headers = {_verify_header: 'FAILED', _fingerprint_header: fingerprint}
    assert_unauthorized(client.get(Paths.MTLS_Fingerprint, headers))

    # .. a verified certificate of another client ..
    assert_unauthorized(client.get(Paths.MTLS_Fingerprint, _certificate_headers(**{_fingerprint_header: other_fingerprint})))

    # .. a fingerprint without the verification header ..
    assert_unauthorized(client.get(Paths.MTLS_Fingerprint, {_fingerprint_header: fingerprint}))

    # .. and no certificate at all.
    assert_unauthorized(client.get(Paths.MTLS_Fingerprint))

# ################################################################################################################################

def test_client_certificate_subject(client:'ChannelClient') -> 'None':
    response = client.get(Paths.MTLS_Subject, _certificate_headers(**{_subject_header: Credentials.MTLS_Subject_DN}))

    assert response.status == OK
    assert response.json()['channel']['security']['name'] == Security.MTLS_Subject

# ################################################################################################################################

def test_client_certificate_subject_rejected(client:'ChannelClient') -> 'None':

    other_subject = 'CN=orders.example.com,O=Example Corporation,C=US'
    reordered_subject = 'C=US,O=Example Corporation,CN=customers.example.com'

    for subject in (other_subject, reordered_subject):
        assert_unauthorized(client.get(Paths.MTLS_Subject, _certificate_headers(**{_subject_header: subject})))

    assert_unauthorized(client.get(Paths.MTLS_Subject))

# ################################################################################################################################

def test_service_handles_rejection(client:'ChannelClient') -> 'None':

    # Valid credentials reach the service with the security definition ..
    authorization = basic_auth_header(Credentials.Rejection_Username, Credentials.Rejection_Password)
    response = client.get(Paths.Rejection, {'Authorization': authorization})

    assert response.status == OK
    data = response.json()

    assert data['security']['name'] == Security.Rejection
    assert data['security']['username'] == Credentials.Rejection_Username

    # .. and rejected credentials reach it too, without a security definition.
    for headers in ({'Authorization': basic_auth_header(Credentials.Rejection_Username, 'Wrong.Password.1')}, {}):
        response = client.get(Paths.Rejection, headers)

        assert response.status == OK
        data = response.json()

        assert data['security'] == _empty_security
        assert data['echo']['service_name'] == 'test.channel.auth-rejection'
        assert 'zato.sec_def' not in data['echo']['context_keys']

# ################################################################################################################################

def test_wss_username_token(client:'ChannelClient') -> 'None':
    body = _wss_envelope(Credentials.WSS_Username, Credentials.WSS_Password)
    response = client.request('POST', Paths.SOAP_WSS, headers=SOAP_11_Headers, body=body)

    assert response.status == OK
    root = parse_soap(response.body)

    assert find_text(root, 'Body/GetCustomerResponse/customer_id') == '123'

# ################################################################################################################################

def test_wss_rejected(client:'ChannelClient') -> 'None':

    bodies = (
        _wss_envelope(Credentials.WSS_Username, 'Wrong.Password.1'),
        _wss_envelope('mary.johnson', Credentials.WSS_Password),
        _wss_envelope(Credentials.WSS_Username, Credentials.WSS_Password, use_digest=True),
        SOAP_11_Envelope.encode('utf-8'),
    )

    for body in bodies:
        response = client.request('POST', Paths.SOAP_WSS, headers=SOAP_11_Headers, body=body)

        assert response.status == UNAUTHORIZED
        assert response.headers['content-type'] == 'text/xml; charset=utf-8'

        root = parse_soap(response.body)
        assert find_text(root, 'Body/Fault/faultcode') == 'soap:Client'
        assert find_text(root, 'Body/Fault/faultstring') == '401 Unauthorized'

# ################################################################################################################################
# ################################################################################################################################
