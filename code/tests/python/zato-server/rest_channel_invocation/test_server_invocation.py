# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Channels imported through enmasse into the running server on their own and invoked over HTTP.

# stdlib
from http.client import NOT_FOUND, OK, UNAUTHORIZED

# pytest
import pytest

# Zato
from channel_client import basic_auth_header
from channel_definitions import build_server_yaml, Server, Services
from channel_suite import assert_unauthorized, find_text, parse_soap, SOAP_11_Envelope, SOAP_11_Headers, SOAP_12_Envelope, \
    SOAP_12_Headers, wait_until

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from channel_suite import Suite
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

_subject = 'patricia.martin'
_basic_path = '/test/channel/server/basic/123?segment=retail'

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='module')
def server_suite(suite:'Suite') -> 'any_':
    """ Imports the channels of the group and waits until the server serves them.
    """
    suite.environment.import_yaml(build_server_yaml(suite.provider))

    def _is_served() -> 'bool':
        out = suite.client.get(_basic_path).status != NOT_FOUND
        return out

    _ = wait_until(_is_served)

    yield suite

# ################################################################################################################################
# ################################################################################################################################

def test_basic_auth_channel(server_suite:'Suite') -> 'None':
    client = server_suite.client

    authorization = basic_auth_header(Server.Basic_Username, Server.Basic_Password)
    response = client.request('POST', _basic_path, headers={'Authorization': authorization, 'Content-Type': 'application/json'},
        body=b'{"name": "Patricia Martin"}')

    # What the client received ..
    assert response.status == OK
    assert response.headers['content-type'] == 'application/json'

    # .. and what the service received.
    data = response.json()

    assert data['service_name'] == Services.Echo
    assert data['channel']['name'] == Server.Basic_Channel
    assert data['channel']['security']['name'] == Server.Basic_Security
    assert data['channel']['security']['username'] == Server.Basic_Username
    assert data['params'] == {'customer_id': '123', 'segment': 'retail'}
    assert data['payload'] == {'type': 'dict', 'value': {'name': {'type': 'str', 'value': 'Patricia Martin'}}}

    wrong = basic_auth_header(Server.Basic_Username, 'Wrong.Password.1')
    assert client.get(_basic_path, {'Authorization': wrong}).status == UNAUTHORIZED

# ################################################################################################################################

def test_jwt_channel(server_suite:'Suite') -> 'None':
    client = server_suite.client
    token = server_suite.provider.new_token(_subject)

    response = client.get(Server.JWT_Path, {'Authorization': f'Bearer {token}'})

    assert response.status == OK
    data = response.json()

    assert data['channel']['name'] == Server.JWT_Channel
    assert data['channel']['security']['name'] == Server.JWT_Security
    assert data['headers']['authorization'] == f'Bearer {token}'

    assert_unauthorized(client.get(Server.JWT_Path), 'Bearer')

# ################################################################################################################################

def test_soap_channel(server_suite:'Suite') -> 'None':
    client = server_suite.client

    for headers, envelope, version in ((SOAP_11_Headers, SOAP_11_Envelope, '1.1'), (SOAP_12_Headers, SOAP_12_Envelope, '1.2')):
        response = client.request('POST', Server.SOAP_Path, headers=headers, body=envelope.encode('utf-8'))

        assert response.status == OK
        root = parse_soap(response.body)

        assert find_text(root, 'Body/GetCustomerResponse/operation') == 'GetCustomer'
        assert find_text(root, 'Body/GetCustomerResponse/soap_version') == version
        assert find_text(root, 'Body/GetCustomerResponse/customer_id') == '123'
        assert find_text(root, 'Body/GetCustomerResponse/name') == 'John Smith'

# ################################################################################################################################
# ################################################################################################################################
