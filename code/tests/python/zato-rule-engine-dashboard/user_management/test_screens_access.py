# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from http.client import FORBIDDEN, FOUND, OK

# Django
from django.contrib.auth.models import User
from django.test import Client

# Zato
from zato.rule_engine_dashboard.app.bootstrap import Env_Admin_Password
from zato.rule_engine_dashboard.app.models import UserEvent
from zato.rule_engine_dashboard.app.user_rules import Root_Username

# ################################################################################################################################

from user_test_helpers import is_signed_in, new_account, signed_in_client

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

class TestSignIn:

    def test_admin_lands_on_the_users_list(self:'any_') -> 'None':
        user, password = new_account(is_admin=True)
        client = Client()

        response:'any_' = client.post('/login/', {'username': user.username, 'password': password, 'next': ''})

        assert response.status_code == FOUND
        assert response['Location'] == '/users/'
        assert is_signed_in(client)

# ################################################################################################################################

    def test_regular_user_lands_on_the_profile(self:'any_') -> 'None':
        user, password = new_account()
        client = Client()

        response:'any_' = client.post('/login/', {'username': user.username, 'password': password, 'next': ''})

        assert response.status_code == FOUND
        assert response['Location'] == '/profile/'
        assert is_signed_in(client)

# ################################################################################################################################

    def test_next_path_round_trip(self:'any_') -> 'None':
        user, password = new_account(is_admin=True)
        client = Client()

        response:'any_' = client.post('/login/', {'username': user.username, 'password': password, 'next': '/events/'})

        assert response.status_code == FOUND
        assert response['Location'] == '/events/'

# ################################################################################################################################

    def test_unsafe_next_path_goes_to_the_default_screen(self:'any_') -> 'None':
        user, password = new_account(is_admin=True)
        client = Client()

        response:'any_' = client.post(
            '/login/', {'username': user.username, 'password': password, 'next': 'https://example.com/elsewhere'})

        assert response.status_code == FOUND
        assert response['Location'] == '/users/'

# ################################################################################################################################

    def test_wrong_password_is_rejected(self:'any_') -> 'None':
        user, _ = new_account()
        client = Client()

        wrong_password = 'wrong-password-value'
        response:'any_' = client.post('/login/', {'username': user.username, 'password': wrong_password, 'next': ''})

        assert response.status_code == OK

        content = response.content.decode('utf8')
        assert 'Invalid username or password' in content

        assert not is_signed_in(client)

# ################################################################################################################################

    def test_disabled_user_cannot_sign_in(self:'any_') -> 'None':
        user, password = new_account(is_active=False)
        client = Client()

        response:'any_' = client.post('/login/', {'username': user.username, 'password': password, 'next': ''})

        assert response.status_code == OK
        assert not is_signed_in(client)

# ################################################################################################################################

    def test_root_signs_in_with_the_environment_password(self:'any_') -> 'None':
        client = Client()

        root_password = os.environ[Env_Admin_Password]
        response:'any_' = client.post('/login/', {'username': Root_Username, 'password': root_password, 'next': ''})

        assert response.status_code == FOUND
        assert is_signed_in(client)

# ################################################################################################################################

    def test_sign_out(self:'any_') -> 'None':
        user, _ = new_account()
        client = signed_in_client(user)

        response:'any_' = client.post('/logout/')

        assert response.status_code == FOUND
        assert response['Location'] == '/login/'
        assert not is_signed_in(client)

# ################################################################################################################################
# ################################################################################################################################

class TestAccessControl:

    def test_anonymous_goes_to_the_sign_in_screen(self:'any_') -> 'None':
        client = Client()

        for path in ['/users/', '/users/create', '/events/', '/profile/']:
            response:'any_' = client.get(path)

            assert response.status_code == FOUND
            assert response['Location'] == f'/login/?next={path}'

# ################################################################################################################################

    def test_regular_user_is_rejected_from_admin_screens(self:'any_') -> 'None':
        user, _ = new_account()
        other, _ = new_account()
        client = signed_in_client(user)

        paths = [
            '/users/',
            '/users/create',
            '/events/',
            f'/users/{other.username}/edit',
        ]

        for path in paths:
            response:'any_' = client.get(path)
            assert response.status_code == FORBIDDEN

# ################################################################################################################################

    def test_admin_reaches_admin_screens(self:'any_') -> 'None':
        user, _ = new_account(is_admin=True)
        client = signed_in_client(user)

        for path in ['/users/', '/users/create', '/events/', '/profile/']:
            response:'any_' = client.get(path)
            assert response.status_code == OK

# ################################################################################################################################
# ################################################################################################################################

class TestUsersListActions:

    def test_root_row_exposes_no_actions(self:'any_') -> 'None':
        user, _ = new_account(is_admin=True)
        client = signed_in_client(user)

        response:'any_' = client.get('/users/')
        content = response.content.decode('utf8')

        assert f'/users/{Root_Username}/edit' not in content
        assert f'/users/{Root_Username}/change-password' not in content
        assert f'/users/{Root_Username}/enable' not in content
        assert f'/users/{Root_Username}/disable' not in content
        assert f'/users/{Root_Username}/delete' not in content

# ################################################################################################################################

    def test_own_row_has_no_disable_or_delete(self:'any_') -> 'None':
        user, _ = new_account(is_admin=True)
        client = signed_in_client(user)

        response:'any_' = client.get('/users/')
        content = response.content.decode('utf8')

        # One's own profile and password stay editable ..
        assert f'/users/{user.username}/edit' in content
        assert f'/users/{user.username}/change-password' in content

        # .. while disabling or deleting oneself is not offered.
        assert f'/users/{user.username}/disable' not in content
        assert f'/users/{user.username}/delete' not in content

# ################################################################################################################################
# ################################################################################################################################

class TestProfile:

    def test_self_edit_updates_the_display_name(self:'any_') -> 'None':
        user, _ = new_account()
        client = signed_in_client(user)

        response:'any_' = client.post('/profile/', {'display_name': 'Updated Name'})

        assert response.status_code == FOUND
        assert response['Location'] == '/profile/'

        user.refresh_from_db()
        assert user.first_name == 'Updated'
        assert user.last_name == 'Name'

        # The change left its event, with the remote address of the test client
        event = UserEvent.objects.get(subject=user.username)
        assert event.actor == user.username
        assert event.action == 'user.update'
        assert event.remote_addr == '127.0.0.1'
        assert event.details == 'display_name=Updated Name'

# ################################################################################################################################

    def test_self_edit_without_changes_still_leaves_its_event(self:'any_') -> 'None':
        user, _ = new_account(display_name='Test User')
        client = signed_in_client(user)

        response:'any_' = client.post('/profile/', {'display_name': 'Test User'})

        assert response.status_code == FOUND

        # The action itself is on record even though the name stayed the same
        event = UserEvent.objects.get(subject=user.username)
        assert event.actor == user.username
        assert event.action == 'user.update'
        assert event.remote_addr == '127.0.0.1'
        assert event.details == 'no_changes=True'

# ################################################################################################################################

    def test_root_profile_is_immutable(self:'any_') -> 'None':
        root = User.objects.get(username=Root_Username)
        client = signed_in_client(root)

        response:'any_' = client.post('/profile/', {'display_name': 'Renamed Root'})

        assert response.status_code == FOUND

        root.refresh_from_db()
        assert root.first_name == ''
        assert root.last_name == ''

        # Nothing changed, so nothing was recorded either
        assert not UserEvent.objects.filter(subject=Root_Username).exists()

# ################################################################################################################################
# ################################################################################################################################
