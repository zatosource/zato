# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import dumps

# local
from _steps import ClientProfile, ClientSuite

# ################################################################################################################################
# ################################################################################################################################

ChatGPT_Redirect_URI = 'https://chatgpt.com/connector_platform_oauth_redirect'

# ################################################################################################################################
# ################################################################################################################################

def build_config(gateway_url:'str', client_id:'str') -> 'str':
    """ What a person fills in when adding the gateway as a ChatGPT connector - ChatGPT registers itself with the
    authorization server, so the only thing to enter is the URL and the client ID is whatever registration gave it.
    """
    form = {
        'Name': 'Billing',
        'MCP Server URL': gateway_url,
        'Authentication': 'OAuth',
        'Registered client ID': client_id,
    }

    out = dumps(form, indent=4)
    return out

# ################################################################################################################################
# ################################################################################################################################

# ChatGPT has no client ID of its own ahead of time - it registers one dynamically with the authorization server,
# from its hosted redirect URI, and asks for a token with no resource parameter
Profile = ClientProfile(
    product='ChatGPT',
    client_id='',
    redirect_uri=ChatGPT_Redirect_URI,
    sends_resource=False,
    is_dynamic_registration=True,
    is_json_config=True,
    build_config=build_config,
)

# ################################################################################################################################
# ################################################################################################################################

class TestChatGPT(ClientSuite):
    profile = Profile

# ################################################################################################################################
# ################################################################################################################################
