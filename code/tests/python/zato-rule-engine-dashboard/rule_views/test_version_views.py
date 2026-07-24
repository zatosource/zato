# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import OK

# ################################################################################################################################

from rule_views_client import post_json
from rule_views_test_data import Author, create_ruleset, parse_documents, Rules_Text_Lower_Bar

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

def _add_lower_bar_version(backend:'any_', definition_id:'int') -> 'None':
    """ Stores the lower-bar rules as version two.
    """
    documents = parse_documents(Rules_Text_Lower_Bar)

    _ = backend.versions.create(
        definition_id=definition_id,
        expected_current_version=1,
        document={'documents': documents},
        author=Author,
        comment='Lower the bar',
    )

# ################################################################################################################################

def test_timeline_carries_the_history(client:'any_', backend:'any_') -> 'None':
    """ The timeline answers with the definition and its events, newest first.
    """
    definition = create_ruleset(backend)
    _add_lower_bar_version(backend, definition.id)

    response:'any_' = client.get(f'/rules/rulesets/{definition.id}/timeline/')
    assert response.status_code == OK

    data = response.json()
    assert data['definition']['current_version'] == 2

    event_types = []
    for event in data['events']:
        event_types.append(event['event_type'])

    assert 'definition.created' in event_types
    assert 'version.created' in event_types

# ################################################################################################################################

def test_version_is_served_with_its_rendered_form(client:'any_', backend:'any_') -> 'None':
    """ One snapshot comes back with its document and the readable text it renders into.
    """
    definition = create_ruleset(backend)

    response:'any_' = client.get(f'/rules/rulesets/{definition.id}/versions/1/')
    assert response.status_code == OK

    data = response.json()
    assert data['version'] == 1
    assert data['comment'] == 'Create the ruleset'
    assert 'credit_score is at least 700' in data['rendered']

# ################################################################################################################################

def test_diff_names_what_changed(client:'any_', backend:'any_') -> 'None':
    """ The structural diff puts the changed rule into the updated bucket with its changed blocks named.
    """
    definition = create_ruleset(backend)
    _add_lower_bar_version(backend, definition.id)

    response:'any_' = client.get(f'/rules/rulesets/{definition.id}/diff/', {'old': 1, 'new': 2})
    assert response.status_code == OK

    data = response.json()
    assert len(data['updated']) == 1

    updated = data['updated'][0]
    assert 'when' in updated['changed']

# ################################################################################################################################

def test_rollback_restores_and_publishes(client:'any_', backend:'any_') -> 'None':
    """ A rollback copies the source snapshot into a new linear version and makes it live at once.
    """
    definition = create_ruleset(backend)
    _add_lower_bar_version(backend, definition.id)

    body = {'source_version': 1, 'expected_current_version': 2, 'comment': 'Back to the strict bar'}
    response = post_json(client, f'/rules/rulesets/{definition.id}/rollback/', body)
    assert response.status_code == OK
    assert response.json()['version'] == 3

    restored = backend.definitions.get(definition.id)
    assert restored.current_version == 3
    assert restored.live_version == 3

    # The restored document is the strict one again.
    response:'any_' = client.get(f'/rules/rulesets/{definition.id}/versions/3/')
    assert 'credit_score is at least 700' in response.json()['rendered']

# ################################################################################################################################

def test_compare_outcomes_names_the_decisions_that_change(client:'any_', backend:'any_') -> 'None':
    """ The outcome diff reports which scenarios decide differently between two versions and why.
    """
    definition = create_ruleset(backend)
    _add_lower_bar_version(backend, definition.id)

    scenarios = [
        {'name': 'Middling score', 'input': {'credit_score': 660}},
        {'name': 'High score', 'input': {'credit_score': 720}},
    ]
    body = {'old_version': 1, 'new_version': 2, 'scenarios': scenarios}

    response = post_json(client, f'/rules/rulesets/{definition.id}/compare-outcomes/', body)
    assert response.status_code == OK

    data = response.json()
    assert data['total'] == 2
    assert data['changed'] == 1
    assert data['unchanged'] == 1

# ################################################################################################################################
# ################################################################################################################################
