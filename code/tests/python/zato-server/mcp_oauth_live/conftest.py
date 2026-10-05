# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys
import tempfile
import time
from http.client import OK

_this_directory = os.path.dirname(__file__)

sys.path.insert(0, os.path.join(_this_directory, '..', '..', 'zato-common', 'lib'))
sys.path.insert(0, os.path.join(_this_directory, '..', '..', 'zato-common', 'test'))
sys.path.insert(0, _this_directory)

# pytest
import pytest  # noqa: E402

# requests
import requests  # noqa: E402

# Zato
from zato.common.crypto.api import CryptoManager  # noqa: E402
from zato.common.util.mcp_oauth import Server_Address_Env_Key  # noqa: E402

# Live environment
from live_environment.parts import Parts, tear_down  # noqa: E402
from live_environment.quickstart import Host, ZatoEnvironment  # noqa: E402

# Zato - test helpers
import keycloak_  # noqa: E402
import keycloak_oauth  # noqa: E402

# local
from _common import api_key_caller, ModuleCtx, OAuthLiveEnvironment, tool_names  # noqa: E402

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, iterator_, tupnone

# ################################################################################################################################
# ################################################################################################################################

def pytest_report_teststatus(report:'any_', config:'any_') -> 'tupnone':
    if report.when == 'call':
        outcome = report.outcome.upper()
        return report.outcome, f' {outcome} ', f'{outcome} {report.nodeid}'
    return None

# ################################################################################################################################
# ################################################################################################################################

def _build_definitions(api_key:'str') -> 'str':
    """ The security definitions, groups and gateways the tests run against, as the YAML a user would import.
    """
    issuer = keycloak_.get_issuer()

    out = f'''\
security:
  - name: {ModuleCtx.Definition_Name}
    type: bearer_token
    username: {ModuleCtx.Definition_Username}
    issuer: {issuer}
    audience: {keycloak_.Audience_Main}
    identity_claim: {keycloak_oauth.Claim_Username}
    claims:
      - {keycloak_oauth.Claim_Groups}={keycloak_oauth.Group_Billing_Agents}
  - name: {ModuleCtx.Limited_Definition_Name}
    type: bearer_token
    username: {ModuleCtx.Limited_Definition_Username}
    issuer: {issuer}
    audience: {keycloak_.Audience_Main}
    identity_claim: {keycloak_oauth.Claim_Username}
    rate_limiting:
      - cidr_list:
          - 0.0.0.0/0
        time_range:
          - is_all_day: true
            disabled: false
            disallowed: false
            rate: 1000
            burst: 1000
            limit: {ModuleCtx.Daily_Limit}
            limit_unit: day
  - name: {ModuleCtx.Key_Definition_Name}
    type: apikey
    header: {ModuleCtx.Key_Header}
    password: "{api_key}"

groups:
  - name: {ModuleCtx.Group_Name}
    members:
      - {ModuleCtx.Definition_Name}
  - name: {ModuleCtx.Limited_Group_Name}
    members:
      - {ModuleCtx.Limited_Definition_Name}
  - name: {ModuleCtx.Key_Group_Name}
    members:
      - {ModuleCtx.Key_Definition_Name}

mcp_gateway:
  - name: {ModuleCtx.Gateway_Name}
    is_active: true
    is_audit_log_active: true
    url_path: {ModuleCtx.Gateway_Path}
    oauth: true
    oauth_scopes: {ModuleCtx.Scopes}
    services:
      - {ModuleCtx.Echo_Service}
    security_groups:
      - {ModuleCtx.Group_Name}
  - name: {ModuleCtx.Limited_Gateway_Name}
    is_active: true
    is_audit_log_active: true
    url_path: {ModuleCtx.Limited_Gateway_Path}
    oauth: true
    services:
      - {ModuleCtx.Echo_Service}
    security_groups:
      - {ModuleCtx.Limited_Group_Name}
  - name: {ModuleCtx.Key_Gateway_Name}
    is_active: true
    is_audit_log_active: true
    url_path: {ModuleCtx.Key_Gateway_Path}
    services:
      - {ModuleCtx.Echo_Service}
    security_groups:
      - {ModuleCtx.Key_Group_Name}
'''
    return out

# ################################################################################################################################

def _wait_for_tools(gateway_url:'str', api_key:'str') -> 'None':
    """ Waits until the gateway secured with the key lists the demo service, which is the moment every
    gateway's tool registry holds the services the start deployed.
    """
    deadline = time.monotonic() + ModuleCtx.Tools_Timeout
    caller = api_key_caller(gateway_url, api_key)

    while time.monotonic() < deadline:

        try:
            response = caller.tools_list_stateless()
        except requests.exceptions.ConnectionError:
            time.sleep(ModuleCtx.Tools_Poll_Interval)
            continue

        if response.status_code == OK:
            if ModuleCtx.Echo_Service in tool_names(response):
                return

        time.sleep(ModuleCtx.Tools_Poll_Interval)

    raise Exception(f'`{ModuleCtx.Echo_Service}` did not appear in the tools of {gateway_url} within {ModuleCtx.Tools_Timeout}s')

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def oauth_live() -> 'iterator_':
    """ One Keycloak and one Zato server for the whole session - the server told the address clients reach it under,
    so the challenge and the metadata document name the same address the tests use.
    """
    parts = Parts()

    try:
        keycloak_.ensure_keycloak()

        directory = tempfile.mkdtemp(prefix='zato_mcp_oauth_live_')
        zato = ZatoEnvironment(directory, password_prefix='test.mcp.oauth')
        parts.add('zato environment', zato.stop)
        zato.create()

        server_address = f'http://{Host}:{zato.server_port}'
        zato.start({Server_Address_Env_Key: server_address})

        api_key = 'test.mcp.oauth.key.' + CryptoManager.generate_hex_string()
        _ = zato.import_yaml('mcp_oauth_live.yaml', _build_definitions(api_key))

        key_gateway_url = server_address + ModuleCtx.Key_Gateway_Path
        _wait_for_tools(key_gateway_url, api_key)

        out = OAuthLiveEnvironment(
            zato=zato,
            server_address=server_address,
            gateway_url=server_address + ModuleCtx.Gateway_Path,
            limited_gateway_url=server_address + ModuleCtx.Limited_Gateway_Path,
            key_gateway_url=key_gateway_url,
            api_key=api_key,
            audit_db_path=zato.audit_db_path,
        )
        yield out

    finally:
        tear_down(parts)

# ################################################################################################################################
# ################################################################################################################################
