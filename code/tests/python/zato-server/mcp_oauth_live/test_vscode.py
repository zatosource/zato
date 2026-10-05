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
    """ What a person writes into .vscode/mcp.json to connect VS Code to the gateway with a pre-registered client.
    """
    config = {
        'servers': {
            'billing': {
                'type': 'http',
                'url': gateway_url,
                'oauth': {
                    'clientId': client_id,
                },
            },
        },
    }

    out = dumps(config, indent=4)
    return out

# ################################################################################################################################
# ################################################################################################################################

# VS Code presents a pre-registered client ID from its loopback redirect URI, names the gateway it wants
# a token for in the resource parameter, and connects through .vscode/mcp.json
Profile = ClientProfile(
    product='VS Code',
    client_id=keycloak_oauth.Client_VSCode.client_id,
    redirect_uri=keycloak_oauth.Client_VSCode.redirect_uri,
    sends_resource=True,
    is_dynamic_registration=False,
    is_json_config=True,
    build_config=build_config,
)

# ################################################################################################################################
# ################################################################################################################################

class TestVSCode(ClientSuite):
    profile = Profile

# ################################################################################################################################
# ################################################################################################################################
