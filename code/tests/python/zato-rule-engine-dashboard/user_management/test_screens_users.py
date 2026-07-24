# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from http.client import FOUND, OK

# Django
from django.contrib.auth.models import User

# Zato
from zato.common.crypto.api import CryptoManager
from zato.rule_engine_dashboard.app.bootstrap import Env_Admin_Password
from zato.rule_engine_dashboard.app.models import UserAction, UserEvent
from zato.rule_engine_dashboard.app.user_rules import Root_Username

# ################################################################################################################################

from user_test_helpers import is_signed_in, new_account, signed_in_client

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

class TestUserCreate:

    def test_create_regular_user(self:'any_') -> 'None':
        admin, _ = new_account(is_admin=True)
        client = signed_in_client(admin)

        username = 'test.created.' + CryptoManager.generate_hex_string()
        password = 'password.' + CryptoManager.generate_hex_string()

        response:'any_' = client.post('/users/create', {
            'username': username,
            'display_name': 'New Person',
            'password': password,
        })

        assert response.status_code == FOUND
        assert response['Location'] == '/users/'

        user = User.objects.get(username=username)
        assert not user.is_superuser
        assert user.is_active
        assert user.first_name == 'New'
        assert user.last_name == 'Person'
        assert user.check_password(password)

        # The creation left its event and the details never carry the password
        event = UserEvent.objects.get(subject=username)
        assert event.actor == admin.username
        assert event.action == UserAction.Create
        assert event.remote_addr == '127.0.0.1'
        assert event.details == 'is_admin=False'
        assert password not in event.details

# ################################################################################################################################

    def test_create_admin_user(self:'any_') -> 'None':
        admin, _ = new_account(is_admin=True)
        client = signed_in_client(admin)

        username = 'test.created.' + CryptoManager.generate_hex_string()
        password = 'password.' + CryptoManager.generate_hex_string()

        response:'any_' = client.post('/users/create', {
            'username': username,
            'display_name': 'New Admin',
            'password': password,
            'is_admin': 'on',
        })

        assert response.status_code == FOUND

        user = User.objects.get(username=username)
        assert user.is_superuser

        event = UserEvent.objects.get(subject=username)
        assert event.details == 'is_admin=True'

# ################################################################################################################################

    def test_create_records_the_forwarded_remote_address(self:'any_') -> 'None':
        admin, _ = new_account(is_admin=True)
        client = signed_in_client(admin)

        username = 'test.created.' + CryptoManager.generate_hex_string()
        password = 'password.' + CryptoManager.generate_hex_string()

        _ = client.post(
            '/users/create',
            {'username': username, 'display_name': 'New Person', 'password': password},
            HTTP_X_FORWARDED_FOR='203.0.113.5',
        )

        event = UserEvent.objects.get(subject=username)
        assert event.remote_addr == '203.0.113.5'

# ################################################################################################################################

    def test_duplicate_username_is_rejected(self:'any_') -> 'None':
        admin, _ = new_account(is_admin=True)
        existing, _ = new_account()
        client = signed_in_client(admin)

        password = 'password.' + CryptoManager.generate_hex_string()
        response:'any_' = client.post('/users/create', {
            'username': existing.username,
            'display_name': 'Duplicate Person',
            'password': password,
        })

        # The form renders again with the message and no event was written
        assert response.status_code == OK

        content = response.content.decode('utf8')
        assert 'already exists' in content

        count = User.objects.filter(username=existing.username).count()
        assert count == 1

        assert not UserEvent.objects.filter(subject=existing.username).exists()

# ################################################################################################################################

    def test_root_username_cannot_be_created(self:'any_') -> 'None':
        admin, _ = new_account(is_admin=True)
        client = signed_in_client(admin)

        password = 'password.' + CryptoManager.generate_hex_string()
        response:'any_' = client.post('/users/create', {
            'username': Root_Username,
            'display_name': 'Second Root',
            'password': password,
        })

        assert response.status_code == OK

        content = response.content.decode('utf8')
        assert 'cannot be created' in content

        assert not UserEvent.objects.filter(subject=Root_Username).exists()

# ################################################################################################################################
# ################################################################################################################################

class TestUserEdit:

    def test_edit_display_name_role_and_status(self:'any_') -> 'None':
        admin, _ = new_account(is_admin=True)
        subject, _ = new_account()
        client = signed_in_client(admin)

        # The active checkbox stays unticked, which disables the account
        response:'any_' = client.post(f'/users/{subject.username}/edit', {
            'display_name': 'Promoted Person',
            'is_admin': 'on',
        })

        assert response.status_code == FOUND

        subject.refresh_from_db()
        assert subject.first_name == 'Promoted'
        assert subject.last_name == 'Person'
        assert subject.is_superuser
        assert not subject.is_active

        event = UserEvent.objects.get(subject=subject.username)
        assert event.actor == admin.username
        assert event.action == UserAction.Update
        assert event.remote_addr == '127.0.0.1'
        assert event.details == 'display_name=Promoted Person is_admin=True is_active=False'

# ################################################################################################################################

    def test_no_changes_still_leave_their_event(self:'any_') -> 'None':
        admin, _ = new_account(is_admin=True)
        subject, _ = new_account(display_name='Test User')
        client = signed_in_client(admin)

        response:'any_' = client.post(f'/users/{subject.username}/edit', {
            'display_name': 'Test User',
            'is_active': 'on',
        })

        assert response.status_code == FOUND

        # The action itself is on record even though no field changed
        event = UserEvent.objects.get(subject=subject.username)
        assert event.actor == admin.username
        assert event.action == UserAction.Update
        assert event.remote_addr == '127.0.0.1'
        assert event.details == 'no_changes=True'

# ################################################################################################################################

    def test_own_role_and_status_never_change_here(self:'any_') -> 'None':
        admin, _ = new_account(is_admin=True)
        client = signed_in_client(admin)

        # Neither checkbox is submitted, yet the account keeps its role and stays active
        response:'any_' = client.post(f'/users/{admin.username}/edit', {
            'display_name': 'Renamed Admin',
        })

        assert response.status_code == FOUND

        admin.refresh_from_db()
        assert admin.is_superuser
        assert admin.is_active
        assert admin.first_name == 'Renamed'

# ################################################################################################################################
# ################################################################################################################################

class TestEnableDisableDelete:

    def test_disable_and_enable(self:'any_') -> 'None':
        admin, _ = new_account(is_admin=True)
        subject, _ = new_account()
        client = signed_in_client(admin)

        response:'any_' = client.post(f'/users/{subject.username}/disable')
        assert response.status_code == FOUND

        subject.refresh_from_db()
        assert not subject.is_active

        response = client.post(f'/users/{subject.username}/enable')
        assert response.status_code == FOUND

        subject.refresh_from_db()
        assert subject.is_active

        # Both changes left their events, newest first
        events = UserEvent.objects.filter(subject=subject.username).order_by('id')

        disable_event = events[0]
        assert disable_event.action == UserAction.Disable
        assert disable_event.details == 'is_active=False'
        assert disable_event.remote_addr == '127.0.0.1'

        enable_event = events[1]
        assert enable_event.action == UserAction.Enable
        assert enable_event.details == 'is_active=True'

# ################################################################################################################################

    def test_delete(self:'any_') -> 'None':
        admin, _ = new_account(is_admin=True)
        subject, _ = new_account()
        client = signed_in_client(admin)

        response:'any_' = client.post(f'/users/{subject.username}/delete')
        assert response.status_code == FOUND

        assert not User.objects.filter(username=subject.username).exists()

        event = UserEvent.objects.get(subject=subject.username)
        assert event.action == UserAction.Delete
        assert event.details == 'is_admin=False is_active=True'
        assert event.remote_addr == '127.0.0.1'

# ################################################################################################################################

    def test_admin_cannot_disable_or_delete_itself(self:'any_') -> 'None':
        admin, _ = new_account(is_admin=True)
        client = signed_in_client(admin)

        _ = client.post(f'/users/{admin.username}/disable')
        _ = client.post(f'/users/{admin.username}/delete')

        admin.refresh_from_db()
        assert admin.is_active

        assert not UserEvent.objects.filter(subject=admin.username).exists()

# ################################################################################################################################

    def test_root_cannot_be_disabled_or_deleted(self:'any_') -> 'None':
        admin, _ = new_account(is_admin=True)
        client = signed_in_client(admin)

        _ = client.post(f'/users/{Root_Username}/disable')
        _ = client.post(f'/users/{Root_Username}/delete')

        root = User.objects.get(username=Root_Username)
        assert root.is_active

        assert not UserEvent.objects.filter(subject=Root_Username).exists()

# ################################################################################################################################
# ################################################################################################################################

class TestChangePassword:

    def test_admin_changes_another_password(self:'any_') -> 'None':
        admin, _ = new_account(is_admin=True)
        subject, _ = new_account()
        client = signed_in_client(admin)

        new_password = 'password.' + CryptoManager.generate_hex_string()

        response:'any_' = client.post(f'/users/{subject.username}/change-password', {
            'new_password': new_password,
            'confirm_password': new_password,
        })

        assert response.status_code == FOUND
        assert response['Location'] == '/users/'

        subject.refresh_from_db()
        assert subject.check_password(new_password)

        # The change left its event and the details never carry the password
        event = UserEvent.objects.get(subject=subject.username)
        assert event.actor == admin.username
        assert event.action == UserAction.Password_Change
        assert event.remote_addr == '127.0.0.1'
        assert event.details == ''

# ################################################################################################################################

    def test_self_change_keeps_the_session(self:'any_') -> 'None':
        user, _ = new_account()
        client = signed_in_client(user)

        new_password = 'password.' + CryptoManager.generate_hex_string()

        response:'any_' = client.post(f'/users/{user.username}/change-password', {
            'new_password': new_password,
            'confirm_password': new_password,
        })

        assert response.status_code == FOUND
        assert response['Location'] == '/profile/'

        user.refresh_from_db()
        assert user.check_password(new_password)

        # The session survived the change
        assert is_signed_in(client)

# ################################################################################################################################

    def test_mismatched_passwords_are_rejected(self:'any_') -> 'None':
        user, password = new_account()
        client = signed_in_client(user)

        response:'any_' = client.post(f'/users/{user.username}/change-password', {
            'new_password': 'password.first.' + CryptoManager.generate_hex_string(),
            'confirm_password': 'password.second.' + CryptoManager.generate_hex_string(),
        })

        assert response.status_code == FOUND

        user.refresh_from_db()
        assert user.check_password(password)

        assert not UserEvent.objects.filter(subject=user.username).exists()

# ################################################################################################################################

    def test_regular_user_cannot_change_another_password(self:'any_') -> 'None':
        user, _ = new_account()
        other, other_password = new_account()
        client = signed_in_client(user)

        new_password = 'password.' + CryptoManager.generate_hex_string()

        response:'any_' = client.post(f'/users/{other.username}/change-password', {
            'new_password': new_password,
            'confirm_password': new_password,
        })

        assert response.status_code == FOUND
        assert response['Location'] == '/profile/'

        other.refresh_from_db()
        assert other.check_password(other_password)

        assert not UserEvent.objects.filter(subject=other.username).exists()

# ################################################################################################################################

    def test_root_password_cannot_be_changed(self:'any_') -> 'None':
        admin, _ = new_account(is_admin=True)
        client = signed_in_client(admin)

        new_password = 'password.' + CryptoManager.generate_hex_string()

        response:'any_' = client.post(f'/users/{Root_Username}/change-password', {
            'new_password': new_password,
            'confirm_password': new_password,
        })

        assert response.status_code == FOUND

        root = User.objects.get(username=Root_Username)
        assert root.check_password(os.environ[Env_Admin_Password])

        assert not UserEvent.objects.filter(subject=Root_Username).exists()

# ################################################################################################################################
# ################################################################################################################################
