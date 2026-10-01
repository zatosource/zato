# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time
from http.client import OK, UNAUTHORIZED
from json import loads
from typing import NamedTuple

# cryptography
from cryptography.hazmat.primitives.asymmetric import rsa

# PyJWT
import jwt as pyjwt

# requests
import requests

# SQLAlchemy
from sqlalchemy import create_engine

# Zato
from zato.common.audit_log.api import AuditEvent, AuditOutcome, AuditSource
from zato.common.audit_log.common import MCPAttr
from zato.common.audit_log.search import search_events
from zato.common.bearer_token_identity import Auth_Type_Bearer_JWT, Identity_Separator
from zato.common.model.security import BearerRefusalReason
from zato.common.util.mcp_oauth import build_challenge_header, get_metadata_url
from zato.common.util.time_ import utcnow

# Zato - test helpers
import keycloak_
import keycloak_oauth

# local
from _common import bearer_caller, last_event_id, MCPCaller, ModuleCtx, OAuthLiveEnvironment, tool_names, \
    wait_for_event_of_type

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, callable_, strlist, strnone

# ################################################################################################################################
# ################################################################################################################################

# How much longer than the token lifespan to wait before using a short-lived token, in seconds
_expiry_wait_extra = 1.5

# The key ID of a token signed by a key the realm never published
_unpublished_key_id = 'test-unpublished-key'

# How long a self-signed token is valid for, in seconds
_self_signed_lifespan = 300

# The arguments the echo tool is called with and the field of the result they come back in
_echo_arguments = {'invoice_id': 'INV-2026-0042'}

# ################################################################################################################################
# ################################################################################################################################

class ClientProfile(NamedTuple):
    """ What one MCP client product does when it connects - which client ID it presents and from which redirect URI,
    whether it names the resource it wants a token for, whether it registers itself, and the configuration a person
    writes to connect it. A product's behavior changing is a change to its profile and nothing else.
    """
    product: 'str'
    client_id: 'str'
    redirect_uri: 'str'
    sends_resource: 'bool'
    is_dynamic_registration: 'bool'
    is_json_config: 'bool'
    build_config: 'callable_'

# ################################################################################################################################
# ################################################################################################################################

def expected_challenge(oauth_live:'OAuthLiveEnvironment', url_path:'str', has_token:'bool') -> 'str':
    """ The challenge a gateway at the path answers with - naming the token as refused when one was sent.
    """
    out = build_challenge_header(get_metadata_url(oauth_live.server_address, url_path), has_token)
    return out

# ################################################################################################################################

def read_claims(token:'str') -> 'anydict':
    """ The claims of a token as the test issued it - the server does the verifying, the test reads them back.
    """
    out = pyjwt.decode(token, options={'verify_signature': False})
    return out

# ################################################################################################################################

def expected_identity(definition:'str', username:'str') -> 'str':
    out = f'{definition}{Identity_Separator}{username}'
    return out

# ################################################################################################################################

def build_unpublished_key_token() -> 'str':
    """ A token whose claims are all right and whose signing key the realm never published.
    """
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    now = int(time.time())

    claims = {
        'iss': keycloak_.get_issuer(),
        'aud': keycloak_.Audience_Main,
        'exp': now + _self_signed_lifespan,
        'iat': now,
        'azp': keycloak_oauth.Client_VSCode.client_id,
        keycloak_oauth.Claim_Username: keycloak_oauth.User_Member,
        keycloak_oauth.Claim_Groups: [keycloak_oauth.Group_Billing_Agents],
    }

    out = pyjwt.encode(claims, private_key, algorithm='RS256', headers={'kid': _unpublished_key_id})
    return out

# ################################################################################################################################

def audit_engine(oauth_live:'OAuthLiveEnvironment') -> 'any_':
    out = create_engine(f'sqlite:///{oauth_live.audit_db_path}')
    return out

# ################################################################################################################################
# ################################################################################################################################

class ClientSuite:
    """ The steps every client product runs against the gateway - the probe, the metadata, a full conversation
    of a group member with its audit record, and every refusal with its own. A module sets the profile.
    """
    profile: 'ClientProfile'

    # The client ID a product that registers itself received, filled on first use, one per product
    _dynamic_client_ids:'dict[str, str]' = {}

# ################################################################################################################################

    def _client_id(self) -> 'str':
        """ The client ID this product presents - its pre-registered one, or the one it registered itself.
        """
        profile = self.profile

        if not profile.is_dynamic_registration:
            return profile.client_id

        if profile.product not in self._dynamic_client_ids:
            client_id = keycloak_oauth.register_client(profile.product, [profile.redirect_uri])
            self._dynamic_client_ids[profile.product] = client_id

        out = self._dynamic_client_ids[profile.product]
        return out

# ################################################################################################################################

    def _token(self, oauth_live:'OAuthLiveEnvironment', username:'str', password:'str', client_id:'strnone'=None,
        redirect_uri:'strnone'=None) -> 'str':
        """ Signs the person in the way this product does and returns their access token.
        """
        profile = self.profile

        if client_id is None:
            client_id = self._client_id()

        if redirect_uri is None:
            redirect_uri = profile.redirect_uri

        resource = None
        if profile.sends_resource:
            resource = oauth_live.gateway_url

        out = keycloak_oauth.get_user_token(client_id, redirect_uri, username, password, resource=resource)
        return out

# ################################################################################################################################

    def _member_token(self, oauth_live:'OAuthLiveEnvironment') -> 'str':
        out = self._token(oauth_live, keycloak_oauth.User_Member, keycloak_oauth.Password_Member)
        return out

# ################################################################################################################################

    def _assert_refused(
        self,
        oauth_live:'OAuthLiveEnvironment',
        token:'str',
        reason:'str',
        claim:'str'='',
        has_identity:'bool'=True,
        ) -> 'anydict':
        """ Sends a request with the token, asserts the 401 with the challenge that names the token as refused and
        the auth-failed event with the reason, and returns the event. A refused token that could be read leaves the
        person and the client in the record, one that could not leaves neither.
        """
        min_id = last_event_id(oauth_live.audit_db_path, ModuleCtx.Gateway_Name)

        caller = bearer_caller(oauth_live.gateway_url, token)
        response = caller.tools_list_stateless()

        assert response.status_code == UNAUTHORIZED, f'Expected 401, got {response.status_code} -> {response.text}'

        challenge = response.headers[ModuleCtx.Challenge_Header]
        expected = expected_challenge(oauth_live, ModuleCtx.Gateway_Path, has_token=True)
        assert challenge == expected, f'Expected `{expected}`, got `{challenge}`'

        event = wait_for_event_of_type(oauth_live.audit_db_path, ModuleCtx.Gateway_Name, min_id, AuditEvent.Auth_Failed)
        auth = event['data']['auth']

        assert event['outcome'] == AuditOutcome.Error
        assert auth['type'] == Auth_Type_Bearer_JWT
        assert auth['definition'] == ModuleCtx.Definition_Name
        assert auth['reason'] == reason, f'Expected reason `{reason}`, got `{auth["reason"]}` in {auth}'
        assert auth['claim'] == claim, f'Expected claim `{claim}`, got `{auth["claim"]}` in {auth}'
        assert event['attrs'][MCPAttr.Reason] == reason

        if has_identity:
            claims = read_claims(token)
            assert auth['identity'] == claims[keycloak_oauth.Claim_Username]
            assert auth['client'] == claims['azp']
            assert event['ext_client_id'] == expected_identity(ModuleCtx.Definition_Name, auth['identity'])
            assert event['attrs'][MCPAttr.Identity] == auth['identity']
            assert event['attrs'][MCPAttr.Client] == auth['client']
        else:
            assert auth['identity'] == ''
            assert auth['client'] == ''
            assert MCPAttr.Identity not in event['attrs']
            assert MCPAttr.Client not in event['attrs']

        return event

# ################################################################################################################################

    def test_a_probe_without_a_token_is_told_where_the_metadata_is(self, oauth_live:'OAuthLiveEnvironment') -> 'None':

        caller = MCPCaller(oauth_live.gateway_url)
        response = caller.initialize().response

        assert response.status_code == UNAUTHORIZED, f'Expected 401, got {response.status_code} -> {response.text}'

        challenge = response.headers[ModuleCtx.Challenge_Header]
        expected = expected_challenge(oauth_live, ModuleCtx.Gateway_Path, has_token=False)
        assert challenge == expected, f'Expected `{expected}`, got `{challenge}`'

        # A probe that carried no token is not told that a token was refused
        assert 'invalid_token' not in challenge

# ################################################################################################################################

    def test_the_metadata_names_the_issuer_the_scopes_and_the_resource(self, oauth_live:'OAuthLiveEnvironment') -> 'None':

        metadata_url = get_metadata_url(oauth_live.server_address, ModuleCtx.Gateway_Path)
        response = requests.get(metadata_url, timeout=ModuleCtx.HTTP_Timeout)

        assert response.status_code == OK, f'Expected 200, got {response.status_code} -> {response.text}'

        document = response.json()

        assert document['resource'] == oauth_live.gateway_url
        assert document['authorization_servers'] == [keycloak_.get_issuer()]
        assert document['scopes_supported'] == ModuleCtx.Scopes.split()
        assert document['bearer_methods_supported'] == ['header']

        # A client may keep the document for a while before asking again
        assert 'max-age' in response.headers['Cache-Control']

        # The issuer the document names publishes the authorization server metadata the client reads next
        issuer_metadata = requests.get(
            keycloak_oauth.get_authorization_server_metadata_url(), timeout=ModuleCtx.HTTP_Timeout).json()
        assert issuer_metadata['issuer'] == document['authorization_servers'][0]
        assert issuer_metadata['code_challenge_methods_supported']

# ################################################################################################################################

    def test_a_member_runs_a_conversation_and_the_grant_is_recorded(self, oauth_live:'OAuthLiveEnvironment') -> 'None':

        token = self._member_token(oauth_live)
        claims = read_claims(token)
        caller = bearer_caller(oauth_live.gateway_url, token)

        min_id = last_event_id(oauth_live.audit_db_path, ModuleCtx.Gateway_Name)
        time_from = utcnow().isoformat()

        # The conversation of the revision with sessions ..
        initialize_result = caller.initialize()
        assert initialize_result.response.status_code == OK, initialize_result.response.text
        assert initialize_result.session_id

        session_id = initialize_result.session_id

        response = caller.tools_list(session_id)
        assert response.status_code == OK, response.text
        assert ModuleCtx.Echo_Service in tool_names(response)

        response = caller.tools_call(session_id, ModuleCtx.Echo_Service, _echo_arguments)
        assert response.status_code == OK, response.text

        result = response.json()['result']
        assert 'isError' not in result

        # .. and the self-contained one, which carries the same token the same way ..
        response = caller.tools_list_stateless()
        assert response.status_code == OK, response.text
        assert ModuleCtx.Echo_Service in tool_names(response)

        response = caller.tools_call_stateless(ModuleCtx.Echo_Service, _echo_arguments)
        assert response.status_code == OK, response.text

        time_to = utcnow().isoformat()

        # .. the record of the tool call says who called and through what ..
        event = wait_for_event_of_type(oauth_live.audit_db_path, ModuleCtx.Gateway_Name, min_id, AuditEvent.MCP_Tools_Call)

        identity = expected_identity(ModuleCtx.Definition_Name, keycloak_oauth.User_Member)

        assert event['outcome'] == AuditOutcome.OK
        assert event['endpoint'] == ModuleCtx.Echo_Service
        assert event['ext_client_id'] == identity
        assert event['sub_key'] == session_id
        assert time_from <= event['event_time_iso'] <= time_to, (time_from, event['event_time_iso'], time_to)

        data = event['data']
        assert data['remote_address'] == ModuleCtx.Remote_Address

        auth = data['auth']

        assert auth == {
            'type': Auth_Type_Bearer_JWT,
            'definition': ModuleCtx.Definition_Name,
            'identity': keycloak_oauth.User_Member,
            'issuer': keycloak_.get_issuer(),
            'audience': claims['aud'],
            'client': self._client_id(),
            'scopes': claims['scope'].split(),
            'token_id': claims['jti'],
            'expires_at': claims['exp'],
            'claims_matched': [f'{keycloak_oauth.Claim_Groups}={keycloak_oauth.Group_Billing_Agents}'],
        }, auth

        assert keycloak_.Audience_Main in auth['audience']

        # .. the fields the listing shows are attributes of the row as well ..
        assert event['attrs'][MCPAttr.Identity] == keycloak_oauth.User_Member
        assert event['attrs'][MCPAttr.Client] == self._client_id()
        assert MCPAttr.Reason not in event['attrs']

        # .. and the person's other requests of the conversation name them the same way.
        for other in (AuditEvent.MCP_Initialize, AuditEvent.MCP_Tools_List):
            other_event = wait_for_event_of_type(oauth_live.audit_db_path, ModuleCtx.Gateway_Name, min_id, other)
            assert other_event['ext_client_id'] == identity

# ################################################################################################################################

    def test_a_person_outside_the_group_is_refused(self, oauth_live:'OAuthLiveEnvironment') -> 'None':

        # A person in no group has no groups claim at all in their token
        token = self._token(oauth_live, keycloak_oauth.User_Outsider, keycloak_oauth.Password_Outsider)

        event = self._assert_refused(oauth_live, token, BearerRefusalReason.Claim_Missing, claim=keycloak_oauth.Claim_Groups)
        assert event['data']['auth']['identity'] == keycloak_oauth.User_Outsider

# ################################################################################################################################

    def test_an_expired_token_is_refused(self, oauth_live:'OAuthLiveEnvironment') -> 'None':

        # The lifespan of a token is a property of the client it was issued to, so this one comes from the
        # client whose tokens live for a second, signed in to the way this product does
        short_lived = keycloak_oauth.Client_Short_Lived_Login
        token = self._token(oauth_live, keycloak_oauth.User_Member, keycloak_oauth.Password_Member,
            client_id=short_lived.client_id, redirect_uri=short_lived.redirect_uri)

        time.sleep(keycloak_oauth.Short_Login_Token_Lifespan + _expiry_wait_extra)

        event = self._assert_refused(oauth_live, token, BearerRefusalReason.Expired)
        assert event['data']['auth']['identity'] == keycloak_oauth.User_Member

# ################################################################################################################################

    def test_a_token_for_another_audience_is_refused(self, oauth_live:'OAuthLiveEnvironment') -> 'None':

        token = keycloak_.get_token(keycloak_.Client_Wrong_Audience, keycloak_.Secret_Wrong_Audience)

        _ = self._assert_refused(oauth_live, token, BearerRefusalReason.Wrong_Audience)

# ################################################################################################################################

    def test_a_token_of_another_realm_is_refused(self, oauth_live:'OAuthLiveEnvironment') -> 'None':

        # The other realm signs with keys of its own, none of which the issuer's document names
        token = keycloak_.get_token(keycloak_.Client_Other_Realm, keycloak_.Secret_Other_Realm, realm=keycloak_.Realm_Other)

        _ = self._assert_refused(oauth_live, token, BearerRefusalReason.Unknown_Key)

# ################################################################################################################################

    def test_a_token_signed_by_an_unpublished_key_is_refused(self, oauth_live:'OAuthLiveEnvironment') -> 'None':

        token = build_unpublished_key_token()

        _ = self._assert_refused(oauth_live, token, BearerRefusalReason.Unknown_Key)

# ################################################################################################################################

    def test_a_malformed_token_is_refused(self, oauth_live:'OAuthLiveEnvironment') -> 'None':

        _ = self._assert_refused(oauth_live, 'not-a-token', BearerRefusalReason.Malformed, has_identity=False)

# ################################################################################################################################

    def test_search_finds_the_grant_and_the_refusal_by_person_and_by_client(self, oauth_live:'OAuthLiveEnvironment') -> 'None':

        min_id = last_event_id(oauth_live.audit_db_path, ModuleCtx.Gateway_Name)

        # One accepted call and one refused one ..
        member_token = self._member_token(oauth_live)
        response = bearer_caller(oauth_live.gateway_url, member_token).tools_call_stateless(ModuleCtx.Echo_Service, {})
        assert response.status_code == OK, response.text

        outsider_token = self._token(oauth_live, keycloak_oauth.User_Outsider, keycloak_oauth.Password_Outsider)
        response = bearer_caller(oauth_live.gateway_url, outsider_token).tools_list_stateless()
        assert response.status_code == UNAUTHORIZED, response.text

        grant = wait_for_event_of_type(oauth_live.audit_db_path, ModuleCtx.Gateway_Name, min_id, AuditEvent.MCP_Tools_Call)
        refusal = wait_for_event_of_type(oauth_live.audit_db_path, ModuleCtx.Gateway_Name, min_id, AuditEvent.Auth_Failed)

        engine = audit_engine(oauth_live)

        # .. the free-text search finds each by the person ..
        found_ids = _search_ids(engine, keycloak_oauth.User_Member)
        assert grant['id'] in found_ids, (grant['id'], found_ids)

        found_ids = _search_ids(engine, keycloak_oauth.User_Outsider)
        assert refusal['id'] in found_ids, (refusal['id'], found_ids)

        # .. and both by the client they signed in through.
        found_ids = _search_ids(engine, self._client_id())
        assert grant['id'] in found_ids, (grant['id'], found_ids)
        assert refusal['id'] in found_ids, (refusal['id'], found_ids)

# ################################################################################################################################

    def test_the_configuration_names_the_gateway_and_the_client(self, oauth_live:'OAuthLiveEnvironment') -> 'None':

        profile = self.profile
        client_id = self._client_id()

        config = profile.build_config(oauth_live.gateway_url, client_id)

        assert oauth_live.gateway_url in config
        assert client_id in config

        if profile.is_json_config:
            _ = loads(config)

# ################################################################################################################################
# ################################################################################################################################

def _search_ids(engine:'any_', query:'str') -> 'strlist':
    """ The IDs of the gateway's events the free-text search returns for a query - the same search the
    audit facade runs for a service.
    """
    events = search_events(engine, source=AuditSource.MCP, object_name=ModuleCtx.Gateway_Name, query=query)

    out = []
    for event in events:
        out.append(event['id'])

    return out

# ################################################################################################################################
# ################################################################################################################################
