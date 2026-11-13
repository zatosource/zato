# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Channels secured with API key definitions.

# stdlib
from http.client import OK

# Zato
from channel_definitions import Credentials, Paths, Security
from channel_suite import assert_unauthorized, wait_until

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from channel_client import ChannelClient
    from channel_suite import Suite

# ################################################################################################################################
# ################################################################################################################################

_default_header = 'X-API-Key'

# ################################################################################################################################
# ################################################################################################################################

def test_valid_key(client:'ChannelClient') -> 'None':
    response = client.get(Paths.API_Key, {_default_header: Credentials.API_Key})

    assert response.status == OK
    security = response.json()['channel']['security']

    assert security['name'] == Security.API_Key
    assert security['type'] == 'apikey'

# ################################################################################################################################

def test_header_name_case_insensitive(client:'ChannelClient') -> 'None':
    response = client.get(Paths.API_Key, {'x-api-key': Credentials.API_Key})
    assert response.status == OK

# ################################################################################################################################

def test_wrong_key(client:'ChannelClient') -> 'None':
    assert_unauthorized(client.get(Paths.API_Key, {_default_header: 'wrong-api-key'}))

# ################################################################################################################################

def test_missing_header(client:'ChannelClient') -> 'None':
    assert_unauthorized(client.get(Paths.API_Key))

# ################################################################################################################################

def test_key_of_another_definition(client:'ChannelClient') -> 'None':
    assert_unauthorized(client.get(Paths.API_Key, {_default_header: Credentials.Group_API_Key}))

# ################################################################################################################################

def test_custom_header(client:'ChannelClient') -> 'None':

    response = client.get(Paths.API_Key_Custom, {Credentials.API_Key_Custom_Header: Credentials.API_Key_Custom})
    assert response.status == OK
    assert response.json()['channel']['security']['name'] == Security.API_Key_Custom

    # The key in the default header is not read by a definition with a header of its own
    assert_unauthorized(client.get(Paths.API_Key_Custom, {_default_header: Credentials.API_Key_Custom}))

# ################################################################################################################################

def test_key_changed(suite:'Suite') -> 'None':
    client = suite.client

    first = {_default_header: Credentials.API_Key_Changing_First}
    second = {_default_header: Credentials.API_Key_Changing_Second}

    assert client.get(Paths.API_Key_Changing, first).status == OK
    assert_unauthorized(client.get(Paths.API_Key_Changing, second))

    try:
        suite.import_yaml(api_key_changing=Credentials.API_Key_Changing_Second)

        def _is_changed() -> 'bool':
            out = client.get(Paths.API_Key_Changing, second).status == OK
            return out

        _ = wait_until(_is_changed)
        assert_unauthorized(client.get(Paths.API_Key_Changing, first))

    finally:
        suite.restore_yaml()

    def _is_restored() -> 'bool':
        out = client.get(Paths.API_Key_Changing, first).status == OK
        return out

    _ = wait_until(_is_restored)

# ################################################################################################################################
# ################################################################################################################################
