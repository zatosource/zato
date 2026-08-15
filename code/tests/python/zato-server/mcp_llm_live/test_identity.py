# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time
from http.client import BAD_REQUEST, OK

# local
import _audit
import _constants
import _helpers
import keycloak_
from _helpers import wait_until as _wait_until

# Zato
from zato.common.audit_log.api import AuditEvent, AuditOutcome
from zato.common.test import rand_string

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

# How long to wait until a short-lived token has provably expired, in seconds
_past_token_expiry_seconds = keycloak_.Short_Token_Lifespan + 2

# The admin service that changes a basic auth password
_service_change_password = 'zato.security.basic-auth.change-password'

# ################################################################################################################################
# ################################################################################################################################

class TestIdentityOverTime:
    """ Credentials over their lifetime - a password change, a token expiry,
    a session's binding to its credential and the audit trail of a rejection
    followed by an acceptance.
    """

# ################################################################################################################################

    def test_a_password_change_takes_effect_live(self, zato_server:'anydict') -> 'None':

        old_auth = (_constants.Username_Basic_B, _constants.Password_Basic_B)
        old_client = _helpers.make_client(zato_server, _constants.Path_Identity, auth=old_auth)

        # The current password is accepted before the change ..
        response = _helpers.initialize_response(old_client)
        assert response.status_code == OK, response.text

        new_password = 'test.llm.b.' + rand_string()

        new_auth = (_constants.Username_Basic_B, new_password)
        new_client = _helpers.make_client(zato_server, _constants.Path_Identity, auth=new_auth)

        try:
            # .. one password-change call swaps the password ..
            _ = _helpers.admin_invoke(zato_server, _service_change_password, {
                'name': _constants.Sec_Basic_B,
                'password': new_password,
            })

            # .. the old password is refused on the next call ..
            def old_password_is_refused() -> 'bool':
                response = _helpers.initialize_response(old_client)
                out = response.status_code != OK
                return out

            _wait_until(old_password_is_refused, 'the old password is refused')

            # .. and the new one is accepted, no restart anywhere.
            response = _helpers.initialize_response(new_client)
            assert response.status_code == OK, response.text

        finally:
            # The original password always comes back for the other tests.
            _ = _helpers.admin_invoke(zato_server, _service_change_password, {
                'name': _constants.Sec_Basic_B,
                'password': _constants.Password_Basic_B,
            })

            def old_password_is_back() -> 'bool':
                response = _helpers.initialize_response(old_client)
                out = response.status_code == OK
                return out

            _wait_until(old_password_is_back, 'the original password is accepted again')

# ################################################################################################################################

    def test_a_keycloak_token_expires_mid_session(self, zato_server:'anydict', keycloak:'None') -> 'None':

        token = keycloak_.get_token(keycloak_.Client_Short_Lived, keycloak_.Secret_Short_Lived)
        headers = _helpers.bearer_headers(token)

        client = _helpers.make_client(zato_server, _constants.Path_Main, auth=None)

        # The session works while the token lives ..
        session_id = _helpers.open_session(client, extra_headers=headers)

        response = client.jsonrpc('tools/list', session_id=session_id, extra_headers=headers)
        assert response.status_code == OK, response.text

        # .. and the same session's calls are refused once the token expires -
        # validation is per request, not per session.
        time.sleep(_past_token_expiry_seconds)

        response = client.jsonrpc('tools/list', session_id=session_id, extra_headers=headers)
        assert response.status_code != OK, response.text

# ################################################################################################################################

    def test_a_session_is_bound_to_its_credential(self, zato_server:'anydict') -> 'None':

        # A session opened with Basic Auth ..
        basic_client = _helpers.make_client(zato_server, _constants.Path_Main)
        session_id = _helpers.open_session(basic_client)

        # .. keeps working for the identity that created it ..
        response = basic_client.jsonrpc('tools/list', session_id=session_id)
        assert response.status_code == OK, response.text

        # .. and is refused when presented with the API key, a credential
        # the same gateway otherwise accepts.
        apikey_client = _helpers.make_client(zato_server, _constants.Path_Main, auth=None)
        headers = _helpers.apikey_headers(zato_server['apikey_value'])

        response = apikey_client.jsonrpc('tools/list', session_id=session_id, extra_headers=headers)
        assert response.status_code == BAD_REQUEST, response.text

# ################################################################################################################################

    def test_rejection_and_acceptance_audit_separately(self, zato_server:'anydict') -> 'None':

        audit_db_path = zato_server['audit_db_path']
        min_id = _audit.last_event_id(audit_db_path)

        # The wrong password is rejected first ..
        wrong_auth = (_constants.Username_Basic, 'test.llm.wrong.' + rand_string())
        wrong_client = _helpers.make_client(zato_server, _constants.Path_Main, auth=wrong_auth)

        response = _helpers.initialize_response(wrong_client)
        assert response.status_code != OK, response.text

        # .. then the right one is accepted ..
        client = _helpers.make_client(zato_server, _constants.Path_Main)
        session_id = _helpers.open_session(client)
        assert session_id, session_id

        # .. the rejection audits with an empty identity ..
        rejection_events = _audit.wait_for_events(
            audit_db_path, 1,
            object_name=_constants.Gateway_Main,
            event_type=AuditEvent.Auth_Failed,
            min_id=min_id)

        rejection = rejection_events[-1]
        assert rejection['outcome'] == AuditOutcome.Error, rejection
        assert rejection['ext_client_id'] == '', rejection

        # .. and the acceptance audits with the definition that admitted the caller.
        initialize_events = _audit.wait_for_events(
            audit_db_path, 1,
            object_name=_constants.Gateway_Main,
            event_type=AuditEvent.MCP_Initialize,
            min_id=min_id)

        acceptance = initialize_events[-1]
        assert acceptance['outcome'] == AuditOutcome.OK, acceptance
        assert acceptance['ext_client_id'] == _constants.Sec_Basic, acceptance
        assert acceptance['sub_key'] == session_id, acceptance

# ################################################################################################################################
# ################################################################################################################################
