# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from copy import deepcopy

# Zato
from zato.common.rule_engine.evaluation import evaluate_input
from zato.common.rule_engine.loading import load_documents
from zato.common.rule_engine.vocabulary import ErrorCode, new_error

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.rule_engine.loading import LoadedRules
    from zato.common.typing_ import anydict, dictlist

# ################################################################################################################################
# ################################################################################################################################

class ScenarioStatus:
    """ How one scenario of a test run ended.
    """
    Passed   = 'passed'
    Failed   = 'failed'
    Explored = 'explored'  # No expectations declared - the run just shows what happened

# ################################################################################################################################

class DiffStatus:
    """ How one expected field compared against the actual outcome.
    """
    Matched   = 'matched'
    Different = 'different'
    Missing   = 'missing'

# ################################################################################################################################
# ################################################################################################################################

def validate_test_set(test_set:'anydict') -> 'dictlist':
    """ Validates a test-set document structurally, returning parser-shaped findings.

    A valid test set has a name and uniquely named scenarios, each with a mapping
    for its input and a mapping for its expected outcome - an empty expected mapping
    means the scenario explores rather than asserts.
    """

    # Our response to produce
    errors = []

    if not test_set['name']:
        errors.append(new_error('', 'test_set', 'name', ErrorCode.Bad_Test_Set, 'A test set needs a name'))

    seen = set()

    for scenario in test_set['scenarios']:
        name = scenario['name']

        if not name:
            errors.append(new_error('', 'test_set', 'name', ErrorCode.Bad_Scenario, 'A scenario needs a name'))
            continue

        if name in seen:
            errors.append(new_error(name, 'test_set', 'name', ErrorCode.Duplicate_Scenario, f'Scenario `{name}` appears more than once'))
            continue

        seen.add(name)

        if not isinstance(scenario['input'], dict):
            errors.append(new_error(name, 'test_set', 'input', ErrorCode.Bad_Scenario, 'A scenario input has to be a mapping'))

        if not isinstance(scenario['expected'], dict):
            errors.append(new_error(name, 'test_set', 'expected', ErrorCode.Bad_Scenario, 'A scenario expectation has to be a mapping'))

    return errors

# ################################################################################################################################
# ################################################################################################################################

def _diff_expected(expected:'anydict', actual:'anydict') -> 'dictlist':
    """ Compares every declared expected field against the actual outcome, field by field.
    """

    # Our response to produce
    out = []

    for field, expected_value in expected.items():

        # A field the run never assigned is missing ..
        if field not in actual:
            entry = {'field': field, 'expected': expected_value, 'actual': None, 'status': DiffStatus.Missing}

        # .. one with another value differs ..
        elif actual[field] != expected_value:
            entry = {'field': field, 'expected': expected_value, 'actual': actual[field], 'status': DiffStatus.Different}

        # .. and one with the same value matches.
        else:
            entry = {'field': field, 'expected': expected_value, 'actual': actual[field], 'status': DiffStatus.Matched}

        out.append(entry)

    return out

# ################################################################################################################################

def _run_scenario(scenario:'anydict', loaded:'LoadedRules') -> 'anydict':
    """ Runs one scenario against every loaded rule, comparing the outcome against its expectations.
    """
    evaluated = evaluate_input(loaded, scenario['input'])

    actual = evaluated['actual']
    error = evaluated['error']

    expected = scenario['expected']
    diffs = _diff_expected(expected, actual)

    # The scenario's status follows from the error, the expectations and the diffs ..
    if error:
        status = ScenarioStatus.Failed

    # .. no expectations means the run explores rather than asserts ..
    elif not expected:
        status = ScenarioStatus.Explored

    else:
        status = ScenarioStatus.Passed
        for diff in diffs:
            if diff['status'] != DiffStatus.Matched:
                status = ScenarioStatus.Failed

    out = {
        'scenario': scenario['name'],
        'status': status,
        'actual': actual,
        'diffs': diffs,
        'fired': evaluated['fired'],
        'error': error,
    }
    return out

# ################################################################################################################################

def run_test_set(test_set:'anydict', documents:'anydict') -> 'anydict':
    """ Runs every scenario of a test set against the given rule documents.

    The documents are the canonical form the parser and the table compiler both
    produce, loaded into a fresh manager for the run. Each scenario comes back
    with its status, its actual outcome, field-level diffs against the declared
    expectations and the fired rules as plain-language statements with severity.
    """
    if not documents:
        raise Exception('A test set needs documents to run against')

    loaded = load_documents(documents)

    scenarios = []
    counts = {
        ScenarioStatus.Passed: 0,
        ScenarioStatus.Failed: 0,
        ScenarioStatus.Explored: 0,
    }

    for scenario in test_set['scenarios']:
        result = _run_scenario(scenario, loaded)
        scenarios.append(result)
        counts[result['status']] += 1

    # Our response to produce
    out = {
        'name': test_set['name'],
        'total': len(scenarios),
        'passed': counts[ScenarioStatus.Passed],
        'failed': counts[ScenarioStatus.Failed],
        'explored': counts[ScenarioStatus.Explored],
        'scenarios': scenarios,
    }
    return out

# ################################################################################################################################

def promote_actual(test_set:'anydict', scenario_name:'str', actual:'anydict') -> 'anydict':
    """ Returns a copy of the test set with one scenario's actual outcome promoted to its expectation.

    This is how exploration turns into assertion - run first, look at what happened,
    then declare that outcome as what has to keep happening.
    """
    out = deepcopy(test_set)

    # Find the one scenario the promotion names ..
    for scenario in out['scenarios']:
        if scenario['name'] == scenario_name:
            break
    else:
        raise Exception(f'No such scenario -> `{scenario_name}`')

    # .. and its expectation becomes the outcome it just produced.
    scenario['expected'] = deepcopy(actual)
    return out

# ################################################################################################################################
# ################################################################################################################################
