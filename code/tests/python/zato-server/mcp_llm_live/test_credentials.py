# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time
from http.client import FORBIDDEN, OK

# pytest
import pytest

# local
import _agent
import _audit
import _constants
import _enmasse
import _helpers
import _markers
import containers
import keycloak_

# Zato
from zato.common.audit_log.api import AuditEvent, AuditOutcome

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

# How long a group membership change from a re-import may take to reach live enforcement, in seconds
_reimport_timeout = 60

# How often to poll for it, in seconds
_reimport_poll_interval = 0.5

# How long past its lifespan to wait before using a short-lived token, in seconds
_token_expiry_wait = keycloak_.Short_Token_Lifespan + 2

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='module')
def keycloak() -> 'None':
    """ The Keycloak-issued token tests need the container running and provisioned.
    """

    if not containers.is_docker_available():
        pytest.skip('Docker is not available')

    keycloak_.ensure_keycloak()

# ################################################################################################################################
# ################################################################################################################################

def _wait_until_status(client:'_helpers.MCPClient', extra_headers:'anydict | None', expected_status:'int') -> 'None':
    """ Polls with initialize requests until the expected status code comes back,
    which is how the tests wait for a re-imported group change to reach enforcement.
    """

    deadline = time.monotonic() + _reimport_timeout
    last_status = 0

    while time.monotonic() < deadline:

        response = _helpers.initialize_response(client, extra_headers)
        last_status = response.status_code

        if last_status == expected_status:
            return

        time.sleep(_reimport_poll_interval)

    raise Exception(
        f'Status {expected_status} did not arrive within {_reimport_timeout}s, last was {last_status}')

# ################################################################################################################################
# ################################################################################################################################

class TestBasicAuth:
    """ HTTP basic credentials are accepted only when both the username and the password
    match a member of the gateway's group.
    """

# ################################################################################################################################

    def test_valid_credentials_complete_a_whole_task(self, zato_server:'anydict', ollama:'anydict') -> 'None':

        client = _helpers.make_client(zato_server, _constants.Path_Main)

        task = f'What city does customer {_constants.Customer_ID} live in? Use the tools.'

        result = _agent.run_agent(client, task)

        assert result.tool_calls, result.messages
        assert _helpers.text_contains(result.final_text, _constants.Customer_City), result.final_text

# ################################################################################################################################

    def test_rejected_credentials_never_reach_a_tool(self, zato_server:'anydict') -> 'None':

        marker_path = zato_server['marker_path']
        audit_db_path = zato_server['audit_db_path']

        username, password = zato_server['basic_auth']

        # Wrong password, wrong username and no credentials at all are all refused the same way
        rejected_clients = [
            _helpers.make_client(zato_server, _constants.Path_Main, auth=(username, 'wrong-' + password)),
            _helpers.make_client(zato_server, _constants.Path_Main, auth=('wrong-' + username, password)),
            _helpers.make_client(zato_server, _constants.Path_Main, auth=None),
        ]

        invocations_before = len(_markers.read_invocations(marker_path))
        min_id = _audit.last_event_id(audit_db_path)

        for client in rejected_clients:

            response = _helpers.initialize_response(client)
            assert response.status_code == FORBIDDEN, (client.auth, response.status_code, response.text)

        # No tool executed for any of the rejected requests ..
        invocations_after = len(_markers.read_invocations(marker_path))
        assert invocations_after == invocations_before, (invocations_before, invocations_after)

        # .. and each rejection is audited with an error outcome and an empty caller identity.
        events = _audit.wait_for_events(
            audit_db_path, len(rejected_clients),
            object_name=_constants.Gateway_Main,
            event_type=AuditEvent.Auth_Failed,
            min_id=min_id)

        for event in events:
            assert event['outcome'] == AuditOutcome.Error, event
            assert event['ext_client_id'] == '', event

# ################################################################################################################################
# ################################################################################################################################

class TestAPIKey:
    """ API key credentials travel in their own header and are accepted and rejected
    the same way basic credentials are.
    """

# ################################################################################################################################

    def test_valid_key_is_accepted(self, zato_server:'anydict') -> 'None':

        client = _helpers.make_client(zato_server, _constants.Path_Main, auth=None)
        headers = _helpers.apikey_headers(zato_server['apikey_value'])

        session_id = _helpers.open_session(client, extra_headers=headers)

        body = _helpers.call_tool(
            client, session_id, _constants.Service_Order_Status,
            {'order_id': _constants.Order_ID}, extra_headers=headers)

        data = _helpers.get_result_data(body)
        assert data['status'] == _constants.Order_Status, body

# ################################################################################################################################

    def test_wrong_key_is_rejected(self, zato_server:'anydict') -> 'None':

        client = _helpers.make_client(zato_server, _constants.Path_Main, auth=None)
        headers = _helpers.apikey_headers('wrong-' + zato_server['apikey_value'])

        response = _helpers.initialize_response(client, extra_headers=headers)
        assert response.status_code == FORBIDDEN, response.text

# ################################################################################################################################
# ################################################################################################################################

class TestStaticBearerToken:
    """ A static bearer token authenticates only with its exact value.
    """

# ################################################################################################################################

    def test_valid_token_is_accepted(self, zato_server:'anydict') -> 'None':

        client = _helpers.make_client(zato_server, _constants.Path_Main, auth=None)
        headers = _helpers.bearer_headers(zato_server['bearer_static_token'])

        session_id = _helpers.open_session(client, extra_headers=headers)

        body = _helpers.call_tool(
            client, session_id, _constants.Service_Order_Status,
            {'order_id': _constants.Order_ID}, extra_headers=headers)

        data = _helpers.get_result_data(body)
        assert data['carrier'] == _constants.Order_Carrier, body

# ################################################################################################################################

    def test_wrong_token_is_rejected(self, zato_server:'anydict') -> 'None':

        client = _helpers.make_client(zato_server, _constants.Path_Main, auth=None)
        headers = _helpers.bearer_headers('wrong-' + zato_server['bearer_static_token'])

        response = _helpers.initialize_response(client, extra_headers=headers)
        assert response.status_code == FORBIDDEN, response.text

# ################################################################################################################################
# ################################################################################################################################

class TestKeycloakBearerToken:
    """ Tokens issued by Keycloak are validated against the definition's issuer,
    audience and claims - and only for as long as they live.
    """

# ################################################################################################################################

    def test_issued_token_is_accepted(self, zato_server:'anydict', keycloak:'None') -> 'None':

        token = keycloak_.get_token(keycloak_.Client_Accounting, keycloak_.Secret_Accounting)

        client = _helpers.make_client(zato_server, _constants.Path_Main, auth=None)
        headers = _helpers.bearer_headers(token)

        response = _helpers.initialize_response(client, extra_headers=headers)
        assert response.status_code == OK, response.text

# ################################################################################################################################

    def test_garbage_token_is_rejected(self, zato_server:'anydict', keycloak:'None') -> 'None':

        client = _helpers.make_client(zato_server, _constants.Path_Main, auth=None)
        headers = _helpers.bearer_headers('not-a-token-at-all')

        response = _helpers.initialize_response(client, extra_headers=headers)
        assert response.status_code == FORBIDDEN, response.text

# ################################################################################################################################

    def test_expired_token_is_rejected(self, zato_server:'anydict', keycloak:'None') -> 'None':

        token = keycloak_.get_token(keycloak_.Client_Short_Lived, keycloak_.Secret_Short_Lived)

        # The token lives for one second, so by now it has expired
        time.sleep(_token_expiry_wait)

        client = _helpers.make_client(zato_server, _constants.Path_Main, auth=None)
        headers = _helpers.bearer_headers(token)

        response = _helpers.initialize_response(client, extra_headers=headers)
        assert response.status_code == FORBIDDEN, response.text

# ################################################################################################################################
# ################################################################################################################################

class TestGroupMembershipChanges:
    """ Group membership changes from a re-import reach live enforcement without a restart.
    """

# ################################################################################################################################

    def test_removing_a_definition_from_the_group_takes_effect_live(self, zato_server:'anydict') -> 'None':

        server_directory = zato_server['server_directory']

        client = _helpers.make_client(zato_server, _constants.Path_Main, auth=None)
        headers = _helpers.apikey_headers(zato_server['apikey_value'])

        # The key works before the change ..
        response = _helpers.initialize_response(client, extra_headers=headers)
        assert response.status_code == OK, response.text

        # .. a re-import removes the API key definition from the main group ..
        members_without_apikey = [
            _constants.Sec_Basic,
            _constants.Sec_Bearer_Static,
            _constants.Sec_Bearer_Keycloak,
        ]

        try:
            config = _enmasse.build_suite_config(main_members=members_without_apikey)
            _enmasse.run_import(server_directory, config)

            # .. and the previously working key is refused on the next call ..
            _wait_until_status(client, headers, FORBIDDEN)

        finally:
            # .. the standard configuration always comes back for the other tests.
            config = _enmasse.build_suite_config()
            _enmasse.run_import(server_directory, config)

            _wait_until_status(client, headers, OK)

# ################################################################################################################################
# ################################################################################################################################

class TestCallerIdentityInAuditEvents:
    """ Every audited event names the security definition its caller authenticated with.
    """

# ################################################################################################################################

    def test_events_name_the_definition_of_each_credential_type(self, zato_server:'anydict', keycloak:'None') -> 'None':

        audit_db_path = zato_server['audit_db_path']
        min_id = _audit.last_event_id(audit_db_path)

        arguments = {'order_id': _constants.Order_ID}

        # One tools/call per credential type, each expected to audit under its own definition
        basic_client = _helpers.make_client(zato_server, _constants.Path_Main)
        basic_session = _helpers.open_session(basic_client)
        _ = _helpers.call_tool(basic_client, basic_session, _constants.Service_Order_Status, arguments)

        apikey_client = _helpers.make_client(zato_server, _constants.Path_Main, auth=None)
        apikey_auth_headers = _helpers.apikey_headers(zato_server['apikey_value'])
        apikey_session = _helpers.open_session(apikey_client, extra_headers=apikey_auth_headers)
        _ = _helpers.call_tool(
            apikey_client, apikey_session, _constants.Service_Order_Status, arguments,
            extra_headers=apikey_auth_headers)

        bearer_client = _helpers.make_client(zato_server, _constants.Path_Main, auth=None)
        bearer_auth_headers = _helpers.bearer_headers(zato_server['bearer_static_token'])
        bearer_session = _helpers.open_session(bearer_client, extra_headers=bearer_auth_headers)
        _ = _helpers.call_tool(
            bearer_client, bearer_session, _constants.Service_Order_Status, arguments,
            extra_headers=bearer_auth_headers)

        keycloak_token = keycloak_.get_token(keycloak_.Client_Accounting, keycloak_.Secret_Accounting)
        keycloak_client = _helpers.make_client(zato_server, _constants.Path_Main, auth=None)
        keycloak_auth_headers = _helpers.bearer_headers(keycloak_token)
        keycloak_session = _helpers.open_session(keycloak_client, extra_headers=keycloak_auth_headers)
        _ = _helpers.call_tool(
            keycloak_client, keycloak_session, _constants.Service_Order_Status, arguments,
            extra_headers=keycloak_auth_headers)

        # Four calls, four events, each carrying its own caller identity and tool name
        events = _audit.wait_for_events(
            audit_db_path, 4,
            object_name=_constants.Gateway_Main,
            event_type=AuditEvent.MCP_Tools_Call,
            min_id=min_id)

        identities = []

        for event in events:
            identities.append(event['ext_client_id'])
            assert event['endpoint'] == _constants.Service_Order_Status, event

        expected = [
            _constants.Sec_Basic,
            _constants.Sec_APIKey,
            _constants.Sec_Bearer_Static,
            _constants.Sec_Bearer_Keycloak,
        ]
        assert identities == expected, identities

# ################################################################################################################################
# ################################################################################################################################
