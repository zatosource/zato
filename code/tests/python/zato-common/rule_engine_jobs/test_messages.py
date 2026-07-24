# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# Zato
from zato.common.rule_engine.notify.messages import build_message, Env_Dashboard_Base_URL
from zato.common.rule_engine.sql.constants import Event_Type_Decisions_Spiked, Event_Type_Version_Published, \
    Event_Type_Version_Restored, System_Actor

# Test helpers
from jobs_test_data import add_version, Author, create_ruleset, Rules_Text_Lower_Bar

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

def _newest_event_of_type(backend:'any_', definition_id:'int', event_type:'str') -> 'any_':
    """ Returns the newest feed event of one type.
    """
    events = backend.events.list(definition_id=definition_id)

    for event in events:
        if event.event_type == event_type:
            out = event
            break
    else:
        raise Exception(f'No event of type {event_type} for definition {definition_id}')

    return out

# ################################################################################################################################
# ################################################################################################################################

def test_publish_message_carries_the_change_summary(backend:'any_') -> 'None':
    """ A publication message names the ruleset, the version, the actor and what changed.
    """
    ruleset = create_ruleset(backend)
    _ = add_version(backend, ruleset, Rules_Text_Lower_Bar)
    _ = backend.versions.publish(definition_id=ruleset.id, version=2, actor=Author)

    event = _newest_event_of_type(backend, ruleset.id, Event_Type_Version_Published)
    message = build_message(backend, event)

    assert "'Loans' version 2 is live" in message
    assert Author in message
    assert '1 rule updated (loans_Preferential_rate)' in message

# ################################################################################################################################

def test_first_publication_has_no_change_summary(backend:'any_') -> 'None':
    """ Version one has no predecessor, so its message carries no diff.
    """
    ruleset = create_ruleset(backend)
    _ = backend.versions.publish(definition_id=ruleset.id, version=1, actor=Author)

    event = _newest_event_of_type(backend, ruleset.id, Event_Type_Version_Published)
    message = build_message(backend, event)

    assert message == f"'Loans' version 1 is live, published by {Author}."

# ################################################################################################################################

def test_rollback_message_names_both_versions(backend:'any_') -> 'None':
    """ A rollback message names the restored version and the new live one.
    """
    ruleset = create_ruleset(backend)
    _ = add_version(backend, ruleset, Rules_Text_Lower_Bar)
    _ = backend.versions.restore(
        definition_id=ruleset.id,
        source_version=1,
        expected_current_version=2,
        actor=Author,
        comment='Back to the higher bar',
    )

    event = _newest_event_of_type(backend, ruleset.id, Event_Type_Version_Restored)
    message = build_message(backend, event)

    assert message == f"'Loans' was rolled back to version 1 by {Author}, now live as version 3."

# ################################################################################################################################

def test_spike_message_reports_both_counts(backend:'any_') -> 'None':
    """ A spike message reads with thousands separators for both the spike and the typical rate.
    """
    ruleset = create_ruleset(backend)

    payload = {'hour': '2026-07-20T10', 'count': 4200, 'typical': 300}
    _ = backend.events.append(
        definition_id=ruleset.id,
        version=None,
        event_type=Event_Type_Decisions_Spiked,
        actor=System_Actor,
        payload=payload,
    )

    event = _newest_event_of_type(backend, ruleset.id, Event_Type_Decisions_Spiked)
    message = build_message(backend, event)

    assert message == "'Loans' decided 4,200 times in the last hour against a typical 300."

# ################################################################################################################################

def test_deep_link_is_appended_when_the_base_url_is_known(backend:'any_') -> 'None':
    """ With the dashboard's address in the environment, every message ends with a deep link.
    """
    ruleset = create_ruleset(backend)
    _ = backend.versions.publish(definition_id=ruleset.id, version=1, actor=Author)

    event = _newest_event_of_type(backend, ruleset.id, Event_Type_Version_Published)

    os.environ[Env_Dashboard_Base_URL] = 'https://rules.example.com/'

    try:
        message = build_message(backend, event)
    finally:
        del os.environ[Env_Dashboard_Base_URL]

    assert message.endswith(f' https://rules.example.com/rules/rulesets/{ruleset.id}/')

# ################################################################################################################################
# ################################################################################################################################
