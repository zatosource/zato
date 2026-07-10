# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import FOUND, OK

# Django
from django.contrib.auth.models import User
from django.test import Client

# Zato
from zato.common.crypto.api import CryptoManager

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

class TestBuiltInCoexistence:
    """ With Entra ID enabled, accounts created with 'zato create user' keep working through the form.
    """

    def _create_built_in_user(self:'any_') -> 'tuple[str, str]':
        username = 'test.builtin.' + CryptoManager.generate_hex_string()
        password = 'password.' + CryptoManager.generate_hex_string()

        _ = User.objects.create_user(username=username, password=password)

        out = (username, password)
        return out

# ################################################################################################################################

    def test_built_in_account_logs_in_through_the_form(self:'any_') -> 'None':
        username, password = self._create_built_in_user()
        client = Client()

        response:'any_' = client.post('/accounts/login/', {
            'username': username,
            'password': password,
            'next': '/zato/',
        })

        assert response.status_code == FOUND
        assert response['Location'] == '/zato/'
        assert '_auth_user_id' in client.session

# ################################################################################################################################

    def test_invalid_built_in_credentials_are_rejected(self:'any_') -> 'None':
        username, _ = self._create_built_in_user()
        wrong_password = 'password.' + CryptoManager.generate_hex_string()

        client = Client()

        response:'any_' = client.post('/accounts/login/', {
            'username': username,
            'password': wrong_password,
            'next': '/zato/',
        })

        assert response.status_code == OK

        content = response.content.decode('utf8')
        assert 'Invalid credentials' in content
        assert '_auth_user_id' not in client.session

# ################################################################################################################################

    def test_form_is_rendered_alongside_the_microsoft_button(self:'any_') -> 'None':
        client = Client()

        response:'any_' = client.get('/accounts/login/')
        assert response.status_code == OK

        content = response.content.decode('utf8')

        # Both paths are on the same page.
        assert 'id_username' in content
        assert 'id_password' in content
        assert 'Sign in with Microsoft' in content

# ################################################################################################################################
# ################################################################################################################################
