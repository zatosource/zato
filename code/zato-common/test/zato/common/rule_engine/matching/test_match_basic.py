# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import unittest
from pathlib import Path

# Zato
from zato.common.test.rule_engine import RuleTestHelper

# ################################################################################################################################
# ################################################################################################################################

class TestMatchBasic(unittest.TestCase):
    """ Tests basic rule matching functionality.
    """
    def setUp(self) -> 'None':
        # The shared zrules fixtures live one level up, next to the test subdirectories.
        rules_dir = Path(os.path.dirname(os.path.abspath(__file__))).parent
        self.helper = RuleTestHelper(rules_dir)

# ################################################################################################################################

    def test_simple_equality_match(self) -> 'None':
        """ A simple equality condition matches equal input and rejects anything else.
        """

        # The matching value produces a match with the expected actions ..
        result = self.helper.match_rule('simple_01_Simple_Equality_Test_1', {'abc': 123})
        self.assertTrue(result)
        self.assertEqual(result.then['result'], 'matched_abc_123')
        self.assertEqual(result.then['action'], 'process')
        self.assertEqual(result.full_name, 'simple_01_Simple_Equality_Test_1')

        # .. and a different value does not match.
        result = self.helper.match_rule('simple_01_Simple_Equality_Test_1', {'abc': 124})
        self.assertFalse(result)

# ################################################################################################################################

    def test_equality_alias(self) -> 'None':
        """ The == alias behaves exactly like the is comparator.
        """
        result = self.helper.match_rule('simple_02_Simple_Equality_Test_2', {'xyz': 456})
        self.assertTrue(result)
        self.assertEqual(result.then['result'], 'matched_xyz_456')

        result = self.helper.match_rule('simple_02_Simple_Equality_Test_2', {'xyz': 457})
        self.assertFalse(result)

# ################################################################################################################################

    def test_string_equality(self) -> 'None':
        """ String equality matches exact values only.
        """
        result = self.helper.match_rule('simple_03_Simple_Equality_Test_3', {'customer_segment': 'premium'})
        self.assertTrue(result)
        self.assertEqual(result.then['service_level'], 'high')
        self.assertEqual(result.then['priority'], 1)

        result = self.helper.match_rule('simple_03_Simple_Equality_Test_3', {'customer_segment': 'standard'})
        self.assertFalse(result)

# ################################################################################################################################

    def test_numeric_comparisons(self) -> 'None':
        """ Numeric comparison comparators respect their boundaries.
        """

        # All three conditions hold ..
        data = {'x': 5, 'max_x': 10, 'amount': 2000, 'min_amount': 1000, 'income_ratio': 0.5}
        result = self.helper.match_rule('parser_ABC_BANK_001', data)
        self.assertTrue(result)
        self.assertEqual(result.then['addition'], 2.5)
        self.assertEqual(result.then['extra_requirements'], True)
        self.assertEqual(result.then['max_term_years'], 3)

        # .. x reaching max_x breaks is less than ..
        data = {'x': 10, 'max_x': 10, 'amount': 2000, 'min_amount': 1000, 'income_ratio': 0.5}
        result = self.helper.match_rule('parser_ABC_BANK_001', data)
        self.assertFalse(result)

        # .. and income_ratio at the boundary breaks is more than.
        data = {'x': 5, 'max_x': 10, 'amount': 2000, 'min_amount': 1000, 'income_ratio': 0.4}
        result = self.helper.match_rule('parser_ABC_BANK_001', data)
        self.assertFalse(result)

# ################################################################################################################################

    def test_list_value_in_then(self) -> 'None':
        """ A list-valued action arrives as a real list.
        """
        result = self.helper.match_rule('simple_04_Simple_Equality_Test_4', {'account_tier': 'gold'})
        self.assertTrue(result)
        self.assertEqual(result.then['fee_waiver'], True)
        self.assertListEqual(result.then['special_offers'], ['premium_service', 'extended_support'])

# ################################################################################################################################

    def test_else_branch_application(self) -> 'None':
        """ A non-match still carries the else actions for the caller to apply.
        """

        # A match applies the then actions, including a reference to input data ..
        data = {'channel': 'email', 'priority': 2}
        result = self.helper.match_rule('parser_Routing_004', data)
        self.assertTrue(result)
        self.assertEqual(result.then['routing'], 'automated')
        self.assertEqual(result.then['handler'], 'email')

        # .. and a non-match applies the else actions instead.
        data = {'channel': 'fax', 'priority': 2}
        result = self.helper.match_rule('parser_Routing_004', data)
        self.assertFalse(result)
        self.assertEqual(result.else_['routing'], 'manual')
        self.assertEqual(result.else_['review_queue'], 'operations')
        self.assertEqual(result.full_name, 'parser_Routing_004')

# ################################################################################################################################

    def test_object_value_delivered_intact(self) -> 'None':
        """ An object-valued action is delivered as the same mapping the rule declares.
        """
        data = {
            'account_balance_average': 600000,
            'customer_segment': 'private_banking',
            'relationship_tenure_years': 3,
        }
        result = self.helper.match_rule('parser_Payments_003', data)
        self.assertTrue(result)
        self.assertEqual(result.then['fee_waiver'], True)
        self.assertEqual(result.then['dedicated_advisor'], True)
        self.assertDictEqual(result.then['status'], {'key1': 'value1', 'key2': 'value2'})

# ################################################################################################################################

    def test_ruleset_access(self) -> 'None':
        """ Rules are reachable through their ruleset as well as by full name.
        """
        ruleset = self.helper.rules_manager['simple']
        rule = ruleset['03_Simple_Equality_Test_3']
        self.assertEqual(rule.full_name, 'simple_03_Simple_Equality_Test_3')

        result = rule.match({'customer_segment': 'premium'})
        self.assertTrue(result)

# ################################################################################################################################

    def test_manager_match_with_rule_list(self) -> 'None':
        """ The manager returns the first match when given a list of rules.
        """
        rule_names = ['simple_01_Simple_Equality_Test_1', 'simple_02_Simple_Equality_Test_2']

        # Both fields are provided because every checked rule needs its own value present.
        result = self.helper.rules_manager.match({'xyz': 456, 'abc': 0}, rule_names)
        self.assertTrue(result)

        if result:
            self.assertEqual(result.full_name, 'simple_02_Simple_Equality_Test_2')

        result = self.helper.rules_manager.match({'xyz': 111, 'abc': 111}, rule_names)
        self.assertIsNone(result)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
