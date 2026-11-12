# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# OAuth bearer tokens - a token obtained from the token endpoint of the security definition on the first call,
# taken from the cache on the following ones and obtained anew once the definition changes.

# stdlib
from json import dumps, loads
from urllib.parse import parse_qsl

# pytest
import pytest

# Zato
from zato.common.api import DATA_FORMAT, SEC_DEF_TYPE
from zato.common.exception import BackendInvocationError

# Test support
from endpoint import EndpointResponse
from support import Client_ID, Client_Secret, new_connection, Test_CID, Token_Path_Suffix

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from endpoint import TestEndpoint
    from support import ServerStub
    from zato.server.connection.http_soap.outgoing import HTTPSOAPWrapper

# ################################################################################################################################
# ################################################################################################################################

# The name of the definition the connections use
_sec_def_name = 'test.bearer.oauth'

# The tokens the token endpoint issues
_first_token  = 'oauth.token.first.3b9e7d1a5c2f4e8b'
_second_token = 'oauth.token.second.9d6a1c7e3f5b2d8a'

# ################################################################################################################################
# ################################################################################################################################

def _token_response(token:'str') -> 'EndpointResponse':
    """ Returns what the token endpoint answers a successful token request with.
    """
    body = {
        'access_token': token,
        'token_type': 'Bearer',
        'expires_in': 3600,
    }

    out = EndpointResponse(body=dumps(body), headers=[('Content-Type', 'application/json')])
    return out

# ################################################################################################################################

def _new_oauth_connection(
    endpoint:'TestEndpoint',
    server:'ServerStub',
    path:'str',
    *,
    scopes:'str'='',
    data_format:'str'=DATA_FORMAT.JSON,
    ) -> 'HTTPSOAPWrapper':
    """ Registers the OAuth definition with its token endpoint under the test's path and returns a connection that uses it.
    """
    token_path = path + Token_Path_Suffix
    endpoint.set_responses(token_path, [_token_response(_first_token), _token_response(_second_token)])

    auth_server_url = endpoint.http_base + token_path
    server.add_oauth(_sec_def_name, auth_server_url, scopes=scopes, data_format=data_format)

    out = new_connection(server, endpoint.http_base, path, sec_type=SEC_DEF_TYPE.OAUTH, security_name=_sec_def_name)
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_token_obtained_once_and_cached(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ The first call obtains a token from the token endpoint and the following ones use the same token without asking for it again.
    """
    connection = _new_oauth_connection(endpoint, server, path)

    _ = connection.get(Test_CID)
    _ = connection.post(Test_CID, 'Test request body')
    _ = connection.get(Test_CID)

    token_requests = endpoint.get_requests(path + Token_Path_Suffix)
    assert len(token_requests) == 1

    requests = endpoint.get_requests(path)
    assert len(requests) == 3

    for item in requests:
        assert item.get_header_list('Authorization') == [f'Bearer {_first_token}']

# ################################################################################################################################

def test_token_request_json(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A definition with the JSON data format sends its client credentials as a JSON document.
    """
    connection = _new_oauth_connection(endpoint, server, path, data_format=DATA_FORMAT.JSON)

    _ = connection.get(Test_CID)

    token_request = endpoint.get_request(path + Token_Path_Suffix)

    assert token_request.method == 'POST'
    assert token_request.get_header('Content-Type') == 'application/json'
    assert loads(token_request.body) == {
        'client_id': Client_ID,
        'client_secret': Client_Secret,
        'grant_type': 'client_credentials',
    }

# ################################################################################################################################

def test_token_request_form_data(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A definition with the form data format sends its client credentials as a form.
    """
    connection = _new_oauth_connection(endpoint, server, path, data_format=DATA_FORMAT.FORM_DATA)

    _ = connection.get(Test_CID)

    token_request = endpoint.get_request(path + Token_Path_Suffix)
    form = dict(parse_qsl(token_request.body.decode('utf8')))

    assert token_request.get_header('Content-Type') == 'application/x-www-form-urlencoded'
    assert form == {
        'client_id': Client_ID,
        'client_secret': Client_Secret,
        'grant_type': 'client_credentials',
    }

# ################################################################################################################################

def test_scopes_from_definition(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ The scopes of the definition, given one per line, are sent in one line separated with spaces.
    """
    connection = _new_oauth_connection(endpoint, server, path, scopes='orders.read\n  orders.write  \n\ncustomers.read')

    _ = connection.get(Test_CID)

    token_request = endpoint.get_request(path + Token_Path_Suffix)
    assert loads(token_request.body)['scope'] == 'orders.read orders.write customers.read'

# ################################################################################################################################

def test_scopes_from_call(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ Scopes given in the call win over the scopes of the definition, and a token is cached per set of scopes.
    """
    connection = _new_oauth_connection(endpoint, server, path, scopes='orders.read')

    _ = connection.get(Test_CID)
    _ = connection.get(Test_CID, auth_scopes='customers.read')

    first, second = endpoint.get_requests(path + Token_Path_Suffix)

    assert loads(first.body)['scope'] == 'orders.read'
    assert loads(second.body)['scope'] == 'customers.read'

    first_call, second_call = endpoint.get_requests(path)

    assert first_call.get_header('Authorization') == f'Bearer {_first_token}'
    assert second_call.get_header('Authorization') == f'Bearer {_second_token}'

# ################################################################################################################################

def test_definition_named_on_call(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A definition named in the call is used instead of the definition of the connection.
    """
    connection = _new_oauth_connection(endpoint, server, path)

    other_name = 'test.bearer.oauth.other'
    other_token_path = path + '/other' + Token_Path_Suffix
    endpoint.set_response(other_token_path, _token_response('oauth.token.other.5c2f4e8b3b9e7d1a'))

    other_auth_server_url = endpoint.http_base + other_token_path
    server.add_oauth(other_name, other_auth_server_url)

    _ = connection.get(Test_CID, sec_def_name=other_name)

    assert endpoint.get_requests(path + Token_Path_Suffix) == []
    assert len(endpoint.get_requests(other_token_path)) == 1

    request = endpoint.get_request(path)
    assert request.get_header('Authorization') == 'Bearer oauth.token.other.5c2f4e8b3b9e7d1a'

# ################################################################################################################################

def test_definition_edit_invalidates_tokens(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A token obtained before the definition was edited is not used after the edit, and a new one is obtained instead.
    """
    connection = _new_oauth_connection(endpoint, server, path)

    _ = connection.get(Test_CID)
    _ = connection.get(Test_CID)

    server.edit_bearer_token(_sec_def_name, [connection], password='New.Test.Client.Secret.2026')

    _ = connection.get(Test_CID)

    token_requests = endpoint.get_requests(path + Token_Path_Suffix)
    assert len(token_requests) == 2

    second_token_request = token_requests[1]
    assert loads(second_token_request.body)['client_secret'] == 'New.Test.Client.Secret.2026'

    first, second, third = endpoint.get_requests(path)

    assert first.get_header('Authorization') == f'Bearer {_first_token}'
    assert second.get_header('Authorization') == f'Bearer {_first_token}'
    assert third.get_header('Authorization') == f'Bearer {_second_token}'

# ################################################################################################################################

def test_token_endpoint_error(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A token endpoint that answers with an error raises BackendInvocationError with its status and body,
    and the resource is not invoked.
    """
    connection = _new_oauth_connection(endpoint, server, path)

    token_path = path + Token_Path_Suffix
    error_body = '{"error": "invalid_client"}'
    endpoint.set_response(token_path, EndpointResponse(401, error_body))

    with pytest.raises(BackendInvocationError) as info:
        _ = connection.get(Test_CID)

    auth_server_url = endpoint.http_base + token_path
    assert info.value.msg == f'Bearer token for `{_sec_def_name}` could not be obtained from {auth_server_url} -> 401 -> {error_body}'

    assert endpoint.get_requests(path) == []

# ################################################################################################################################
# ################################################################################################################################
