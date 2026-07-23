# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json

# Zato
from zato.common.rules.ingestion import DecisionRecorder, Outcome
from zato.common.rules.parser import parse_data_details
from zato.common.rules.sql import CapturePolicy, RuleDefinitionRecord, RuleSQLBackend
from zato.common.rules.sql.constants import Definition_Type_Ruleset, Documents_Key
from zato.common.rules.testing import load_documents

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.rules.testing import LoadedRules
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

_author = 'anna.k'

# One rule that fires on good scores and one input field the rule always needs.
_rules_text = """
rule
    Preferential_rate
docs
    Better rates for our best customers.
when
    credit_score is at least 700
then
    rate = 2.9
    approved = true
"""

# ################################################################################################################################
# ################################################################################################################################

def _documents() -> 'anydict':
    """ Parses the shared rules text into canonical documents keyed by full name.
    """
    documents, errors = parse_data_details(_rules_text, 'loans')
    if errors:
        raise Exception(f'Unexpected parse errors -> {errors}')

    return documents

# ################################################################################################################################

def _create_ruleset(backend:'RuleSQLBackend') -> 'RuleDefinitionRecord':
    """ Stores the ruleset definition the decisions will reference.
    """
    out = backend.definitions.create(
        name='Loans',
        object_type=Definition_Type_Ruleset,
        document={Documents_Key: _documents()},
        author=_author,
        comment='Create the loans ruleset',
    )
    return out

# ################################################################################################################################

def _loaded_rules() -> 'LoadedRules':
    """ Loads the shared documents into a fresh manager.
    """
    out = load_documents(_documents())
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_matched_decision_lands_with_story_and_fired_rules(backend:'RuleSQLBackend') -> 'None':
    """ A matching evaluation lands as one complete decision row.
    """
    definition = _create_ruleset(backend)
    loaded = _loaded_rules()

    # Record one decision through the non-blocking writer ..
    capture_policy = CapturePolicy(success_percent=100, store_fired_rule_ids=True)
    writer = backend.decision_writer(capture_policy=capture_policy)

    with writer:
        recorder = DecisionRecorder(
            writer,
            ruleset_id=definition.id,
            rules_version=1,
            business_key_field='customer_id',
        )
        result = recorder.record(loaded, {'credit_score': 720, 'customer_id': 'C-1'})

    # .. the returned outcome names what happened ..
    assert result['outcome'] == Outcome.Matched
    assert result['actual'] == {'rate': 2.9, 'approved': True}
    assert result['error'] == ''
    assert result['duration_ms'] >= 0

    # .. the decision row carries the promoted header ..
    decision = backend.decisions.get(result['decision_id'])
    assert decision.ruleset_id == definition.id
    assert decision.rules_version == 1
    assert decision.outcome == Outcome.Matched
    assert decision.is_error is False
    assert decision.business_key == 'C-1'

    # .. the promoted fired-rule list matches what actually fired ..
    assert decision.fired_rule_ids is not None
    fired_rule_ids = json.loads(decision.fired_rule_ids)
    assert fired_rule_ids == ['loans_Preferential_rate']

    # .. and the retained story keeps the complete decision.
    assert decision.has_payload is True
    assert decision.payload is not None
    story = json.loads(decision.payload)
    assert story['input'] == {'credit_score': 720, 'customer_id': 'C-1'}
    assert story['outputs'] == {'rate': 2.9, 'approved': True}
    assert story['error'] == ''

# ################################################################################################################################

def test_no_match_decision_has_no_fired_rules(backend:'RuleSQLBackend') -> 'None':
    """ An input no rule matches still lands, marked as a no-match.
    """
    definition = _create_ruleset(backend)
    loaded = _loaded_rules()

    writer = backend.decision_writer()

    with writer:
        recorder = DecisionRecorder(writer, ruleset_id=definition.id, rules_version=1)
        result = recorder.record(loaded, {'credit_score': 500})

    assert result['outcome'] == Outcome.No_Match
    assert result['fired'] == []

    decision = backend.decisions.get(result['decision_id'])
    assert decision.outcome == Outcome.No_Match
    assert decision.is_error is False

    # No configured field means no business key.
    assert decision.business_key is None

# ################################################################################################################################

def test_error_decision_keeps_its_story_even_with_capture_off(backend:'RuleSQLBackend') -> 'None':
    """ An input a rule cannot evaluate lands as an error whose story is always retained.
    """
    definition = _create_ruleset(backend)
    loaded = _loaded_rules()

    # Header-only capture for successes ..
    capture_policy = CapturePolicy(success_percent=0)
    writer = backend.decision_writer(capture_policy=capture_policy)

    with writer:
        recorder = DecisionRecorder(writer, ruleset_id=definition.id, rules_version=1)

        # .. the rule needs credit_score and the input has none ..
        result = recorder.record(loaded, {'amount': 50})

    assert result['outcome'] == Outcome.Error
    assert 'credit_score' in result['error']

    # .. and the error's story is retained despite the capture dial.
    decision = backend.decisions.get(result['decision_id'])
    assert decision.is_error is True
    assert decision.has_payload is True
    assert decision.payload is not None

    story = json.loads(decision.payload)
    assert 'credit_score' in story['error']

# ################################################################################################################################

def test_capture_dial_drops_successful_stories(backend:'RuleSQLBackend') -> 'None':
    """ With header-only capture a successful decision keeps its header but not its story.
    """
    definition = _create_ruleset(backend)
    loaded = _loaded_rules()

    capture_policy = CapturePolicy(success_percent=0)
    writer = backend.decision_writer(capture_policy=capture_policy)

    with writer:
        recorder = DecisionRecorder(writer, ruleset_id=definition.id, rules_version=1)
        result = recorder.record(loaded, {'credit_score': 720})

    decision = backend.decisions.get(result['decision_id'])

    # The promoted header always lands ..
    assert decision.outcome == Outcome.Matched

    # .. while the story obeys the dial.
    assert decision.has_payload is False
    assert decision.payload is None

# ################################################################################################################################
# ################################################################################################################################
