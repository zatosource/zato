# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Basic Auth - the Authorization header every request of a connection has, built from the credentials
# of its security definition as they stand at the time of the call.

# stdlib
from base64 import b64encode

# pytest
import pytest

# Zato
from zato.common.api import EnvVariable, SEC_DEF_TYPE
from zato.common.exception import BackendInvocationError

# Test support
from support import Basic_Password, Basic_Username, get_basic_authorization, new_basic_auth_connection, new_connection, \
    Test_CID

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from endpoint import TestEndpoint
    from support import ServerStub

# ################################################################################################################################
# ################################################################################################################################

def test_header_on_every_request(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ Each request has the same Authorization header, with a colon in the password kept as part of the password.
    """
    connection = new_basic_auth_connection(server, endpoint.http_base, path)

    _ = connection.get(Test_CID)
    _ = connection.post(Test_CID, 'Test request body')
    _ = connection.get(Test_CID)

    expected = get_basic_authorization(Basic_Username, Basic_Password)

    requests = endpoint.get_requests(path)
    assert len(requests) == 3

    for item in requests:
        assert item.get_header_list('Authorization') == [expected]

# ################################################################################################################################

def test_non_ascii_credentials(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ Non-ASCII characters of the credentials are sent as their ISO-8859-1 bytes.
    """
    username = 'jürgen.müller'
    password = 'Pässwörd:2026'

    connection = new_connection(
        server,
        endpoint.http_base,
        path,
        sec_type=SEC_DEF_TYPE.BASIC_AUTH,
        username=username,
        password=password,
    )

    _ = connection.get(Test_CID)

    credentials = username.encode('latin1') + b':' + password.encode('latin1')
    expected = 'Basic ' + b64encode(credentials).decode('ascii')

    request = endpoint.get_request(path)
    assert request.get_header('Authorization') == expected

# ################################################################################################################################

def test_password_change(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A password changed through a configuration update is the one the next call is made with.
    """
    connection = new_basic_auth_connection(server, endpoint.http_base, path)

    _ = connection.get(Test_CID)

    new_password = 'New.Test.Password.2026'
    connection.config['password'] = new_password
    connection.set_auth()

    _ = connection.get(Test_CID)

    first, second = endpoint.get_requests(path)

    assert first.get_header('Authorization') == get_basic_authorization(Basic_Username, Basic_Password)
    assert second.get_header('Authorization') == get_basic_authorization(Basic_Username, new_password)

# ################################################################################################################################

def test_missing_password(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A password that is the placeholder of an environment variable that was never set raises an error
    naming the connection, and nothing is sent.
    """
    placeholder = EnvVariable.Missing_Value_Prefix + 'Test_Basic_Auth_Password'

    connection = new_connection(
        server,
        endpoint.http_base,
        path,
        name='test.basic.auth.missing',
        sec_type=SEC_DEF_TYPE.BASIC_AUTH,
        username=Basic_Username,
        password=placeholder,
    )

    with pytest.raises(BackendInvocationError) as info:
        _ = connection.get(Test_CID)

    assert info.value.msg == f'Connection `test.basic.auth.missing` has no password -> `{placeholder}`'
    assert endpoint.get_requests(path) == []

# ################################################################################################################################

def test_no_security(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A connection without a security definition sends no Authorization header.
    """
    connection = new_connection(server, endpoint.http_base, path)

    _ = connection.get(Test_CID)

    request = endpoint.get_request(path)
    assert request.get_header('Authorization') is None

# ################################################################################################################################
# ################################################################################################################################
