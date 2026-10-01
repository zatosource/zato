# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import dumps

# Zato - test helpers
import keycloak_oauth

# local
from _steps import ClientProfile, ClientSuite

# ################################################################################################################################
# ################################################################################################################################

def build_config(gateway_url:'str', client_id:'str') -> 'str':
    """ What a person writes into .cursor/mcp.json to connect Cursor to the gateway with a pre-registered client.
    """
    config = {
        'mcpServers': {
            'billing': {
                'url': gateway_url,
                'auth': {
                    'CLIENT_ID': client_id,
                },
            },
        },
    }

    out = dumps(config, indent=4)
    return out

# ################################################################################################################################
# ################################################################################################################################

# Cursor presents a pre-registered client ID from its fixed loopback redirect URI, asks for a token with no
# resource parameter, and connects through .cursor/mcp.json
Profile = ClientProfile(
    product='Cursor',
    client_id=keycloak_oauth.Client_Cursor.client_id,
    redirect_uri=keycloak_oauth.Client_Cursor.redirect_uri,
    sends_resource=False,
    is_dynamic_registration=False,
    is_json_config=True,
    build_config=build_config,
)

# ################################################################################################################################
# ################################################################################################################################

class TestCursor(ClientSuite):
    profile = Profile

# ################################################################################################################################
# ################################################################################################################################
