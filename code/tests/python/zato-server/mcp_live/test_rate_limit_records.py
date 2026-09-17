# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What the alerting of a gateway reads off the live server - a caller over its definition's rate limit is answered
# 429 with a Retry-After header and, with the audit log on, one rate-limited row naming the definition lands in the
# audit database, and the tools/list the tool count is read off is exactly the services the gateway was deployed with.

# stdlib
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from http.client import TOO_MANY_REQUESTS
from json import loads

# local
from _client import MCPClient
from test_audit_log import _get_demo_gateway, _read_events, _set_audit_log_active, _wait_until_audit_is_on

# Zato
from zato.common.audit_log.api import AuditEvent, AuditOutcome, AuditSource
from zato.common.rate_limiting.headers import Header_Retry_After

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

# The services the demo gateway exposes, as the live conftest deploys them
_demo_services = ['demo.echo', 'test.raise']

# What an initialize request carries - sent by hand for the one request that is refused before it gets a session
_initialize_params = {
    'protocolVersion': '2025-06-18',
    'capabilities': {},
    'clientInfo': {'name': 'zato-mcp-test', 'version': '1.0'},
}

# ################################################################################################################################
# ################################################################################################################################

def _exhaust_the_limit(zato_server:'anydict') -> 'MCPClient':
    """ Sends the limited caller's whole daily allowance as initialize requests and returns its client.
    """
    client = MCPClient(zato_server['mcp_url'], auth=zato_server['mcp_auth_limited'])

    for _ in range(zato_server['mcp_limited_daily_limit']):
        response = client.initialize().response
        assert response.status_code != TOO_MANY_REQUESTS, response.text

    return client

# ################################################################################################################################
# ################################################################################################################################

class TestRateLimitedCaller:
    """ A caller over its limit is refused before any JSON-RPC processing and the refusal is recorded.
    """

    def test_a_caller_over_its_limit_is_answered_429_and_audited(self, zato_server:'anydict') -> 'None':

        gateway = _get_demo_gateway(zato_server)

        try:
            _set_audit_log_active(zato_server, gateway, True)
            last_seen_id = _wait_until_audit_is_on(zato_server)

            client = _exhaust_the_limit(zato_server)

            # The next request is one too many - refused before it is answered with a session ..
            response = client.jsonrpc('initialize', params=_initialize_params)

            assert response.status_code == TOO_MANY_REQUESTS, response.text

            # A daily limit resets at midnight, so the header names that moment as an HTTP date
            assert Header_Retry_After in response.headers, response.headers
            retry_after = parsedate_to_datetime(response.headers[Header_Retry_After])
            assert retry_after > datetime.now(timezone.utc), retry_after

            # .. and its row is the one rate-limited event naming the caller's definition.
            events = _read_events(zato_server, min_id=last_seen_id)
            rate_limited = [event for event in events if event['event_type'] == AuditEvent.Rate_Limited]

            assert len(rate_limited) == 1, events

            event = rate_limited[0]
            assert event['source'] == AuditSource.MCP
            assert event['ext_client_id'] == zato_server['mcp_sec_def_name_limited']
            assert event['outcome'] == AuditOutcome.Error
            assert event['endpoint'] == ''

            data = loads(event['data'])
            assert data['retry_after_seconds'] >= 1
            assert data['remote_address']

        finally:
            _set_audit_log_active(zato_server, gateway, False)

# ################################################################################################################################
# ################################################################################################################################

class TestToolCount:
    """ The number the Too_Many_Tools rule reads is the length of what tools/list returns - the services deployed.
    """

    def test_the_tools_list_is_the_services_the_gateway_exposes(self, zato_server:'anydict') -> 'None':

        client = MCPClient(zato_server['mcp_url'], auth=zato_server['mcp_auth'])
        session_id = client.initialize().session_id

        response = client.jsonrpc('tools/list', session_id=session_id)
        tools = response.json()['result']['tools']

        assert len(tools) == len(_demo_services), tools
        assert sorted(tool['name'] for tool in tools) == sorted(_demo_services)

# ################################################################################################################################
# ################################################################################################################################
