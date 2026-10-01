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
    """ What a person fills in on the custom connector form of Claude.ai and Claude Desktop - the fields as the
    form names them, there is no file.
    """
    form = {
        'Name': 'Billing',
        'Remote MCP server URL': gateway_url,
        'OAuth Client ID': client_id,
    }

    out = dumps(form, indent=4)
    return out

# ################################################################################################################################
# ################################################################################################################################

# Claude.ai and Claude Desktop present a pre-registered client ID from the hosted redirect URI of claude.ai,
# ask for a token with no resource parameter, and connect through the connector form
Profile = ClientProfile(
    product='Claude',
    client_id=keycloak_oauth.Client_Claude_AI.client_id,
    redirect_uri=keycloak_oauth.Client_Claude_AI.redirect_uri,
    sends_resource=False,
    is_dynamic_registration=False,
    is_json_config=True,
    build_config=build_config,
)

# ################################################################################################################################
# ################################################################################################################################

class TestClaude(ClientSuite):
    profile = Profile

# ################################################################################################################################
# ################################################################################################################################
