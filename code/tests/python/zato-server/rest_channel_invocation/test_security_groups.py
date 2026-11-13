# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Channels secured with security groups whose members are Basic Auth and API key definitions.

# stdlib
from http.client import FORBIDDEN, OK

# Zato
from channel_client import basic_auth_header
from channel_definitions import Credentials, Paths, Security
from channel_suite import assert_json_error, wait_until

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from channel_client import ChannelClient, HTTPResponse
    from channel_suite import Suite
    from zato.common.typing_ import strdict

# ################################################################################################################################
# ################################################################################################################################

_forbidden_details = 'You are not allowed to access this resource'

_basic_member = {'Authorization': basic_auth_header(Credentials.Group_Basic_Username, Credentials.Group_Basic_Password)}
_api_key_member = {'X-API-Key': Credentials.Group_API_Key}
_extra_member = {'Authorization': basic_auth_header(Credentials.Group_Extra_Username, Credentials.Group_Extra_Password)}

# ################################################################################################################################
# ################################################################################################################################

def _assert_forbidden(response:'HTTPResponse') -> 'None':
    _ = assert_json_error(response, FORBIDDEN, _forbidden_details)
    assert response.get_header_values('WWW-Authenticate') == []

# ################################################################################################################################

def _status(client:'ChannelClient', headers:'strdict') -> 'int':
    out = client.get(Paths.Group, headers).status
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_basic_auth_member(client:'ChannelClient') -> 'None':
    response = client.get(Paths.Group, _basic_member)

    assert response.status == OK
    security = response.json()['channel']['security']

    assert security['name'] == Security.Group_Basic
    assert security['type'] == 'basic_auth'
    assert security['username'] == Credentials.Group_Basic_Username

# ################################################################################################################################

def test_api_key_member(client:'ChannelClient') -> 'None':
    response = client.get(Paths.Group, _api_key_member)

    assert response.status == OK
    security = response.json()['channel']['security']

    assert security['name'] == Security.Group_API_Key
    assert security['type'] == 'apikey'

# ################################################################################################################################

def test_no_member_matched(client:'ChannelClient') -> 'None':

    _assert_forbidden(client.get(Paths.Group, _extra_member))
    _assert_forbidden(client.get(Paths.Group))

    wrong_password = {'Authorization': basic_auth_header(Credentials.Group_Basic_Username, 'Wrong.Password.1')}
    _assert_forbidden(client.get(Paths.Group, wrong_password))

    _assert_forbidden(client.get(Paths.Group, {'X-API-Key': 'wrong-api-key'}))

# ################################################################################################################################

def test_empty_group(client:'ChannelClient') -> 'None':
    _assert_forbidden(client.get(Paths.Group_Empty, _basic_member))
    _assert_forbidden(client.get(Paths.Group_Empty))

# ################################################################################################################################

def test_members_changed(suite:'Suite') -> 'None':
    client = suite.client

    assert _status(client, _api_key_member) == OK
    assert _status(client, _extra_member) == FORBIDDEN

    try:

        # One member is added and one is removed ..
        suite.import_yaml(group_members=(Security.Group_Basic, Security.Group_Extra))

        def _is_changed() -> 'bool':
            out = _status(client, _extra_member) == OK
            return out

        _ = wait_until(_is_changed)

        # .. so the removed one is rejected and the one that stayed is still accepted.
        _assert_forbidden(client.get(Paths.Group, _api_key_member))
        assert _status(client, _basic_member) == OK

    finally:
        suite.restore_yaml()

    def _is_restored() -> 'bool':
        out = _status(client, _api_key_member) == OK
        return out

    _ = wait_until(_is_restored)
    assert _status(client, _extra_member) == FORBIDDEN

# ################################################################################################################################
# ################################################################################################################################
