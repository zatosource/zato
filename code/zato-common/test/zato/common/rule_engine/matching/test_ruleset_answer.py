# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest

# Zato
from zato.common.rule_engine.errors import RuleEvaluationError
from zato.common.rule_engine.evaluation import evaluate_input
from zato.common.rule_engine.loading import load_documents
from zato.common.rule_engine.parser import parse_data_details

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

# Two rules that fire together and one that does not, with the two overlapping on `rate` so the
# order in which a merged answer applies them is observable.
_rules_text = """
rule
    01_Standard_rate
docs
    Every loan starts at the standard rate.
when
    amount is more than 0
then
    rate = 4.5
    fee = 15.0

rule
    02_Preferential_rate
docs
    Better rates for our best customers.
when
    credit_score is at least 700
then
    rate = 2.9
    approved = true

rule
    03_Declined
docs
    Low scores are declined.
when
    credit_score is less than 500
then
    approved = false
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
# ################################################################################################################################

class TestRulesetAnswer(unittest.TestCase):
    """ Tests the one answer a whole ruleset gives - every rule that fires contributes to it.
    """

    def setUp(self) -> 'None':
        self.loaded = load_documents(_get_documents())
        self.ruleset = self.loaded.manager['loans']

# ################################################################################################################################

    def test_every_firing_rule_contributes(self) -> 'None':
        """ Two rules that both fire both contribute their assignments, the later one having the final say.
        """
        outcome = self.ruleset.match({'amount': 1000, 'credit_score': 720})

        self.assertTrue(outcome)

        # The standard rate fired first and its fee stands, the preferential rate came after
        # it and its own rate is the one that stays.
        self.assertEqual(outcome.then['fee'], 15.0)
        self.assertEqual(outcome.then['rate'], 2.9)
        self.assertEqual(outcome.then['approved'], True)

# ################################################################################################################################

    def test_the_trace_names_every_rule_that_fired(self) -> 'None':
        """ The outcome carries one trace line per fired rule, in rule order, with its statement.
        """
        outcome = self.ruleset.match({'amount': 1000, 'credit_score': 720})
        fired = outcome.fired

        self.assertEqual(len(fired), 2)

        first = fired[0]
        second = fired[1]

        self.assertEqual(first['rule'], 'loans_01_Standard_rate')
        self.assertEqual(first['statement'], 'Every loan starts at the standard rate.')
        self.assertEqual(first['severity'], 'info')

        self.assertEqual(second['rule'], 'loans_02_Preferential_rate')

# ################################################################################################################################

    def test_no_rule_firing_is_an_empty_answer(self) -> 'None':
        """ Input no rule fires on answers with nothing assigned rather than with a rule's else actions.
        """
        outcome = self.ruleset.match({'amount': 0, 'credit_score': 600})

        self.assertFalse(outcome)
        self.assertDictEqual(outcome.then, {})
        self.assertListEqual(outcome.fired, [])

# ################################################################################################################################

    def test_both_doors_give_the_same_answer(self) -> 'None':
        """ The in-process ruleset door and the REST-facing evaluation answer identically.
        """
        data = {'amount': 1000, 'credit_score': 720}

        outcome = self.ruleset.match(data)
        evaluated = evaluate_input(self.loaded, data)

        self.assertDictEqual(evaluated['actual'], outcome.then)
        self.assertListEqual(evaluated['fired'], outcome.fired)
        self.assertEqual(evaluated['error'], '')

# ################################################################################################################################

    def test_unevaluable_input_raises_in_process(self) -> 'None':
        """ In process a rule that cannot evaluate the input raises, rather than answering in half.
        """
        with self.assertRaises(RuleEvaluationError) as ctx:
            _ = self.ruleset.match({'credit_score': 720})

        self.assertIn("the input has no value for 'amount'", str(ctx.exception))

# ################################################################################################################################

    def test_unevaluable_input_is_reported_over_rest(self) -> 'None':
        """ The same input comes back from the REST-facing path as a readable message.
        """
        evaluated = evaluate_input(self.loaded, {'credit_score': 720})

        self.assertIn("the input has no value for 'amount'", evaluated['error'])
        self.assertDictEqual(evaluated['actual'], {})

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
