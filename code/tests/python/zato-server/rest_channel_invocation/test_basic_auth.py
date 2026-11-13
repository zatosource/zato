# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Channels secured with Basic Auth definitions.

# stdlib
import base64
from http.client import OK, UNAUTHORIZED

# Zato
from channel_client import basic_auth_header
from channel_definitions import Credentials, Paths, Security
from channel_suite import assert_unauthorized, wait_until

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from channel_client import ChannelClient, HTTPResponse
    from channel_suite import Suite

# ################################################################################################################################
# ################################################################################################################################

_challenge = 'Basic realm="zato"'

# ################################################################################################################################
# ################################################################################################################################

def _assert_basic_rejected(response:'HTTPResponse') -> 'None':
    """ Asserts that a request was rejected with the Basic Auth challenge and a body that names the CID.
    """
    assert response.status == UNAUTHORIZED, response.body
    assert response.headers['content-type'] == 'application/json'
    assert response.get_header_values('WWW-Authenticate') == [_challenge]

    data = response.json()
    cid = data['cid']

    assert data['result'] == 'Error'
    assert data['details'] == f'Unauthorized; cid={cid}'

# ################################################################################################################################
# ################################################################################################################################

def test_valid_credentials(client:'ChannelClient') -> 'None':
    authorization = basic_auth_header(Credentials.Basic_Username, Credentials.Basic_Password)
    response = client.get(Paths.Basic, {'Authorization': authorization})

    assert response.status == OK
    security = response.json()['channel']['security']

    assert security['name'] == Security.Basic
    assert security['username'] == Credentials.Basic_Username
    assert response.get_header_values('WWW-Authenticate') == []

# ################################################################################################################################

def test_wrong_password(client:'ChannelClient') -> 'None':
    authorization = basic_auth_header(Credentials.Basic_Username, 'Wrong.Password.1')
    _assert_basic_rejected(client.get(Paths.Basic, {'Authorization': authorization}))

# ################################################################################################################################

def test_wrong_username(client:'ChannelClient') -> 'None':
    authorization = basic_auth_header('mary.johnson', Credentials.Basic_Password)
    _assert_basic_rejected(client.get(Paths.Basic, {'Authorization': authorization}))

# ################################################################################################################################

def test_missing_header(client:'ChannelClient') -> 'None':
    _assert_basic_rejected(client.get(Paths.Basic))

# ################################################################################################################################

def test_malformed_header(client:'ChannelClient') -> 'None':
    without_colon = 'Basic ' + base64.b64encode(b'john.smith').decode('ascii')

    for authorization in ('Basic !!!not-base64', without_colon, 'Bearer customer-token', 'Basic', ''):
        _assert_basic_rejected(client.get(Paths.Basic, {'Authorization': authorization}))

# ################################################################################################################################

def test_non_ascii_credentials(client:'ChannelClient') -> 'None':
    authorization = basic_auth_header(Credentials.Unicode_Username, Credentials.Unicode_Password)
    response = client.get(Paths.Basic_Unicode, {'Authorization': authorization})

    assert response.status == OK
    assert response.json()['channel']['security']['username'] == Credentials.Unicode_Username

    # The password contains colons, so only the first colon separates it from the username
    authorization = basic_auth_header(Credentials.Unicode_Username, 'pässwörd')
    _assert_basic_rejected(client.get(Paths.Basic_Unicode, {'Authorization': authorization}))

# ################################################################################################################################

def test_inactive_definition(client:'ChannelClient') -> 'None':
    authorization = basic_auth_header(Credentials.Inactive_Username, Credentials.Inactive_Password)
    response = client.get(Paths.Basic_Inactive, {'Authorization': authorization})

    assert_unauthorized(response)

# ################################################################################################################################

def test_credentials_of_another_definition(client:'ChannelClient') -> 'None':
    authorization = basic_auth_header(Credentials.Group_Extra_Username, Credentials.Group_Extra_Password)
    _assert_basic_rejected(client.get(Paths.Basic, {'Authorization': authorization}))

# ################################################################################################################################

def test_password_changed(suite:'Suite') -> 'None':
    client = suite.client

    first = {'Authorization': basic_auth_header(Credentials.Changing_Username, Credentials.Changing_Password_First)}
    second = {'Authorization': basic_auth_header(Credentials.Changing_Username, Credentials.Changing_Password_Second)}

    assert client.get(Paths.Basic_Changing, first).status == OK
    _assert_basic_rejected(client.get(Paths.Basic_Changing, second))

    try:
        suite.import_yaml(basic_changing_password=Credentials.Changing_Password_Second)

        def _is_changed() -> 'bool':
            out = client.get(Paths.Basic_Changing, second).status == OK
            return out

        _ = wait_until(_is_changed)
        _assert_basic_rejected(client.get(Paths.Basic_Changing, first))

    finally:
        suite.restore_yaml()

    def _is_restored() -> 'bool':
        out = client.get(Paths.Basic_Changing, first).status == OK
        return out

    _ = wait_until(_is_restored)

# ################################################################################################################################
# ################################################################################################################################
