# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.rule_engine.notify.credentials import save_credentials
from zato.common.rule_engine.notify.delivery import list_targets, send_test_message, Test_Message
from zato.common.rule_engine.notify.loop import run_once
from zato.common.rule_engine.sql.constants import Event_Type_Advisory_Run

# Test helpers
from chat_simulators import find_free_port, SlackTestHandler, start_slack_server, start_teams_server, \
    TeamsGraphTestHandler
from jobs_test_data import add_version, Author, create_ruleset, create_suite, Rules_Text_Lower_Bar

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

_actor = 'sarah.p'
_channel = 'pricing-rules'

_slack_token = 'xoxb-test-' + CryptoManager.generate_hex_string()

_teams_tenant_id = 'tenant-' + CryptoManager.generate_hex_string()
_teams_client_id = 'client-' + CryptoManager.generate_hex_string()
_teams_client_secret = 'secret-' + CryptoManager.generate_hex_string()

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture()
def slack_address(backend:'any_') -> 'any_':
    """ A running simulated Slack workspace whose credentials are already saved in the backend.
    """
    port = find_free_port()
    server = start_slack_server(port, _slack_token, [_channel, 'general'])
    address = f'http://127.0.0.1:{port}'

    values = {'token': _slack_token, 'address': address}
    save_credentials(backend, kind='slack', values=values, actor=_actor)

    yield address

    server.shutdown()

# ################################################################################################################################

@pytest.fixture()
def teams_address(backend:'any_') -> 'any_':
    """ A running simulated Microsoft Graph whose credentials are already saved in the backend.
    """
    port = find_free_port()
    teams = [
        {
            'id': 'team-001',
            'displayName': 'Pricing',
            'channels': [
                {'id': 'channel-001', 'displayName': 'Rules'},
            ],
        },
    ]
    server = start_teams_server(port, _teams_tenant_id, _teams_client_id, _teams_client_secret, teams)
    address = f'https://127.0.0.1:{port}'

    values = {
        'tenant_id':       _teams_tenant_id,
        'client_id':       _teams_client_id,
        'client_secret':   _teams_client_secret,
        'address':         address,
        'auth_server_url': address,
        'verify_tls':      False,
    }
    save_credentials(backend, kind='teams', values=values, actor=_actor)

    yield address

    server.shutdown()

# ################################################################################################################################
# ################################################################################################################################

def test_publication_is_delivered_to_slack(backend:'any_', slack_address:'any_') -> 'None':
    """ A published version turns into exactly one Slack message and the cursor moves past it.
    """
    ruleset = create_ruleset(backend)
    destination = backend.notifications.add_destination(
        definition_id=ruleset.id,
        kind='slack',
        target=_channel,
        actor=_actor,
    )

    _ = backend.versions.publish(definition_id=ruleset.id, version=1, actor=Author)

    result = run_once(backend)
    assert result.messages_sent == 1
    assert result.delivery_failures == 0

    # The workspace received the message on the right channel ..
    assert len(SlackTestHandler.messages) == 1
    message = SlackTestHandler.messages[0]
    assert message['channel'] == _channel
    assert "'Loans' version 1 is live" in message['text']

    # .. the destination reports the delivery ..
    updated = backend.notifications.list_destinations(definition_id=ruleset.id)[0]
    assert updated.last_status == 'delivered'
    assert updated.cursor_id > destination.cursor_id

    # .. and the next pass has nothing left to send.
    repeated = run_once(backend)
    assert repeated.messages_sent == 0
    assert len(SlackTestHandler.messages) == 1

# ################################################################################################################################

def test_failed_delivery_is_retried_on_the_next_pass(backend:'any_', slack_address:'any_') -> 'None':
    """ A failure surfaces on the destination, keeps the cursor and the next pass retries.
    """
    ruleset = create_ruleset(backend)
    destination = backend.notifications.add_destination(
        definition_id=ruleset.id,
        kind='slack',
        target=_channel,
        actor=_actor,
    )

    _ = backend.versions.publish(definition_id=ruleset.id, version=1, actor=Author)

    # The workspace rejects the channel for now ..
    SlackTestHandler.broken_channels = [_channel]

    result = run_once(backend)
    assert result.messages_sent == 0
    assert result.delivery_failures == 1

    # .. which the destination reports without moving its cursor ..
    failed = backend.notifications.list_destinations(definition_id=ruleset.id)[0]
    assert failed.last_status == 'error'
    assert 'channel_not_found' in failed.last_error
    assert failed.cursor_id == destination.cursor_id

    # .. and once the channel works again, the retry delivers the same event.
    SlackTestHandler.broken_channels = []

    retried = run_once(backend)
    assert retried.messages_sent == 1

    delivered = backend.notifications.list_destinations(definition_id=ruleset.id)[0]
    assert delivered.last_status == 'delivered'
    assert delivered.last_error is None

# ################################################################################################################################

def test_missing_credentials_surface_on_the_destination(backend:'any_') -> 'None':
    """ Pending events with no matching credentials become a visible error, not a silent drop.
    """
    ruleset = create_ruleset(backend)
    _ = backend.notifications.add_destination(definition_id=ruleset.id, kind='slack', target=_channel, actor=_actor)

    _ = backend.versions.publish(definition_id=ruleset.id, version=1, actor=Author)

    result = run_once(backend)
    assert result.messages_sent == 0
    assert result.delivery_failures == 1

    failed = backend.notifications.list_destinations(definition_id=ruleset.id)[0]
    assert failed.last_status == 'error'
    assert failed.last_error == 'No slack credentials are configured'

# ################################################################################################################################

def test_failing_advisory_run_notifies(backend:'any_', slack_address:'any_') -> 'None':
    """ A new version runs its attached suites and a failing run turns into a message.
    """
    ruleset = create_ruleset(backend)
    _ = create_suite(backend, ruleset.id, expected_rate=1.5)

    # Drain the feed up to here so only the new version is pending.
    _ = run_once(backend)

    _ = backend.notifications.add_destination(definition_id=ruleset.id, kind='slack', target=_channel, actor=_actor)
    _ = add_version(backend, ruleset, Rules_Text_Lower_Bar)

    result = run_once(backend)
    assert result.advisory_runs == 1
    assert result.messages_sent == 1

    # The advisory run left its event in the ruleset's history ..
    events = backend.events.list(definition_id=ruleset.id)
    event_types = []
    for event in events:
        event_types.append(event.event_type)

    assert Event_Type_Advisory_Run in event_types

    # .. and its message names the failure.
    message = SlackTestHandler.messages[0]
    assert "1 of 1 scenarios fail against version 2 of 'Loans' (suite 'Loan suite')." in message['text']

# ################################################################################################################################

def test_passing_advisory_run_stays_quiet(backend:'any_', slack_address:'any_') -> 'None':
    """ A passing advisory run advances the cursor without producing any message.
    """
    ruleset = create_ruleset(backend)
    _ = create_suite(backend, ruleset.id, expected_rate=2.9)

    # Drain the feed up to here so only the new version is pending.
    _ = run_once(backend)

    destination = backend.notifications.add_destination(
        definition_id=ruleset.id,
        kind='slack',
        target=_channel,
        actor=_actor,
    )
    _ = add_version(backend, ruleset, Rules_Text_Lower_Bar)

    result = run_once(backend)
    assert result.advisory_runs == 1
    assert result.messages_sent == 0
    assert SlackTestHandler.messages == []

    # The quiet event still moved the cursor, without touching the delivery status.
    updated = backend.notifications.list_destinations(definition_id=ruleset.id)[0]
    assert updated.cursor_id > destination.cursor_id
    assert updated.last_status is None

# ################################################################################################################################

def test_publication_is_delivered_to_teams(backend:'any_', teams_address:'any_') -> 'None':
    """ A published version reaches a Teams channel addressed as 'Team name/Channel name'.
    """
    ruleset = create_ruleset(backend)
    _ = backend.notifications.add_destination(
        definition_id=ruleset.id,
        kind='teams',
        target='Pricing/Rules',
        actor=_actor,
    )

    _ = backend.versions.publish(definition_id=ruleset.id, version=1, actor=Author)

    result = run_once(backend)
    assert result.messages_sent == 1

    # The Graph received the message under the resolved team and channel.
    assert len(TeamsGraphTestHandler.messages) == 1
    message = TeamsGraphTestHandler.messages[0]
    assert message['team_id'] == 'team-001'
    assert message['channel_id'] == 'channel-001'
    assert "'Loans' version 1 is live" in message['payload']['body']['content']

# ################################################################################################################################

def test_slack_picker_lists_channels(backend:'any_', slack_address:'any_') -> 'None':
    """ The live picker names every channel the workspace offers.
    """
    items = list_targets(backend, 'slack')

    assert {'target': _channel, 'name': f'#{_channel}'} in items
    assert {'target': 'general', 'name': '#general'} in items

# ################################################################################################################################

def test_teams_picker_lists_team_channels(backend:'any_', teams_address:'any_') -> 'None':
    """ The live picker names every channel of every team, in the same form messages address them.
    """
    items = list_targets(backend, 'teams')

    assert items == [{'target': 'Pricing/Rules', 'name': 'Pricing/Rules'}]

# ################################################################################################################################

def test_the_settings_test_button_delivers(backend:'any_', slack_address:'any_') -> 'None':
    """ The settings screen's test message reaches the chosen channel.
    """
    send_test_message(backend, 'slack', 'general')

    assert len(SlackTestHandler.messages) == 1
    message = SlackTestHandler.messages[0]
    assert message['channel'] == 'general'
    assert message['text'] == Test_Message

# ################################################################################################################################
# ################################################################################################################################
