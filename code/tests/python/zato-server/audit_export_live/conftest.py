# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys
import tempfile

_this_directory = os.path.dirname(__file__)

sys.path.insert(0, os.path.join(_this_directory, '..', '..', 'zato-common', 'lib'))
sys.path.insert(0, os.path.join(_this_directory, '..', '..', 'zato-common', 'test'))
sys.path.insert(0, _this_directory)

# pytest
import pytest  # noqa: E402

# Zato
from zato.common.audit_log.export.config import ModuleCtx as ExportCtx  # noqa: E402
from zato.common.crypto.api import CryptoManager  # noqa: E402
from zato.common.util.mcp_oauth import Server_Address_Env_Key  # noqa: E402

# Live environment
from live_environment.parts import Parts, tear_down  # noqa: E402
from live_environment.quickstart import Host, ZatoEnvironment  # noqa: E402
from live_otel.containers import remove_container, start_collector  # noqa: E402

# Zato - test helpers
import keycloak_  # noqa: E402
import keycloak_oauth  # noqa: E402

# local
from _common import build_export_environment, wait_for_tools, AuditExportEnvironment, Exported_Sources, ModuleCtx  # noqa: E402

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

def build_definitions(api_key:'str') -> 'str':
    """ The security definitions, groups, gateways and channels the tests run against, as the YAML a user would import.
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
    username: {ModuleCtx.Definition_Username}
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

channel_rest:
  - name: {ModuleCtx.REST_Channel_Name}
    service: {ModuleCtx.Echo_Service}
    url_path: {ModuleCtx.REST_Channel_Path}
    is_audit_log_active: true
  - name: {ModuleCtx.REST_Payload_Channel_Name}
    service: {ModuleCtx.Echo_Service}
    url_path: {ModuleCtx.REST_Payload_Channel_Path}
    is_audit_log_active: true
    is_audit_export_payload_active: true
'''
    return out

# ################################################################################################################################

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def audit_export_live() -> 'iterator_':
    """ One Keycloak, one OpenTelemetry Collector and one Zato server for the whole session, the server exporting
    its MCP and REST channel audit events to the collector over HTTP with TLS and a bearer token.
    """
    parts = Parts()

    try:
        keycloak_.ensure_keycloak()

        collector = start_collector()
        parts.add('OpenTelemetry Collector', remove_container)

        directory = tempfile.mkdtemp(prefix='zato_audit_export_live_')
        zato = ZatoEnvironment(directory, password_prefix='test.audit.export')
        parts.add('zato environment', zato.stop)
        zato.create()

        server_address = f'http://{Host}:{zato.server_port}'

        environment = build_export_environment(collector, protocol=ExportCtx.Protocol_HTTP, sources=Exported_Sources)
        environment[Server_Address_Env_Key] = server_address

        zato.start(environment)

        api_key = 'test.audit.export.key.' + CryptoManager.generate_hex_string()
        _ = zato.import_yaml('audit_export_live.yaml', build_definitions(api_key))

        key_gateway_url = server_address + ModuleCtx.Key_Gateway_Path
        wait_for_tools(key_gateway_url, api_key)

        out = AuditExportEnvironment(
            zato=zato,
            collector=collector,
            server_address=server_address,
            gateway_url=server_address + ModuleCtx.Gateway_Path,
            limited_gateway_url=server_address + ModuleCtx.Limited_Gateway_Path,
            key_gateway_url=key_gateway_url,
            rest_url=server_address + ModuleCtx.REST_Channel_Path,
            rest_payload_url=server_address + ModuleCtx.REST_Payload_Channel_Path,
            api_key=api_key,
            audit_db_path=zato.audit_db_path,
            server_log_path=os.path.join(zato.server_directory, 'logs', 'server.log'),
        )
        yield out

    finally:
        tear_down(parts)

# ################################################################################################################################
# ################################################################################################################################
