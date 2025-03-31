# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import unittest
from logging import getLogger
from pathlib import Path

# Zato
from zato.common.test.rules import RuleTestHelper

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class TestMatchComplex(unittest.TestCase):
    """ Tests complex rule matching functionality with compound conditions.
    """
    def setUp(self) -> 'None':

        # Initialize the rule test helper with the path to the rules directory
        rules_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        self.helper = RuleTestHelper(rules_dir)


    def test_compound_and_conditions(self) -> 'None':
        """ Test rules with multiple AND conditions.
        """

        # Find rules with AND conditions but no OR conditions
        and_rules = []
        for rule_name, condition in self.helper.rule_conditions.items():
            if ' and ' in condition and ' or ' not in condition:
                and_rules.append(rule_name)

        if not and_rules:
            self.skipTest('No rules with AND conditions found')

        # Use the first rule with AND conditions
        rule_name = and_rules[0]
        logger.info(f'Testing AND rule: {rule_name}')

        # Get the rule to inspect its conditions
        rule_condition = self.helper.get_rule_condition(rule_name)
        logger.info(f'Rule conditions: {rule_condition}')

        # For a rule with account_balance_average condition
        if 'account_balance_average' in rule_condition:

            # Test with all conditions matching
            data = {
                'account_balance_average': 600000,
                'customer_segment': 'private_banking',
                'relationship_tenure_years': 3
            }

            result = self.helper.match_rule(rule_name, data)
            self.assertTrue(result, f'Rule {rule_name} should have matched with all conditions true')


            # Test with first condition failing
            data = {
                'account_balance_average': 400000,  # Below threshold
                'customer_segment': 'private_banking',
                'relationship_tenure_years': 3
            }

            result = self.helper.match_rule(rule_name, data)
            self.assertFalse(result, f'Rule {rule_name} should not have matched with first condition false')


            # Test with second condition failing
            data = {
                'account_balance_average': 600000,
                'customer_segment': 'retail',  # Not matching
                'relationship_tenure_years': 3
            }

            result = self.helper.match_rule(rule_name, data)
            self.assertFalse(result, f'Rule {rule_name} should not have matched with second condition false')


            # Test with third condition failing
            data = {
                'account_balance_average': 600000,
                'customer_segment': 'private_banking',
                'relationship_tenure_years': 1  # Below threshold
            }

            result = self.helper.match_rule(rule_name, data)
            self.assertFalse(result, f'Rule {rule_name} should not have matched with third condition false')

        # For other rules with AND conditions, create a generic test
        else:
            # This is a generic test for AND conditions
            # We would need to analyze the rule and create appropriate test data
            logger.info(f'Skipping specific tests for {rule_name} - would need custom test data')

    def test_compound_or_conditions(self) -> 'None':
        """ Test rules with multiple OR conditions.
        """

        # Find rules with OR conditions but no AND conditions
        or_rules = []
        for rule_name, condition in self.helper.rule_conditions.items():
            if ' or ' in condition and ' and ' not in condition:
                or_rules.append(rule_name)

        if not or_rules:
            self.skipTest('No rules with OR conditions found')

        # Use the first rule with OR conditions
        rule_name = or_rules[0]
        logger.info(f'Testing OR rule: {rule_name}')

        # Get the rule to inspect its conditions
        rule_condition = self.helper.get_rule_condition(rule_name)
        logger.info(f'Rule conditions: {rule_condition}')

        # For a rule with abc condition (abc == 123 or abc == 456)
        if 'abc == 123' in rule_condition:

            # Test with first condition matching
            data = {'abc': 123}
            result = self.helper.match_rule(rule_name, data)
            self.assertTrue(result, f'Rule {rule_name} should have matched with first condition true')


            # Test with second condition matching
            data = {'abc': 456}
            result = self.helper.match_rule(rule_name, data)
            self.assertTrue(result, f'Rule {rule_name} should have matched with second condition true')


            # Test with both conditions failing
            data = {'abc': 789}
            result = self.helper.match_rule(rule_name, data)
            self.assertFalse(result, f'Rule {rule_name} should not have matched with both conditions false')

        # For other rules with OR conditions, create a generic test
        else:
            # This is a generic test for OR conditions
            # We would need to analyze the rule and create appropriate test data
            logger.info(f'Skipping specific tests for {rule_name} - would need custom test data')

    def test_mixed_and_or_conditions(self) -> 'None':
        """ Test rules with mixed AND and OR conditions.
        """

        # Find rules with both AND and OR conditions
        mixed_rules = []
        for rule_name, condition in self.helper.rule_conditions.items():
            if ' and ' in condition and ' or ' in condition:
                mixed_rules.append(rule_name)

        if not mixed_rules:
            self.skipTest('No rules with mixed AND/OR conditions found')

        # Use the first rule with mixed conditions
        rule_name = mixed_rules[0]
        logger.info(f'Testing mixed AND/OR rule: {rule_name}')

        # Get the rule to inspect its conditions
        rule_condition = self.helper.get_rule_condition(rule_name)
        logger.info(f'Rule conditions: {rule_condition}')

        # For a rule with transaction_type condition
        if 'transaction_type' in rule_condition:

            # Test with all conditions matching
            data = {
                'transaction_type': 'purchase',
                'customer_type': 'retail',  # Different from transaction_type
                'transaction_amount': 600,
                'transaction_category': 'fixed',  # This satisfies the OR condition
                'transaction_time_hour': 3,      # This doesn't match but not needed because of OR
                'title': {'as_upper': 'QBC'},
                'doc_id': 'AAABBB 123',  # Matches regex
                'abc': '2025-01-01T00:00:00',
                'hello': 123,
                'default': {'transaction_amount': 500}  # For comparison
            }

            result = self.helper.match_rule(rule_name, data)
            self.assertTrue(result, f'Rule {rule_name} should have matched with all conditions true')


            # Test with OR condition using the alternative (time_hour instead of category)
            data = {
                'transaction_type': 'purchase',
                'customer_type': 'retail',
                'transaction_amount': 600,
                'transaction_category': 'variable',  # This doesn't match
                'transaction_time_hour': 5,         # But this matches the OR condition
                'title': {'as_upper': 'QBC'},
                'doc_id': 'AAABBB 123',
                'abc': '2025-01-01T00:00:00',
                'hello': 123,
                'default': {'transaction_amount': 500}
            }

            result = self.helper.match_rule(rule_name, data)
            self.assertTrue(result, f'Rule {rule_name} should have matched with alternative OR condition')


            # Test with both OR conditions failing
            data = {
                'transaction_type': 'purchase',
                'customer_type': 'retail',
                'transaction_amount': 600,
                'transaction_category': 'variable',  # This doesn't match
                'transaction_time_hour': 6,         # This also doesn't match
                'title': {'as_upper': 'QBC'},
                'doc_id': 'AAABBB 123',
                'abc': '2025-01-01T00:00:00',
                'hello': 123,
                'default': {'transaction_amount': 500}
            }

            result = self.helper.match_rule(rule_name, data)
            self.assertFalse(result, f'Rule {rule_name} should not have matched with OR condition failing')

        # For other rules with mixed conditions, create a generic test
        else:
            # This is a generic test for mixed conditions
            # We would need to analyze the rule and create appropriate test data
            logger.info(f'Skipping specific tests for {rule_name} - would need custom test data')

    def test_parenthesized_conditions(self) -> 'None':
        """ Test rules with parenthesized conditions to verify operator precedence.
        """

        # Find rules with parentheses in conditions
        parenthesized_rules = []
        for rule_name, condition in self.helper.rule_conditions.items():
            if '(' in condition and ')' in condition:
                parenthesized_rules.append(rule_name)

        if not parenthesized_rules:
            self.skipTest('No rules with parenthesized conditions found')

        # Use the first rule with parenthesized conditions
        rule_name = parenthesized_rules[0]
        logger.info(f'Testing parenthesized rule: {rule_name}')

        # Get the rule to inspect its conditions
        rule_condition = self.helper.get_rule_condition(rule_name)
        logger.info(f'Rule conditions: {rule_condition}')

        # For a rule with transaction_category condition
        if 'transaction_category' in rule_condition:

            # Test with the parenthesized condition true (first option)
            data = {
                'transaction_type': 'purchase',
                'customer_type': 'retail',
                'transaction_amount': 600,
                'transaction_category': 'fixed',  # This makes the parenthesized condition true
                'transaction_time_hour': 3,
                'title': {'as_upper': 'QBC'},
                'doc_id': 'AAABBB 123',
                'abc': '2025-01-01T00:00:00',
                'hello': 123,
                'default': {'transaction_amount': 500}
            }

            result = self.helper.match_rule(rule_name, data)
            self.assertTrue(result, f'Rule {rule_name} should have matched with parenthesized condition true (first option)')


            # Test with the parenthesized condition true (second option)
            data = {
                'transaction_type': 'purchase',
                'customer_type': 'retail',
                'transaction_amount': 600,
                'transaction_category': 'variable',
                'transaction_time_hour': 5,  # This makes the parenthesized condition true
                'title': {'as_upper': 'QBC'},
                'doc_id': 'AAABBB 123',
                'abc': '2025-01-01T00:00:00',
                'hello': 123,
                'default': {'transaction_amount': 500}
            }

            result = self.helper.match_rule(rule_name, data)
            self.assertTrue(result, f'Rule {rule_name} should have matched with parenthesized condition true (second option)')

        # For other rules with parenthesized conditions, create a generic test
        else:
            # This is a generic test for parenthesized conditions
            # We would need to analyze the rule and create appropriate test data
            logger.info(f'Skipping specific tests for {rule_name} - would need custom test data')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    log_format = '%(asctime)s - %(levelname)s - %(name)s:%(lineno)d - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_format)

    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
