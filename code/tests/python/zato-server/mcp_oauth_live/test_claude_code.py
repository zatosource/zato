# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from urllib.parse import urlsplit

# Zato - test helpers
import keycloak_oauth

# local
from _steps import ClientProfile, ClientSuite

# ################################################################################################################################
# ################################################################################################################################

def build_config(gateway_url:'str', client_id:'str') -> 'str':
    """ The command a person runs to connect Claude Code to the gateway with a pre-registered client - the callback
    port is the one of the redirect URI the client was registered with.
    """
    callback_port = urlsplit(keycloak_oauth.Client_Claude_Code.redirect_uri).port

    out = f'claude mcp add --transport http --client-id {client_id} --callback-port {callback_port} billing {gateway_url}'
    return out

# ################################################################################################################################
# ################################################################################################################################

# Claude Code presents a pre-registered client ID from a loopback redirect URI whose port the person picks,
# names the gateway in the resource parameter, and connects through one command
Profile = ClientProfile(
    product='Claude Code',
    client_id=keycloak_oauth.Client_Claude_Code.client_id,
    redirect_uri=keycloak_oauth.Client_Claude_Code.redirect_uri,
    sends_resource=True,
    is_dynamic_registration=False,
    is_json_config=False,
    build_config=build_config,
)

# ################################################################################################################################
# ################################################################################################################################

class TestClaudeCode(ClientSuite):
    profile = Profile

# ################################################################################################################################
# ################################################################################################################################
