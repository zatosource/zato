# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# API keys - a header named after the username of the security definition, with its password as the value.

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

# The key the definitions hold
_api_key = 'api.key.7d3f1b9e5c2a4d8f'

# ################################################################################################################################
# ################################################################################################################################

def test_header_named_after_username(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ The header is named after the username of the definition and its value is the password, on every request.
    """
    connection = new_connection(
        server,
        endpoint.http_base,
        path,
        sec_type=SEC_DEF_TYPE.APIKEY,
        username='X-API-Key',
        password=_api_key,
    )

    _ = connection.get(Test_CID)
    _ = connection.post(Test_CID, 'Test request body')

    requests = endpoint.get_requests(path)
    assert len(requests) == 2

    for item in requests:
        assert item.get_header_list('X-API-Key') == [_api_key]
        assert item.get_header('Authorization') is None

# ################################################################################################################################

def test_original_username_wins(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ The username of the definition as it was originally given names the header when the definition has one.
    """
    connection = new_connection(
        server,
        endpoint.http_base,
        path,
        sec_type=SEC_DEF_TYPE.APIKEY,
        username='HTTP_X_API_KEY',
        orig_username='X-Partner-Key',
        password=_api_key,
    )

    _ = connection.get(Test_CID)

    request = endpoint.get_request(path)

    assert request.get_header('X-Partner-Key') == _api_key
    assert request.get_header('HTTP_X_API_KEY') is None

# ################################################################################################################################

def test_key_change(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A key changed through a configuration update is the one the next call is made with.
    """
    connection = new_connection(
        server,
        endpoint.http_base,
        path,
        sec_type=SEC_DEF_TYPE.APIKEY,
        username='X-API-Key',
        password=_api_key,
    )

    _ = connection.get(Test_CID)

    new_key = 'api.key.new.2b8e4f1a6c3d9e7b'
    connection.config['password'] = new_key
    connection.set_auth()

    _ = connection.get(Test_CID)

    first, second = endpoint.get_requests(path)

    assert first.get_header('X-API-Key') == _api_key
    assert second.get_header('X-API-Key') == new_key

# ################################################################################################################################
# ################################################################################################################################
