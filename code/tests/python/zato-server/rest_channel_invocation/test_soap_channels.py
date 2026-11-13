# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# SOAP 1.1 and 1.2 channels - envelopes, responses and faults.

# stdlib
from http.client import INTERNAL_SERVER_ERROR, OK

# Zato
from channel_definitions import Paths
from channel_suite import find_text, parse_soap, SOAP_11_Envelope, SOAP_11_Headers, SOAP_11_Namespace, SOAP_12_Envelope, \
    SOAP_12_Headers, SOAP_12_Namespace

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from channel_client import ChannelClient, HTTPResponse
    from zato.common.typing_ import any_, strdict

# ################################################################################################################################
# ################################################################################################################################

_soap_11_content_type = 'text/xml; charset=utf-8'
_soap_12_content_type = 'application/soap+xml; charset=utf-8'

_xml_declaration = b"<?xml version='1.0' encoding='UTF-8'?>\n"

# ################################################################################################################################
# ################################################################################################################################

def _post(client:'ChannelClient', path:'str', headers:'strdict', body:'str | bytes') -> 'HTTPResponse':
    if isinstance(body, str):
        body = body.encode('utf-8')

    out = client.request('POST', path, headers=headers, body=body)
    return out

# ################################################################################################################################

def _assert_envelope(response:'HTTPResponse', status:'int', content_type:'str', namespace:'str') -> 'any_':
    """ Asserts the status, the content type and the namespace of a SOAP response and returns its root element.
    """
    assert response.status == status, response.body
    assert response.headers['content-type'] == content_type
    assert response.body.startswith(_xml_declaration)

    out = parse_soap(response.body)
    assert out.tag == '{' + namespace + '}Envelope'

    return out

# ################################################################################################################################
# ################################################################################################################################

def test_soap_11(client:'ChannelClient') -> 'None':
    response = _post(client, Paths.SOAP_Echo, SOAP_11_Headers, SOAP_11_Envelope)
    root = _assert_envelope(response, OK, _soap_11_content_type, SOAP_11_Namespace)

    assert find_text(root, 'Body/GetCustomerResponse/operation') == 'GetCustomer'
    assert find_text(root, 'Body/GetCustomerResponse/soap_version') == '1.1'
    assert find_text(root, 'Body/GetCustomerResponse/customer_id') == '123'
    assert find_text(root, 'Body/GetCustomerResponse/name') == 'John Smith'

# ################################################################################################################################

def test_soap_12(client:'ChannelClient') -> 'None':
    response = _post(client, Paths.SOAP_Echo, SOAP_12_Headers, SOAP_12_Envelope)
    root = _assert_envelope(response, OK, _soap_12_content_type, SOAP_12_Namespace)

    assert find_text(root, 'Body/GetCustomerResponse/operation') == 'GetCustomer'
    assert find_text(root, 'Body/GetCustomerResponse/soap_version') == '1.2'
    assert find_text(root, 'Body/GetCustomerResponse/customer_id') == '123'

# ################################################################################################################################

def test_soap_action_not_required(client:'ChannelClient') -> 'None':

    # The operation is taken from the body, so neither the action nor the content type is needed
    for headers in ({'Content-Type': _soap_11_content_type}, {'Content-Type': 'application/json'}, {}):
        response = _post(client, Paths.SOAP_Echo, headers, SOAP_11_Envelope)
        root = _assert_envelope(response, OK, _soap_11_content_type, SOAP_11_Namespace)

        assert find_text(root, 'Body/GetCustomerResponse/operation') == 'GetCustomer'

# ################################################################################################################################

def test_invalid_request(client:'ChannelClient') -> 'None':

    bodies = (
        f'<soap:Envelope xmlns:soap="{SOAP_11_Namespace}"><soap:Body>',
        '<customer><customer_id>123</customer_id></customer>',
        '',
    )

    for body in bodies:
        response = _post(client, Paths.SOAP_Echo, SOAP_11_Headers, body)
        root = _assert_envelope(response, INTERNAL_SERVER_ERROR, _soap_11_content_type, SOAP_11_Namespace)

        assert find_text(root, 'Body/Fault/faultcode') == 'soap:Client'
        assert find_text(root, 'Body/Fault/faultstring') == 'Invalid SOAP request'

    response = client.get(Paths.SOAP_Echo)
    root = _assert_envelope(response, INTERNAL_SERVER_ERROR, _soap_11_content_type, SOAP_11_Namespace)
    assert find_text(root, 'Body/Fault/faultstring') == 'Invalid SOAP request'

# ################################################################################################################################

def test_fault_for_exception_soap_11(client:'ChannelClient') -> 'None':
    response = _post(client, Paths.SOAP_Error, SOAP_11_Headers, SOAP_11_Envelope)
    root = _assert_envelope(response, INTERNAL_SERVER_ERROR, _soap_11_content_type, SOAP_11_Namespace)

    assert find_text(root, 'Body/Fault/faultcode') == 'soap:Server'
    assert find_text(root, 'Body/Fault/faultstring') == 'An error has occurred'
    assert b'Customer database is unavailable' not in response.body

# ################################################################################################################################

def test_fault_for_exception_soap_12(client:'ChannelClient') -> 'None':
    response = _post(client, Paths.SOAP_Error, SOAP_12_Headers, SOAP_12_Envelope)
    root = _assert_envelope(response, INTERNAL_SERVER_ERROR, _soap_12_content_type, SOAP_12_Namespace)

    assert find_text(root, 'Body/Fault/Code/Value') == 'soap:Receiver'
    assert find_text(root, 'Body/Fault/Reason/Text') == 'An error has occurred'

# ################################################################################################################################

def test_fault_for_bad_request(client:'ChannelClient') -> 'None':
    response = _post(client, Paths.SOAP_Bad_Request, SOAP_11_Headers, SOAP_11_Envelope)
    root = _assert_envelope(response, INTERNAL_SERVER_ERROR, _soap_11_content_type, SOAP_11_Namespace)

    assert find_text(root, 'Body/Fault/faultcode') == 'soap:Client'
    assert find_text(root, 'Body/Fault/faultstring') == 'Customer ID is missing'

# ################################################################################################################################
# ################################################################################################################################
