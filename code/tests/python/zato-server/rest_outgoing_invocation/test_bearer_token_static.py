# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Static bearer tokens - a token stored in the security definition itself, sent in the header and with the prefix
# the definition names.

# Zato
from zato.common.api import SEC_DEF_TYPE

# Test support
from support import new_connection, Test_CID

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from endpoint import TestEndpoint
    from support import ServerStub

# ################################################################################################################################
# ################################################################################################################################

# The name of the definition and the token it holds
_sec_def_name = 'test.bearer.static'
_token = 'static.token.6f2a1c9e4b7d4a1f8c3e2b5d9a7f1c4e'

# ################################################################################################################################
# ################################################################################################################################

def test_header_and_prefix(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ The token is sent in the Authorization header with the Bearer prefix on every request.
    """
    server.add_static_token(_sec_def_name, _token)

    connection = new_connection(server, endpoint.http_base, path, sec_type=SEC_DEF_TYPE.OAUTH, security_name=_sec_def_name)

    _ = connection.get(Test_CID)
    _ = connection.post(Test_CID, 'Test request body')

    requests = endpoint.get_requests(path)
    assert len(requests) == 2

    for item in requests:
        assert item.get_header_list('Authorization') == [f'Bearer {_token}']

# ################################################################################################################################

def test_custom_header_without_prefix(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A definition with its own header name and without a prefix sends the token alone in that header.
    """
    server.add_static_token(_sec_def_name, _token, header='X-Auth-Token', prefix='')

    connection = new_connection(server, endpoint.http_base, path, sec_type=SEC_DEF_TYPE.OAUTH, security_name=_sec_def_name)

    _ = connection.get(Test_CID)

    request = endpoint.get_request(path)

    assert request.get_header('X-Auth-Token') == _token
    assert request.get_header('Authorization') is None

# ################################################################################################################################

def test_token_in_password_column(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A definition that keeps its token in the password column sends that token.
    """
    server.add_static_token(_sec_def_name, _token, in_password=True)

    connection = new_connection(server, endpoint.http_base, path, sec_type=SEC_DEF_TYPE.OAUTH, security_name=_sec_def_name)

    _ = connection.get(Test_CID)

    request = endpoint.get_request(path)
    assert request.get_header('Authorization') == f'Bearer {_token}'

# ################################################################################################################################

def test_token_change(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A token changed in the definition is the one the next call is made with.
    """
    server.add_static_token(_sec_def_name, _token)

    connection = new_connection(server, endpoint.http_base, path, sec_type=SEC_DEF_TYPE.OAUTH, security_name=_sec_def_name)

    _ = connection.get(Test_CID)

    new_token = 'static.token.new.1a7c3e9b5d2f4a8c'
    server.edit_bearer_token(_sec_def_name, [connection], static_token=new_token)

    _ = connection.get(Test_CID)

    first, second = endpoint.get_requests(path)

    assert first.get_header('Authorization') == f'Bearer {_token}'
    assert second.get_header('Authorization') == f'Bearer {new_token}'

# ################################################################################################################################

def test_definition_named_on_call(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A static token definition named in the call is used by a connection that has no security definition of its own.
    """
    server.add_static_token(_sec_def_name, _token)

    connection = new_connection(server, endpoint.http_base, path)

    _ = connection.get(Test_CID)
    _ = connection.get(Test_CID, sec_def_name=_sec_def_name)

    first, second = endpoint.get_requests(path)

    assert first.get_header('Authorization') is None
    assert second.get_header('Authorization') == f'Bearer {_token}'

# ################################################################################################################################
# ################################################################################################################################
