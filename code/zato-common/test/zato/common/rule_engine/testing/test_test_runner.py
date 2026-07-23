# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest

# Zato
from zato.common.rule_engine.parser import parse_data_details
from zato.common.rule_engine.table import compile_table
from zato.common.rule_engine.testing import DiffStatus, ScenarioStatus, promote_actual, run_test_set, validate_test_set
from zato.common.rule_engine.vocabulary import ErrorCode

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

# Two rules over disjoint targets - one prices a loan, the other flags it for review.
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

rule
    Large_amount_review
docs
    Large amounts need a manual look.
when
    amount is more than 100000
then
    needs_review = true
"""

# ################################################################################################################################

def _get_documents() -> 'anydict':
    """ Parses the shared rules text into documents keyed by full name.
    """
    documents, errors = parse_data_details(_rules_text, 'loans')
    if errors:
        raise Exception(f'Unexpected parse errors -> {errors}')

    return documents

# ################################################################################################################################

def _new_test_set(scenarios:'list') -> 'anydict':
    out = {'name': 'Loan suite', 'scenarios': scenarios}
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestValidateTestSet(unittest.TestCase):
    """ Tests the structural checks over a test-set document.
    """

    def test_valid_test_set_has_no_findings(self) -> 'None':
        """ A named set with uniquely named scenarios over mappings validates cleanly.
        """
        scenario = {'name': 'Basic', 'input': {'credit_score': 720, 'amount': 50}, 'expected': {}}
        errors = validate_test_set(_new_test_set([scenario]))
        self.assertListEqual(errors, [])

# ################################################################################################################################

    def test_missing_names_are_reported(self) -> 'None':
        """ A nameless set and a nameless scenario are both reported.
        """
        scenario = {'name': '', 'input': {}, 'expected': {}}
        test_set = _new_test_set([scenario])
        test_set['name'] = ''

        errors = validate_test_set(test_set)

        codes = []
        for error in errors:
            codes.append(error['code'])

        self.assertIn(ErrorCode.Bad_Test_Set, codes)
        self.assertIn(ErrorCode.Bad_Scenario, codes)

# ################################################################################################################################

    def test_duplicate_scenario_names_are_reported(self) -> 'None':
        """ Two scenarios sharing a name are reported.
        """
        first = {'name': 'Basic', 'input': {}, 'expected': {}}
        second = {'name': 'Basic', 'input': {}, 'expected': {}}

        errors = validate_test_set(_new_test_set([first, second]))
        self.assertEqual(len(errors), 1)

        error = errors[0]
        self.assertEqual(error['code'], ErrorCode.Duplicate_Scenario)

# ################################################################################################################################

    def test_non_mapping_input_is_reported(self) -> 'None':
        """ A scenario whose input or expectation is not a mapping is reported.
        """
        scenario = {'name': 'Basic', 'input': [1, 2], 'expected': {}}

        errors = validate_test_set(_new_test_set([scenario]))
        self.assertEqual(len(errors), 1)

        error = errors[0]
        self.assertEqual(error['code'], ErrorCode.Bad_Scenario)
        self.assertEqual(error['field'], 'input')

# ################################################################################################################################
# ################################################################################################################################

class TestRunTestSet(unittest.TestCase):
    """ Tests the runner - statuses, diffs, traces and errors.
    """

    def setUp(self) -> 'None':
        self.documents = _get_documents()

# ################################################################################################################################

    def test_matching_expectations_pass(self) -> 'None':
        """ A scenario whose expected fields all match the outcome passes.
        """
        scenario = {
            'name': 'Top customer',
            'input': {'credit_score': 720, 'amount': 50},
            'expected': {'rate': 2.9, 'approved': True},
        }
        run = run_test_set(_new_test_set([scenario]), self.documents)

        self.assertEqual(run['total'], 1)
        self.assertEqual(run['passed'], 1)

        result = run['scenarios'][0]
        self.assertEqual(result['status'], ScenarioStatus.Passed)

        # Every declared field carries its own matched diff.
        for diff in result['diffs']:
            self.assertEqual(diff['status'], DiffStatus.Matched)

# ################################################################################################################################

    def test_differing_and_missing_fields_fail(self) -> 'None':
        """ A wrong value and a never-assigned field come back as their own diff entries.
        """
        scenario = {
            'name': 'Wrong expectations',
            'input': {'credit_score': 720, 'amount': 50},
            'expected': {'rate': 9.9, 'needs_review': True},
        }
        run = run_test_set(_new_test_set([scenario]), self.documents)

        result = run['scenarios'][0]
        self.assertEqual(result['status'], ScenarioStatus.Failed)

        diffs = result['diffs']
        first = diffs[0]
        second = diffs[1]

        self.assertEqual(first['field'], 'rate')
        self.assertEqual(first['status'], DiffStatus.Different)
        self.assertEqual(first['expected'], 9.9)
        self.assertEqual(first['actual'], 2.9)

        # The review rule never fired, so its field was never assigned at all.
        self.assertEqual(second['field'], 'needs_review')
        self.assertEqual(second['status'], DiffStatus.Missing)
        self.assertIsNone(second['actual'])

# ################################################################################################################################

    def test_no_expectations_means_exploration(self) -> 'None':
        """ A scenario with an empty expectation explores - it reports, it never asserts.
        """
        scenario = {
            'name': 'Just looking',
            'input': {'credit_score': 720, 'amount': 50},
            'expected': {},
        }
        run = run_test_set(_new_test_set([scenario]), self.documents)

        self.assertEqual(run['explored'], 1)

        result = run['scenarios'][0]
        self.assertEqual(result['status'], ScenarioStatus.Explored)
        self.assertEqual(result['actual']['rate'], 2.9)

# ################################################################################################################################

    def test_fired_rules_come_back_as_statements(self) -> 'None':
        """ The trace lists each fired rule with its statement - here, the docs fallback.
        """
        scenario = {
            'name': 'Both fire',
            'input': {'credit_score': 720, 'amount': 200000},
            'expected': {},
        }
        run = run_test_set(_new_test_set([scenario]), self.documents)

        result = run['scenarios'][0]
        fired = result['fired']
        self.assertEqual(len(fired), 2)

        first = fired[0]
        second = fired[1]

        self.assertEqual(first['rule'], 'loans_Large_amount_review')
        self.assertEqual(first['statement'], 'Large amounts need a manual look.')
        self.assertEqual(first['severity'], 'info')

        self.assertEqual(second['rule'], 'loans_Preferential_rate')
        self.assertEqual(second['statement'], 'Better rates for our best customers.')

# ################################################################################################################################

    def test_unevaluable_input_fails_loudly(self) -> 'None':
        """ Input a rule cannot evaluate fails the scenario with a readable error, never silently.
        """
        scenario = {
            'name': 'No amount',
            'input': {'credit_score': 720},
            'expected': {'rate': 2.9},
        }
        run = run_test_set(_new_test_set([scenario]), self.documents)

        result = run['scenarios'][0]
        self.assertEqual(result['status'], ScenarioStatus.Failed)
        self.assertIn("the input has no value for 'amount'", result['error'])

# ################################################################################################################################

    def test_empty_documents_are_refused(self) -> 'None':
        """ Running against nothing is an error, not an empty green run.
        """
        scenario = {'name': 'Basic', 'input': {}, 'expected': {}}

        with self.assertRaises(Exception) as ctx:
            _ = run_test_set(_new_test_set([scenario]), {})

        self.assertIn('needs documents', str(ctx.exception))

# ################################################################################################################################

    def test_table_statements_carry_their_severity(self) -> 'None':
        """ Documents compiled from a table report their columns' own statements and severities.
        """
        table = {
            'name': 'Loan approval',
            'docs': '',
            'conditions': [{'letter': 'a', 'subject': 'credit_score'}],
            'actions': [{'target': 'approved'}],
            'columns': [
                {
                    'number': 1,
                    'cells': {'a': '< 500'},
                    'actions': {'approved': 'false'},
                    'statement': {'text': 'Low scores are declined.', 'severity': 'violation'},
                },
            ],
        }
        documents = compile_table(table)

        scenario = {
            'name': 'Low score',
            'input': {'credit_score': 400},
            'expected': {'approved': False},
        }
        run = run_test_set(_new_test_set([scenario]), documents)

        result = run['scenarios'][0]
        self.assertEqual(result['status'], ScenarioStatus.Passed)

        fired = result['fired']
        self.assertEqual(len(fired), 1)

        entry = fired[0]
        self.assertEqual(entry['statement'], 'Low scores are declined.')
        self.assertEqual(entry['severity'], 'violation')

# ################################################################################################################################
# ################################################################################################################################

class TestPromoteActual(unittest.TestCase):
    """ Tests promoting an actual outcome to a scenario's expectation.
    """

    def test_promotion_turns_exploration_into_assertion(self) -> 'None':
        """ The promoted outcome becomes the expectation of a copy, the original untouched.
        """
        scenario = {'name': 'Just looking', 'input': {'credit_score': 720, 'amount': 50}, 'expected': {}}
        test_set = _new_test_set([scenario])

        documents = _get_documents()
        run = run_test_set(test_set, documents)

        result = run['scenarios'][0]
        promoted = promote_actual(test_set, 'Just looking', result['actual'])

        promoted_scenario = promoted['scenarios'][0]
        self.assertDictEqual(promoted_scenario['expected'], {'rate': 2.9, 'approved': True})

        # The original test set still explores.
        self.assertEqual(scenario['expected'], {})

        # The promoted set now passes as an assertion.
        rerun = run_test_set(promoted, documents)
        self.assertEqual(rerun['passed'], 1)

# ################################################################################################################################

    def test_unknown_scenario_is_refused(self) -> 'None':
        """ Promoting into a scenario the set does not have is a loud error.
        """
        scenario = {'name': 'Basic', 'input': {}, 'expected': {}}
        test_set = _new_test_set([scenario])

        with self.assertRaises(Exception) as ctx:
            _ = promote_actual(test_set, 'No_such', {'approved': True})

        self.assertIn('No such scenario', str(ctx.exception))

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
