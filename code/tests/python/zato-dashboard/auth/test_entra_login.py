# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import FOUND, OK
from urllib.parse import parse_qsl, urlsplit

# Django
from django.contrib.auth.models import User
from django.test import Client

# requests
import requests

# Zato
from zato.common.webapp.auth.config import auth_config
from zato.common.crypto.api import CryptoManager

# ################################################################################################################################

from entra_test_config import TestConfig
from entra_test_server import AuthorizeErrorMode, TokenErrorMode

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strdict

# ################################################################################################################################
# ################################################################################################################################

def _go_to_microsoft(client:'Client', query_params:'strdict') -> 'str':
    """ Opens the login page in a way that sends the browser to Microsoft and returns the authorize URL.
    """
    response:'any_' = client.get('/accounts/login/', query_params)
    assert response.status_code == FOUND

    out = response['Location']
    return out

# ################################################################################################################################

def _visit_authorize(auth_uri:'str') -> 'str':
    """ Visits the Microsoft authorize URL the way a browser would and returns the callback URL
    the identity provider redirects back to.
    """
    response = requests.get(auth_uri, allow_redirects=False)
    assert response.status_code == FOUND

    out = response.headers['Location']
    return out

# ################################################################################################################################

def _return_to_dashboard(client:'Client', callback_url:'str') -> 'any_':
    """ Follows the identity provider's redirect back into the dashboard's callback view.
    """
    assert callback_url.startswith(TestConfig.redirect_url)

    split = urlsplit(callback_url)
    path_with_query = f'{split.path}?{split.query}'

    out:'any_' = client.get(path_with_query)
    return out

# ################################################################################################################################

def _sign_in(client:'Client', query_params:'strdict') -> 'any_':
    """ Runs the whole sign-in round trip - dashboard to Microsoft to dashboard.
    """
    auth_uri = _go_to_microsoft(client, query_params)
    callback_url = _visit_authorize(auth_uri)

    out = _return_to_dashboard(client, callback_url)
    return out

# ################################################################################################################################

def _is_logged_in(client:'Client') -> 'bool':
    out = '_auth_user_id' in client.session
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestLoginPage:

    def test_microsoft_button_is_shown_above_the_form(self:'any_') -> 'None':
        client = Client()

        response:'any_' = client.get('/accounts/login/')
        assert response.status_code == OK

        content = response.content.decode('utf8')

        # Both sign-in paths are visible - the Microsoft button and the built-in form.
        assert 'Sign in with Microsoft' in content
        assert 'id_username' in content

# ################################################################################################################################

    def test_auto_login_redirects_to_microsoft(self:'any_', monkeypatch:'any_', entra_server:'any_') -> 'None':
        monkeypatch.setattr(auth_config, 'auto_login', True)
        client = Client()

        response:'any_' = client.get('/accounts/login/')
        assert response.status_code == FOUND
        assert response['Location'].startswith(entra_server.address)

# ################################################################################################################################

    def test_built_in_escape_hatch_with_auto_login(self:'any_', monkeypatch:'any_') -> 'None':
        monkeypatch.setattr(auth_config, 'auto_login', True)
        client = Client()

        # Even with auto-login on, the plain form stays reachable for local accounts.
        response:'any_' = client.get('/accounts/login/', {'auth': 'built-in'})
        assert response.status_code == OK

        content = response.content.decode('utf8')
        assert 'id_username' in content

# ################################################################################################################################
# ################################################################################################################################

class TestSignInFlow:

    def test_full_sign_in_flow(self:'any_', entra_server:'any_') -> 'None':
        client = Client()

        response = _sign_in(client, {'auth': 'entra', 'next': '/zato/'})

        # The person lands where they were going ..
        assert response.status_code == FOUND
        assert response['Location'] == '/zato/'

        # .. the session is authenticated ..
        assert _is_logged_in(client)

        # .. the Django user was provisioned without a usable password ..
        user = User.objects.get(username=TestConfig.user_principal_name)
        assert not user.has_usable_password()
        assert user.first_name == 'Test'
        assert user.last_name == 'User'

        # .. the account has admin rights ..
        assert user.is_superuser
        assert user.is_staff

        # .. and the code exchange was a real PKCE-protected one.
        token_requests = []
        for request in entra_server.recorded_requests:
            if request['path'].endswith('/oauth2/v2.0/token'):
                token_requests.append(request)

        token_request = token_requests[0]
        assert token_request['form']['grant_type'] == 'authorization_code'
        assert 'code_verifier' in token_request['form']

# ################################################################################################################################

    def test_next_path_round_trip(self:'any_') -> 'None':
        client = Client()

        response = _sign_in(client, {'auth': 'entra', 'next': '/zato/service/'})
        assert response.status_code == FOUND
        assert response['Location'] == '/zato/service/'

# ################################################################################################################################

    def test_unsafe_next_path_redirects_to_the_main_page(self:'any_') -> 'None':
        client = Client()

        response = _sign_in(client, {'auth': 'entra', 'next': 'https://example.com/elsewhere'})
        assert response.status_code == FOUND
        assert response['Location'] == '/'

# ################################################################################################################################
# ################################################################################################################################

class TestSignInErrors:

    def _assert_error_page(self:'any_', response:'any_', client:'Client', expected_text:'str') -> 'None':

        # The login page renders again with the error explained ..
        assert response.status_code == OK

        content = response.content.decode('utf8')
        assert expected_text in content

        # .. and no session was started.
        assert not _is_logged_in(client)

# ################################################################################################################################

    def test_silent_sign_in_not_possible(self:'any_', entra_server:'any_') -> 'None':
        entra_server.set_authorize_error(AuthorizeErrorMode.Login_Required)
        client = Client()

        response = _sign_in(client, {'auth': 'entra', 'next': '/zato/'})
        self._assert_error_page(response, client, 'AADSTS50058')

# ################################################################################################################################

    def test_expired_code(self:'any_', entra_server:'any_') -> 'None':
        entra_server.set_token_error(TokenErrorMode.Expired_Code)
        client = Client()

        response = _sign_in(client, {'auth': 'entra', 'next': '/zato/'})
        self._assert_error_page(response, client, 'AADSTS70008')

# ################################################################################################################################

    def test_bad_signature(self:'any_', entra_server:'any_') -> 'None':
        entra_server.set_token_error(TokenErrorMode.Bad_Signature)
        client = Client()

        response = _sign_in(client, {'auth': 'entra', 'next': '/zato/'})
        self._assert_error_page(response, client, 'ID token validation error')

# ################################################################################################################################

    def test_wrong_audience(self:'any_', entra_server:'any_') -> 'None':
        entra_server.set_token_error(TokenErrorMode.Wrong_Audience)
        client = Client()

        response = _sign_in(client, {'auth': 'entra', 'next': '/zato/'})
        self._assert_error_page(response, client, 'Sign-in error')

# ################################################################################################################################

    def test_missing_groups_claim(self:'any_', entra_server:'any_') -> 'None':
        entra_server.set_token_error(TokenErrorMode.Missing_Groups)
        client = Client()

        response = _sign_in(client, {'auth': 'entra', 'next': '/zato/'})
        self._assert_error_page(response, client, 'No groups claim')

# ################################################################################################################################

    def test_user_not_in_any_allowed_group(self:'any_', entra_server:'any_') -> 'None':
        unrelated_group = '5a4b3c2d-1e0f-4a5b-8c7d-6e5f4a3b2c1d'
        entra_server.set_user(
            TestConfig.user_principal_name, TestConfig.user_display_name, [unrelated_group])

        client = Client()

        response = _sign_in(client, {'auth': 'entra', 'next': '/zato/'})
        self._assert_error_page(response, client, 'not a member of any allowed group')

# ################################################################################################################################

    def test_tampered_state(self:'any_') -> 'None':
        client = Client()

        # The flow starts normally ..
        auth_uri = _go_to_microsoft(client, {'auth': 'entra', 'next': '/zato/'})
        callback_url = _visit_authorize(auth_uri)

        # .. but the state in the callback does not match the one the flow started with.
        split = urlsplit(callback_url)
        params = dict(parse_qsl(split.query))
        params['state'] = 'tampered-state-' + CryptoManager.generate_hex_string()

        response:'any_' = client.get(split.path, params)
        self._assert_error_page(response, client, 'Sign-in error')

# ################################################################################################################################

    def test_callback_without_a_pending_flow(self:'any_') -> 'None':
        client = Client()

        # The callback arrives without any sign-in having started in this session.
        params = {
            'code': 'code-' + CryptoManager.generate_hex_string(),
            'state': 'state-' + CryptoManager.generate_hex_string(),
        }

        response:'any_' = client.get('/accounts/login/callback/', params)
        self._assert_error_page(response, client, 'No sign-in attempt is in progress')

# ################################################################################################################################
# ################################################################################################################################
