# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest

# Zato
from zato.common.rules.api import RulesManager
from zato.common.rules.errors import RuleEvaluationError
from zato.common.rules.parser import parse_data_details

# ################################################################################################################################
# ################################################################################################################################

# One ruleset used by every test - a condition on a score, a then reference to an input field
# and an else branch, enough to exercise every path a silent null could hide in.
_rules_text = """
rule
    Score_check
when
    credit_score is at least 700
then
    approved = true
    handler = channel
else
    approved = false
"""

# ################################################################################################################################

def _get_manager() -> 'RulesManager':
    """ Builds a manager with the test ruleset loaded, exactly as a file loader would.
    """
    documents, errors = parse_data_details(_rules_text, 'nulls')
    if errors:
        raise Exception(f'Unexpected parse errors -> {errors}')

    manager = RulesManager()
    _ = manager.load_parsed_rules(documents, 'nulls')

    return manager

# ################################################################################################################################
# ################################################################################################################################

class TestNoSilentNulls(unittest.TestCase):
    """ Tests the engine guarantee - a missing value or an unresolvable reference is always
    a loud readable error, never a silent non-match or a None that flows onward.
    """

    def setUp(self) -> 'None':
        self.manager = _get_manager()

# ################################################################################################################################

    def test_complete_data_matches(self) -> 'None':
        """ Complete data evaluates normally, matching and resolving the then reference.
        """
        result = self.manager['nulls_Score_check'].match({'credit_score': 720, 'channel': 'email'})
        self.assertTrue(result)
        self.assertEqual(result.then['approved'], True)
        self.assertEqual(result.then['handler'], 'email')

# ################################################################################################################################

    def test_missing_condition_value_raises(self) -> 'None':
        """ Data without a value a condition needs raises a readable error naming the field.
        """
        with self.assertRaises(RuleEvaluationError) as ctx:
            _ = self.manager['nulls_Score_check'].match({'channel': 'email'})

        self.assertEqual(ctx.exception.rule_name, 'nulls_Score_check')
        self.assertEqual(ctx.exception.field, 'credit_score')
        self.assertIn("the input has no value for 'credit_score'", str(ctx.exception))

# ################################################################################################################################

    def test_missing_condition_value_raises_through_cached_path(self) -> 'None':
        """ The cached evaluation path raises the same readable error as the plain one.
        """
        with self.assertRaises(RuleEvaluationError) as ctx:
            _ = self.manager.match({'channel': 'email'}, ['nulls_Score_check'])

        self.assertEqual(ctx.exception.rule_name, 'nulls_Score_check')
        self.assertIn("the input has no value for 'credit_score'", str(ctx.exception))

# ################################################################################################################################

    def test_unresolvable_then_reference_raises(self) -> 'None':
        """ A then action referencing a field the input does not have raises instead of yielding None.
        """
        with self.assertRaises(RuleEvaluationError) as ctx:
            _ = self.manager['nulls_Score_check'].match({'credit_score': 720})

        self.assertEqual(ctx.exception.rule_name, 'nulls_Score_check')
        self.assertIn("the input has no value for 'channel'", str(ctx.exception))

# ################################################################################################################################

    def test_type_mismatch_raises(self) -> 'None':
        """ A value of the wrong type raises a readable error instead of silently not matching.
        """
        with self.assertRaises(RuleEvaluationError) as ctx:
            _ = self.manager['nulls_Score_check'].match({'credit_score': 'high', 'channel': 'email'})

        self.assertIn('nulls_Score_check cannot run', str(ctx.exception))

# ################################################################################################################################

    def test_else_branch_still_resolves(self) -> 'None':
        """ A clean non-match keeps working - the else actions resolve as before.
        """
        result = self.manager['nulls_Score_check'].match({'credit_score': 500, 'channel': 'email'})
        self.assertFalse(result)
        self.assertEqual(result.else_['approved'], False)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
