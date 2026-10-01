# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time
from http.client import BAD_REQUEST, FORBIDDEN, NOT_FOUND, OK, TOO_MANY_REQUESTS, UNAUTHORIZED

# requests
import requests

# Zato
from zato.common.alerting.collectors.evidence import collect_failed_events
from zato.common.alerting.collectors.rates import collect_auth_failure_facts
from zato.common.alerting.explain.evidence import group_failures
from zato.common.audit_log.api import AuditEvent, AuditSource
from zato.common.rate_limiting.headers import Header_Retry_After
from zato.common.util.mcp_oauth import get_metadata_url
from zato.common.util.time_ import utcnow

# Zato - test helpers
import keycloak_oauth

# local
from _common import api_key_caller, bearer_caller, last_event_id, ModuleCtx, OAuthLiveEnvironment, tool_names, \
    wait_for_event_of_type
from _steps import audit_engine, expected_identity

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, dictlist, strlist

# ################################################################################################################################
# ################################################################################################################################

# A key the API key gateway was not given
_wrong_api_key = 'not-the-partner-key'

# How far back the alert rule looks for refusals, in seconds
_alert_window_seconds = 300

# How much longer than the token lifespan to wait before using a short-lived token, in seconds
_expiry_wait_extra = 1.5

# The two people on the limited gateway sign in through the same product - which one does not matter here
_client = keycloak_oauth.Client_VSCode

# ################################################################################################################################
# ################################################################################################################################

def _member_token() -> 'str':
    out = keycloak_oauth.get_user_token(
        _client.client_id, _client.redirect_uri, keycloak_oauth.User_Member, keycloak_oauth.Password_Member)
    return out

# ################################################################################################################################

def _outsider_token() -> 'str':
    out = keycloak_oauth.get_user_token(
        _client.client_id, _client.redirect_uri, keycloak_oauth.User_Outsider, keycloak_oauth.Password_Outsider)
    return out

# ################################################################################################################################

def _rows_of_person(rows:'dictlist', identity:'str') -> 'dictlist':
    out = []
    for row in rows:
        if row['ext_client_id'] == identity:
            out.append(row)
    return out

# ################################################################################################################################

def _count_of_person(groups:'dictlist', identity:'str') -> 'int':
    """ How many refusals the groups hold of one person - each group names its callers once, so a group
    counting toward a person must name that person and no one else.
    """
    out = 0
    for group in groups:
        callers:'strlist' = group['callers']
        if identity in callers:
            assert callers == [identity], f'A group of one person names more than one: {group}'
            out += group['count']
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestGatewayWithOAuthOff:
    """ A gateway secured with an API key is untouched by OAuth - it takes its key, refuses a bad one the way it
    always did and publishes no metadata.
    """

    def test_the_key_is_accepted_and_a_bad_one_is_refused_without_a_challenge(self, oauth_live:'OAuthLiveEnvironment') -> 'None':

        response = api_key_caller(oauth_live.key_gateway_url, oauth_live.api_key).tools_list_stateless()
        assert response.status_code == OK, response.text
        assert ModuleCtx.Echo_Service in tool_names(response)

        response = api_key_caller(oauth_live.key_gateway_url, _wrong_api_key).tools_list_stateless()
        assert response.status_code == FORBIDDEN, f'Expected 403, got {response.status_code} -> {response.text}'
        assert ModuleCtx.Challenge_Header not in response.headers, dict(response.headers)
        assert response.text == ''

# ################################################################################################################################

    def test_the_metadata_is_not_served(self, oauth_live:'OAuthLiveEnvironment') -> 'None':

        metadata_url = get_metadata_url(oauth_live.server_address, ModuleCtx.Key_Gateway_Path)
        response = requests.get(metadata_url, timeout=ModuleCtx.HTTP_Timeout)

        assert response.status_code == NOT_FOUND, f'Expected 404, got {response.status_code} -> {response.text}'

# ################################################################################################################################
# ################################################################################################################################

class TestTwoPeopleOnOneDefinition:
    """ Two people let in by the same definition are two callers - the one's session is not the other's and
    the one's calls are not counted against the other's limit. One test, because the limit is per day and every
    request of either person counts toward it, so the steps have to know how many went before.
    """

    def test_sessions_and_counters_are_their_own(self, oauth_live:'OAuthLiveEnvironment') -> 'None':

        url = oauth_live.limited_gateway_url

        maria = bearer_caller(url, _member_token())
        john = bearer_caller(url, _outsider_token())

        # Maria opens a session - her first request ..
        initialize_result = maria.initialize()
        assert initialize_result.response.status_code == OK, initialize_result.response.text
        session_id = initialize_result.session_id
        assert session_id

        # .. John presents her session and is turned away without being told whether it exists ..
        response = john.tools_list(session_id)
        assert response.status_code == BAD_REQUEST, f'Expected 400, got {response.status_code} -> {response.text}'

        response = john.delete(session_id)
        assert response.status_code == BAD_REQUEST, f'Expected 400, got {response.status_code} -> {response.text}'
        assert response.text == ''

        # .. the session is still hers - her second and third requests ..
        response = maria.tools_list(session_id)
        assert response.status_code == OK, response.text

        response = maria.tools_call(session_id, ModuleCtx.Echo_Service, {})
        assert response.status_code == OK, response.text

        # .. her next request is one over her daily limit ..
        response = maria.tools_call_stateless(ModuleCtx.Echo_Service, {})
        assert response.status_code == TOO_MANY_REQUESTS, f'Expected 429, got {response.status_code} -> {response.text}'
        assert response.headers[Header_Retry_After]

        # .. and John, who has made two requests of his own, is still within his.
        response = john.tools_call_stateless(ModuleCtx.Echo_Service, {})
        assert response.status_code == OK, response.text

# ################################################################################################################################
# ################################################################################################################################

class TestRejectedCallersAlert:
    """ The alert about rejected callers reads the same events the audit log shows and tells one person's
    refusals from another's.
    """

    def test_the_refusals_of_one_person_are_counted_apart_from_another_s(self, oauth_live:'OAuthLiveEnvironment') -> 'None':

        url = oauth_live.gateway_url
        min_id = last_event_id(oauth_live.audit_db_path, ModuleCtx.Gateway_Name)

        # John, outside the group, is refused twice ..
        john = bearer_caller(url, _outsider_token())

        for _ in range(2):
            response = john.tools_list_stateless()
            assert response.status_code == UNAUTHORIZED, response.text

        # .. and Maria, a member, once, with a token that has run out ..
        short_lived = keycloak_oauth.Client_Short_Lived_Login
        maria_token = keycloak_oauth.get_user_token(
            short_lived.client_id, short_lived.redirect_uri, keycloak_oauth.User_Member, keycloak_oauth.Password_Member)

        time.sleep(keycloak_oauth.Short_Login_Token_Lifespan + _expiry_wait_extra)

        response = bearer_caller(url, maria_token).tools_list_stateless()
        assert response.status_code == UNAUTHORIZED, response.text

        _ = wait_for_event_of_type(oauth_live.audit_db_path, ModuleCtx.Gateway_Name, min_id, AuditEvent.Auth_Failed)

        john_identity = expected_identity(ModuleCtx.Definition_Name, keycloak_oauth.User_Outsider)
        maria_identity = expected_identity(ModuleCtx.Definition_Name, keycloak_oauth.User_Member)

        engine = audit_engine(oauth_live)
        now = utcnow()

        # .. the rule's measure holds every refusal of the gateway in the window ..
        facts = collect_auth_failure_facts(
            engine, _alert_window_seconds, now, source=AuditSource.MCP, object_name=ModuleCtx.Gateway_Name)

        assert len(facts) == 1, facts
        fact:'anydict' = facts[0]
        assert fact['auth_failure_count'] >= 3, fact

        # .. the evidence behind the measure names each caller on their own rows ..
        rows = collect_failed_events(engine, fact, now)

        new_rows = []
        for row in rows:
            if row['id'] > min_id:
                new_rows.append(row)

        assert len(_rows_of_person(new_rows, john_identity)) == 2, new_rows
        assert len(_rows_of_person(new_rows, maria_identity)) == 1, new_rows

        # .. and the explanation groups them so that no group mixes the two people.
        groups = group_failures(new_rows, source=AuditSource.MCP)

        assert _count_of_person(groups, john_identity) == 2, groups
        assert _count_of_person(groups, maria_identity) == 1, groups

# ################################################################################################################################
# ################################################################################################################################
