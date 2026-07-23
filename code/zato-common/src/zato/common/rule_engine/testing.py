# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from copy import deepcopy
from typing import NamedTuple

# Zato
from zato.common.rule_engine.api import RulesManager
from zato.common.rule_engine.errors import RuleEvaluationError
from zato.common.rule_engine.table import StatementSeverity
from zato.common.rule_engine.vocabulary import ErrorCode, new_error

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, dictlist, strlist

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

# What a fired rule's trace line says when its document carries no statement.
Default_Statement_Severity = StatementSeverity.Info

# ################################################################################################################################

class LoadedRules(NamedTuple):
    """ A manager with one ruleset loaded and the full names of its rules, in rule order.
    """
    manager: 'RulesManager'
    rule_names: 'strlist'

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

def _statement_of(document:'anydict') -> 'anydict':
    """ The plain-language statement a fired rule reports - its own, or its docs as a fallback.
    """
    statement = document.get('statement')

    if statement is None:
        statement = {'text': document['docs'], 'severity': Default_Statement_Severity}

    return statement

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

def load_documents(documents:'anydict') -> 'LoadedRules':
    """ Loads canonical rule documents into a fresh manager, ready to evaluate inputs.
    """
    if not documents:
        raise Exception('There are no documents to load')

    # Every document of one load belongs to the same ruleset.
    first = next(iter(documents.values()))
    ruleset_name = first['ruleset_name']

    manager = RulesManager()
    rule_names = manager.load_parsed_rules(documents, ruleset_name)

    out = LoadedRules(manager, rule_names)
    return out

# ################################################################################################################################

def evaluate_input(loaded:'LoadedRules', data:'anydict') -> 'anydict':
    """ Evaluates one input against every loaded rule, collecting the outcome and the trace.

    The outcome merges the assignments of every rule that fired, in rule order.
    An input a rule cannot evaluate comes back with a readable error, never silently.
    """
    fired = []
    actual = {}
    error = ''

    for full_name in loaded.rule_names:
        rule = loaded.manager[full_name]

        # An input a rule cannot evaluate fails loudly, never silently.
        try:
            result = rule.match(data)
        except RuleEvaluationError as e:
            error = str(e)
            break

        # A rule that fired contributes its trace line and its assignments, in rule order.
        if result:
            statement = _statement_of(rule.document)
            fired.append({'rule': full_name, 'statement': statement['text'], 'severity': statement['severity']})
            actual.update(result.then)

    out = {'actual': actual, 'fired': fired, 'error': error}
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
