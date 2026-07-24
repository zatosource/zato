# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from http.client import BAD_REQUEST, FORBIDDEN, NOT_FOUND, OK

# pytest
import pytest

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.rule_engine.notify.credentials import Env_Secret_Key, load_credentials

# The credentials endpoints need the encryption key before any request runs.
_secret_key = CryptoManager.generate_key()
os.environ[Env_Secret_Key] = _secret_key.decode('utf-8')

# Django
from django.contrib.auth.models import User
from django.test import Client

# Test helpers
from rule_views_client import post_json
from rule_views_test_data import create_ruleset

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

_slack_values = {'token': 'xoxb-test-token-0001'}

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture
def admin_client() -> 'any_':
    """ A test client signed in as the root admin.
    """
    admin_user = User.objects.get(username='admin')

    out = Client()
    out.force_login(admin_user)

    return out

# ################################################################################################################################
# ################################################################################################################################

def test_event_matrix_names_every_notified_event(client:'any_') -> 'None':
    """ The matrix endpoint pairs business names with internal codes for every notified event.
    """
    response = client.get('/rules/notifications/matrix/')
    assert response.status_code == OK

    items = response.json()['items']
    assert len(items) == 4

    codes = []
    for item in items:
        codes.append(item['code'])
        assert item['name']
        assert item['description']
        assert item['example']

    assert codes == ['version.published', 'version.restored', 'advisory.run', 'decisions.spiked']

# ################################################################################################################################

def test_admins_save_credentials_and_see_their_status(admin_client:'any_', backend:'any_') -> 'None':
    """ Saving credentials makes the platform configured, the status never echoes the token.
    """
    response = post_json(admin_client, '/rules/notifications/chat-config/save/',
        {'kind': 'slack', 'values': _slack_values})
    assert response.status_code == OK

    # The stored credentials decrypt back to what was sent ..
    loaded = load_credentials(backend, 'slack')
    assert loaded == _slack_values

    # .. and the status reports both platforms, Teams first, secrets never included.
    response = admin_client.get('/rules/notifications/chat-config/')
    assert response.status_code == OK

    items = response.json()['items']
    assert items[0]['kind'] == 'teams'
    assert items[0]['is_configured'] is False
    assert items[1]['kind'] == 'slack'
    assert items[1]['is_configured'] is True
    assert _slack_values['token'] not in str(items)

# ################################################################################################################################

def test_credentials_screens_are_admin_only(client:'any_') -> 'None':
    """ Regular users can neither read nor change chat credentials.
    """
    response = client.get('/rules/notifications/chat-config/')
    assert response.status_code == FORBIDDEN

    response = post_json(client, '/rules/notifications/chat-config/save/',
        {'kind': 'slack', 'values': _slack_values})
    assert response.status_code == FORBIDDEN

# ################################################################################################################################

def test_incomplete_credentials_are_rejected(admin_client:'any_') -> 'None':
    """ Credentials missing a required field never reach the database.
    """
    incomplete = {'tenant_id': 'tenant-0001', 'client_id': 'client-0001'}

    response = post_json(admin_client, '/rules/notifications/chat-config/save/',
        {'kind': 'teams', 'values': incomplete})
    assert response.status_code == BAD_REQUEST
    assert 'client_secret' in response.json()['error']

# ################################################################################################################################

def test_destinations_are_managed_per_ruleset(client:'any_', backend:'any_', username:'str') -> 'None':
    """ Destinations are added, listed with their delivery status and deleted through the views.
    """
    ruleset = create_ruleset(backend)

    # Add one destination ..
    response = post_json(client, f'/rules/rulesets/{ruleset.id}/destinations/add/',
        {'kind': 'slack', 'target': 'pricing-rules'})
    assert response.status_code == OK

    added = response.json()
    assert added['kind'] == 'slack'
    assert added['target'] == 'pricing-rules'
    assert added['created_by'] == username
    assert added['last_status'] is None

    # .. the list shows it with its delivery status fields ..
    response = client.get(f'/rules/rulesets/{ruleset.id}/destinations/')
    assert response.status_code == OK

    items = response.json()['items']
    assert len(items) == 1
    assert items[0]['id'] == added['id']
    assert items[0]['last_error'] is None
    assert items[0]['last_delivery_at'] is None

    # .. adding the same channel again is rejected ..
    response = post_json(client, f'/rules/rulesets/{ruleset.id}/destinations/add/',
        {'kind': 'slack', 'target': 'pricing-rules'})
    assert response.status_code == BAD_REQUEST

    # .. and deleting it empties the list.
    destination_id = added['id']
    response = post_json(client, f'/rules/notifications/destinations/{destination_id}/delete/', {})
    assert response.status_code == OK

    response = client.get(f'/rules/rulesets/{ruleset.id}/destinations/')
    assert response.json()['items'] == []

# ################################################################################################################################

def test_destination_for_unknown_ruleset_is_not_found(client:'any_') -> 'None':
    """ Adding a destination to a ruleset that does not exist reports the missing id.
    """
    response = post_json(client, '/rules/rulesets/123456/destinations/add/',
        {'kind': 'slack', 'target': 'pricing-rules'})
    assert response.status_code == NOT_FOUND

# ################################################################################################################################

def test_target_picker_without_credentials_is_a_readable_error(client:'any_') -> 'None':
    """ The picker names the missing credentials instead of failing silently.
    """
    response = client.get('/rules/notifications/targets/', {'kind': 'slack'})
    assert response.status_code == BAD_REQUEST
    assert response.json()['error'] == 'No slack credentials are configured'

# ################################################################################################################################
# ################################################################################################################################
