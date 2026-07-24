# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# pytest
import pytest

# Zato
from zato.common.rule_engine.notify.credentials import credentials_status, Env_Secret_Key, load_credentials, \
    NotifyConfigError, save_credentials

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

_actor = 'sarah.p'

_slack_values = {'token': 'xoxb-test-token-0001'}

_teams_values = {
    'tenant_id':     'tenant-0001',
    'client_id':     'client-0001',
    'client_secret': 'client-secret-0001',
}

# ################################################################################################################################
# ################################################################################################################################

def test_slack_credentials_roundtrip(backend:'any_') -> 'None':
    """ Slack credentials decrypt back into the exact document that was saved.
    """
    save_credentials(backend, kind='slack', values=_slack_values, actor=_actor)

    loaded = load_credentials(backend, 'slack')
    assert loaded == _slack_values

# ################################################################################################################################

def test_teams_credentials_roundtrip(backend:'any_') -> 'None':
    """ Teams credentials decrypt back into the exact document that was saved.
    """
    save_credentials(backend, kind='teams', values=_teams_values, actor=_actor)

    loaded = load_credentials(backend, 'teams')
    assert loaded == _teams_values

# ################################################################################################################################

def test_credentials_are_encrypted_at_rest(backend:'any_') -> 'None':
    """ What lands in the database is ciphertext, never the token itself.
    """
    save_credentials(backend, kind='slack', values=_slack_values, actor=_actor)

    record = backend.notifications.get_chat_config('slack')
    assert record.payload.startswith('gAAA')
    assert _slack_values['token'] not in record.payload

# ################################################################################################################################

def test_saving_again_replaces_credentials(backend:'any_') -> 'None':
    """ Saving a platform a second time replaces its credentials in place.
    """
    save_credentials(backend, kind='slack', values=_slack_values, actor=_actor)

    replacement = {'token': 'xoxb-test-token-0002'}
    save_credentials(backend, kind='slack', values=replacement, actor='mike.r')

    loaded = load_credentials(backend, 'slack')
    assert loaded == replacement

    records = backend.notifications.list_chat_configs()
    assert len(records) == 1
    assert records[0].updated_by == 'mike.r'

# ################################################################################################################################

def test_unconfigured_platform_loads_as_none(backend:'any_') -> 'None':
    """ A platform without stored credentials is a valid state, not an error.
    """
    loaded = load_credentials(backend, 'teams')
    assert loaded is None

# ################################################################################################################################

def test_status_reports_both_platforms_teams_first(backend:'any_') -> 'None':
    """ The status covers every known platform in fixed order, secrets never included.
    """
    save_credentials(backend, kind='slack', values=_slack_values, actor=_actor)

    items = credentials_status(backend)
    assert len(items) == 2

    teams_row = items[0]
    assert teams_row['kind'] == 'teams'
    assert teams_row['is_configured'] is False
    assert teams_row['updated_by'] is None

    slack_row = items[1]
    assert slack_row['kind'] == 'slack'
    assert slack_row['is_configured'] is True
    assert slack_row['updated_by'] == _actor

    # No secret material anywhere in the status.
    assert _slack_values['token'] not in str(items)

# ################################################################################################################################

def test_missing_required_field_is_rejected(backend:'any_') -> 'None':
    """ Teams credentials without a client secret never reach the database.
    """
    incomplete = {'tenant_id': 'tenant-0001', 'client_id': 'client-0001'}

    with pytest.raises(NotifyConfigError) as info:
        save_credentials(backend, kind='teams', values=incomplete, actor=_actor)

    assert 'client_secret' in str(info.value)

# ################################################################################################################################

def test_unknown_kind_is_rejected(backend:'any_') -> 'None':
    """ Only the known chat platforms are accepted.
    """
    with pytest.raises(NotifyConfigError):
        save_credentials(backend, kind='irc', values={'token': 'irc-token'}, actor=_actor)

# ################################################################################################################################

def test_missing_secret_key_is_reported(backend:'any_') -> 'None':
    """ Without the environment key, saving credentials fails with a message naming the variable.
    """
    secret_key = os.environ.pop(Env_Secret_Key)

    try:
        with pytest.raises(NotifyConfigError) as info:
            save_credentials(backend, kind='slack', values=_slack_values, actor=_actor)

        assert Env_Secret_Key in str(info.value)

    # The other tests still need the key afterwards.
    finally:
        os.environ[Env_Secret_Key] = secret_key

# ################################################################################################################################
# ################################################################################################################################
