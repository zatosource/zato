# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import BAD_REQUEST, OK

# Zato
from zato.common.rule_engine.sql import CapturePolicy
from zato.common.rule_engine.sql.data import DecisionWrite
from zato.common.rule_engine.sql.time_ import utc_now

# ################################################################################################################################

from rule_views_client import post_json
from rule_views_test_data import create_ruleset

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

def _new_decision(
    definition_id:'int',
    decision_id:'str',
    business_key:'str',
    outcome:'str',
    is_error:'bool',
    ) -> 'DecisionWrite':
    """ One complete decision over the shared ruleset's first version.
    """
    story = {
        'input': {'credit_score': 720},
        'outputs': {'rate': 2.9, 'approved': True},
        'statements': [{'rule': 'loans_Preferential_rate', 'statement': 'Better rates for our best customers.',
            'severity': 'info'}],
        'error': '',
    }

    out = DecisionWrite(
        decision_id=decision_id,
        ruleset_id=definition_id,
        rules_version=1,
        occurred_at=utc_now(),
        business_key=business_key,
        outcome=outcome,
        is_error=is_error,
        duration_ms=5,
        story=story,
        fired_rule_ids=['loans_Preferential_rate'],
    )

    return out

# ################################################################################################################################

def _arrange_decisions(backend:'any_') -> 'int':
    """ Stores one matched and one errored decision, returning the ruleset's id.
    """
    definition = create_ruleset(backend)

    decisions = [
        _new_decision(definition.id, 'decision-matched-1', 'customer-123', 'matched', False),
        _new_decision(definition.id, 'decision-error-1', 'customer-456', 'error', True),
    ]
    policy = CapturePolicy(store_fired_rule_ids=True)
    _ = backend.decisions.insert_batch(decisions, policy)

    return definition.id

# ################################################################################################################################

def test_log_lists_and_filters_by_business_key(client:'any_', backend:'any_') -> 'None':
    """ The log answers newest first and narrows by the promoted business key.
    """
    ruleset_id = _arrange_decisions(backend)

    response:'any_' = client.get('/rules/decisions/', {'ruleset_id': ruleset_id})
    assert response.status_code == OK
    assert len(response.json()['items']) == 2

    response:'any_' = client.get('/rules/decisions/', {'business_key': 'customer-123'})
    items = response.json()['items']
    assert len(items) == 1
    assert items[0]['decision_id'] == 'decision-matched-1'
    assert items[0]['story']['input'] == {'credit_score': 720}

# ################################################################################################################################

def test_detail_joins_the_exact_version(client:'any_', backend:'any_') -> 'None':
    """ One decision comes back joined to the very version of the rules that made it.
    """
    _ = _arrange_decisions(backend)

    response:'any_' = client.get('/rules/decisions/decision-matched-1/')
    assert response.status_code == OK

    data = response.json()
    assert data['decision']['outcome'] == 'matched'
    assert data['decision']['fired_rule_ids'] == ['loans_Preferential_rate']

    version = data['version']
    assert version['version'] == 1
    assert 'credit_score is at least 700' in version['rendered']

# ################################################################################################################################

def test_aggregates_come_with_drill_down_keys(client:'any_', backend:'any_') -> 'None':
    """ Outcome, version and hourly counts share one filter, the average duration rides along.
    """
    ruleset_id = _arrange_decisions(backend)

    response:'any_' = client.get('/rules/decisions/aggregates/', {'ruleset_id': ruleset_id})
    assert response.status_code == OK

    data = response.json()

    outcomes = {}
    for point in data['outcomes']:
        outcomes[point['key']] = point['count']

    assert outcomes['matched'] == 1
    assert outcomes['error'] == 1

    assert data['versions'][0]['key'] == 1
    assert len(data['hourly']) == 1
    assert data['average_duration_ms'] == 5.0

# ################################################################################################################################

def test_rule_counts_name_what_never_fired(client:'any_', backend:'any_') -> 'None':
    """ Without daily rollups every live rule is reported as one that never fired.
    """
    ruleset_id = _arrange_decisions(backend)
    _ = backend.versions.publish(definition_id=ruleset_id, version=1, actor='anna.k')

    response:'any_' = client.get(f'/rules/rulesets/{ruleset_id}/rule-counts/')
    assert response.status_code == OK

    data = response.json()
    assert data['fired'] == []
    assert data['never_fired'] == ['loans_Preferential_rate']

# ################################################################################################################################

def test_copy_decision_to_scenario(client:'any_', backend:'any_') -> 'None':
    """ A logged decision becomes a ready-made scenario - the input as given, the outputs as expected.
    """
    _ = _arrange_decisions(backend)

    response = post_json(client, '/rules/decisions/decision-matched-1/to-scenario/', {})
    assert response.status_code == OK

    scenario = response.json()['scenario']
    assert scenario['name'] == 'Decision decision-matched-1'
    assert scenario['input'] == {'credit_score': 720}
    assert scenario['expected'] == {'rate': 2.9, 'approved': True}

# ################################################################################################################################

def test_headers_only_decisions_cannot_be_copied(client:'any_', backend:'any_') -> 'None':
    """ A decision whose story was sampled away is loud about having headers only.
    """
    definition = create_ruleset(backend)

    decision = _new_decision(definition.id, 'decision-headers-1', 'customer-789', 'matched', False)
    policy = CapturePolicy(success_percent=0)
    _ = backend.decisions.insert_batch([decision], policy)

    response = post_json(client, '/rules/decisions/decision-headers-1/to-scenario/', {})
    assert response.status_code == BAD_REQUEST
    assert 'headers only' in response.json()['error']

# ################################################################################################################################

def test_replay_runs_the_input_against_any_version(client:'any_', backend:'any_') -> 'None':
    """ Replaying one decision's input against a stored version reports the outcome that version would make.
    """
    _ = _arrange_decisions(backend)

    response = post_json(client, '/rules/decisions/decision-matched-1/replay/', {'version': 1})
    assert response.status_code == OK

    data = response.json()
    assert data['replayed_version'] == 1

    result = data['result']
    assert result['actual'] == {'rate': 2.9, 'approved': True}
    assert result['error'] == ''

# ################################################################################################################################
# ################################################################################################################################
