# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.rule_engine.ingestion import evaluate_decision, Outcome
from zato.common.rule_engine.loading import load_documents
from zato.common.rule_engine.parser import parse_data_details

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.rule_engine.loading import LoadedRules

# ################################################################################################################################
# ################################################################################################################################

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

def _loaded_rules() -> 'LoadedRules':
    """ Loads the shared rules into a fresh manager.
    """
    documents, errors = parse_data_details(_rules_text, 'loans')
    if errors:
        raise Exception(f'Unexpected parse errors -> {errors}')

    out = load_documents(documents)
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_matched_decision_carries_outputs_and_fired_rules() -> 'None':
    """ A matching evaluation returns the outputs and the rules that fired.
    """
    result = evaluate_decision(_loaded_rules(), {'credit_score': 720})

    assert result['outcome'] == Outcome.Matched
    assert result['actual'] == {'rate': 2.9, 'approved': True}
    assert result['error'] == ''
    assert result['duration_ms'] >= 0

    fired_rules = []
    for entry in result['fired']:
        fired_rules.append(entry['rule'])

    assert fired_rules == ['loans_Preferential_rate']

# ################################################################################################################################

def test_no_match_decision_has_no_fired_rules() -> 'None':
    """ An input no rule matches is reported as a no-match.
    """
    result = evaluate_decision(_loaded_rules(), {'credit_score': 500})

    assert result['outcome'] == Outcome.No_Match
    assert result['fired'] == []

# ################################################################################################################################

def test_error_decision_names_the_missing_input() -> 'None':
    """ An input a rule cannot evaluate is reported as an error that names what is missing.
    """
    result = evaluate_decision(_loaded_rules(), {'amount': 50})

    assert result['outcome'] == Outcome.Error
    assert 'credit_score' in result['error']

# ################################################################################################################################
# ################################################################################################################################
