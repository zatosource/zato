# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import FOUND, OK
from urllib.parse import urlsplit

# Django
from django.contrib.auth.models import User
from django.test import Client

# requests
import requests

# ################################################################################################################################

from entra_test_config import TestConfig
from user_test_helpers import is_signed_in

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

class TestEntraSignIn:

    def test_login_page_offers_both_paths(self:'any_') -> 'None':
        client = Client()

        response:'any_' = client.get('/login/')
        assert response.status_code == OK

        content = response.content.decode('utf8')

        # Both sign-in paths are visible - the Microsoft button and the built-in form.
        assert 'Sign in with Microsoft' in content
        assert 'id_username' in content

# ################################################################################################################################

    def test_callback_provisions_a_superuser(self:'any_', entra_server:'any_') -> 'None':
        client = Client()

        # The Microsoft button sends the browser to the identity provider ..
        response:'any_' = client.get('/login/', {'auth': 'entra', 'next': '/users/'})
        assert response.status_code == FOUND

        auth_uri = response['Location']
        assert auth_uri.startswith(entra_server.address)

        # .. which redirects back to this application's callback ..
        provider_response = requests.get(auth_uri, allow_redirects=False)
        assert provider_response.status_code == FOUND

        callback_url = provider_response.headers['Location']
        assert callback_url.startswith('http://testserver/login/callback/')

        # .. and the callback signs the person in and sends them where they were going.
        split = urlsplit(callback_url)
        path_with_query = f'{split.path}?{split.query}'

        response = client.get(path_with_query)
        assert response.status_code == FOUND
        assert response['Location'] == '/users/'

        assert is_signed_in(client)

        # The user was provisioned in this application's own database as a superuser
        # and external accounts never keep a local password.
        user = User.objects.get(username=TestConfig.user_principal_name)
        assert user.is_superuser
        assert not user.has_usable_password()
        assert user.first_name == 'Test'
        assert user.last_name == 'User'

# ################################################################################################################################
# ################################################################################################################################
