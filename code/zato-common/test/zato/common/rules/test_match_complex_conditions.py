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

class TestMatchComplexConditions(unittest.TestCase):
    """ Tests complex logical expressions in rule conditions.
    """
    def setUp(self) -> 'None':
        # Initialize the rule test helper with the path to the rules directory
        rules_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        self.helper = RuleTestHelper(rules_dir)

    def test_nested_conditions(self) -> 'None':
        """ Test rules with nested conditions using parentheses.
        """
        # Find rules with parentheses in conditions
        nested_rules = self.helper.find_rules_with_parentheses()

        if not nested_rules:
            self.skipTest('No rules with nested conditions found')

        # Use the first rule with nested conditions
        rule_name = nested_rules[0]
        logger.info(f'Testing nested conditions for rule: {rule_name}')

        # Get the rule condition to determine what data to use
        rule_condition = self.helper.get_rule_condition(rule_name)
        logger.info(f'Rule condition: {rule_condition}')

        # For a rule with transaction_category condition
        if 'transaction_category' in rule_condition:
            # Test with the first part of the OR condition true
            data = {
                'transaction_type': 'purchase',
                'customer_type': 'retail',
                'transaction_amount': 600,
                'transaction_category': 'fixed',  # This makes the first part of the OR true
                'transaction_time_hour': 3,       # This doesn't match the second part
                'title': {'as_upper': 'QBC'},
                'doc_id': 'AAABBB 123',
                'abc': '2025-01-01T00:00:00',
                'hello': 123,
                'default': {'transaction_amount': 500}
            }

            result = self.helper.match_rule(rule_name, data)
            self.assertTrue(result, f'Rule {rule_name} should have matched with first part of OR true')

            # Test with the second part of the OR condition true
            data = {
                'transaction_type': 'purchase',
                'customer_type': 'retail',
                'transaction_amount': 600,
                'transaction_category': 'variable',  # This doesn't match the first part
                'transaction_time_hour': 5,          # This makes the second part of the OR true
                'title': {'as_upper': 'QBC'},
                'doc_id': 'AAABBB 123',
                'abc': '2025-01-01T00:00:00',
                'hello': 123,
                'default': {'transaction_amount': 500}
            }

            result = self.helper.match_rule(rule_name, data)
            self.assertTrue(result, f'Rule {rule_name} should have matched with second part of OR true')

            # Test with both parts of the OR condition false
            data = {
                'transaction_type': 'purchase',
                'customer_type': 'retail',
                'transaction_amount': 600,
                'transaction_category': 'variable',  # This doesn't match the first part
                'transaction_time_hour': 6,          # This doesn't match the second part
                'title': {'as_upper': 'QBC'},
                'doc_id': 'AAABBB 123',
                'abc': '2025-01-01T00:00:00',
                'hello': 123,
                'default': {'transaction_amount': 500}
            }

            result = self.helper.match_rule(rule_name, data)
            self.assertFalse(result, f'Rule {rule_name} should not have matched with both parts of OR false')

        # For other rules with nested conditions
        else:
            logger.info(f'Skipping specific tests for {rule_name} - would need custom test data')

    def test_operator_precedence(self) -> 'None':
        """ Test operator precedence in rule conditions (AND has higher precedence than OR).
        """
        # Find rules with both AND and OR operators
        mixed_rules = []
        for rule_name, condition in self.helper.rule_conditions.items():
            if ' and ' in condition and ' or ' in condition:
                mixed_rules.append(rule_name)

        if not mixed_rules:
            self.skipTest('No rules with mixed AND/OR operators found')

        # Use the first rule with mixed operators
        rule_name = mixed_rules[0]
        logger.info(f'Testing operator precedence for rule: {rule_name}')

        # Get the rule condition to determine what data to use
        rule_condition = self.helper.get_rule_condition(rule_name)
        logger.info(f'Rule condition: {rule_condition}')

        # For a rule with transaction_type condition
        if 'transaction_type' in rule_condition:
            # Test with AND groups evaluated correctly
            # In a condition like: A and B and (C or D) and E
            # We'll make A, B, C (not D), and E true
            data = {
                'transaction_type': 'purchase',        # A
                'customer_type': 'retail',            # Different from A (for B)
                'transaction_amount': 600,            # Greater than default (for B)
                'transaction_category': 'fixed',      # C is true
                'transaction_time_hour': 3,           # D is false
                'title': {'as_upper': 'QBC'},         # E
                'doc_id': 'AAABBB 123',
                'abc': '2025-01-01T00:00:00',
                'hello': 123,
                'default': {'transaction_amount': 500}
            }

            result = self.helper.match_rule(rule_name, data)
            self.assertTrue(result, f'Rule {rule_name} should have matched with correct operator precedence')

            # Test with one AND condition false
            # Make the title condition false
            data = {
                'transaction_type': 'purchase',
                'customer_type': 'retail',
                'transaction_amount': 600,
                'transaction_category': 'fixed',
                'transaction_time_hour': 3,
                'title': {'as_upper': 'XYZ'},  # E is now false
                'doc_id': 'AAABBB 123',
                'abc': '2025-01-01T00:00:00',
                'hello': 123,
                'default': {'transaction_amount': 500}
            }

            result = self.helper.match_rule(rule_name, data)
            self.assertFalse(result, f'Rule {rule_name} should not have matched with one AND condition false')

        # For other rules with mixed operators
        else:
            logger.info(f'Skipping specific tests for {rule_name} - would need custom test data')

    def test_short_circuit_evaluation(self) -> 'None':
        """ Test short-circuit evaluation in rule conditions.
        """
        # This is a theoretical test as the rule engine's implementation details determine
        # whether short-circuit evaluation is used. We can only test the logical correctness.

        # Find rules with OR conditions
        or_rules = []
        for rule_name, condition in self.helper.rule_conditions.items():
            if ' or ' in condition:
                or_rules.append(rule_name)

        if not or_rules:
            self.skipTest('No rules with OR conditions found')

        # Use the first rule with OR conditions
        rule_name = or_rules[0]
        logger.info(f'Testing short-circuit evaluation for rule: {rule_name}')

        # Get the rule condition to determine what data to use
        rule_condition = self.helper.get_rule_condition(rule_name)
        logger.info(f'Rule condition: {rule_condition}')

        # For a rule with transaction_category condition
        if 'transaction_category' in rule_condition:
            # Test with first condition true (should short-circuit)
            data = {
                'transaction_type': 'purchase',
                'customer_type': 'retail',
                'transaction_amount': 600,
                'transaction_category': 'fixed',  # This makes the first part of the OR true
                # Intentionally omit transaction_time_hour to show short-circuit works
                'title': {'as_upper': 'QBC'},
                'doc_id': 'AAABBB 123',
                'abc': '2025-01-01T00:00:00',
                'hello': 123,
                'default': {'transaction_amount': 500}
            }

            # If short-circuit evaluation works, this should not raise an error
            # even though transaction_time_hour is missing
            result = self.helper.match_rule(rule_name, data)
            self.assertTrue(result, f'Rule {rule_name} should have matched with first part of OR true')

        # For other rules with OR conditions
        else:
            logger.info(f'Skipping specific tests for {rule_name} - would need custom test data')

    def test_regex_matching(self) -> 'None':
        """ Test regex matching in rule conditions.
        """
        # Find rules with regex matching (=~)
        regex_rules = []
        for rule_name, condition in self.helper.rule_conditions.items():
            if '=~' in condition:
                regex_rules.append(rule_name)
                logger.info(f'Found regex rule: {rule_name} with condition: {condition}')

        if not regex_rules:
            # Try to find specific known rules with regex patterns
            for rule_name in self.helper.rule_conditions:
                if 'TELCO_002' in rule_name or '01_Special_Regex_Test' in rule_name:
                    regex_rules.append(rule_name)
                    logger.info(f'Found specific regex rule: {rule_name}')

        if not regex_rules:
            self.skipTest('No rules with regex matching found')

        # Use the first rule with regex matching
        rule_name = regex_rules[0]
        logger.info(f'Testing regex matching for rule: {rule_name}')

        # Get the rule condition to determine what data to use
        rule_condition = self.helper.get_rule_condition(rule_name)
        logger.info(f'Rule condition: {rule_condition}')

        # For a rule with doc_id regex condition
        if 'doc_id' in rule_condition and '=~' in rule_condition:
            # Test with matching pattern
            data = {
                'transaction_type': 'purchase',
                'customer_type': 'retail',
                'transaction_amount': 600,
                'transaction_category': 'fixed',
                'transaction_time_hour': 5,
                'title': {'as_upper': 'QBC'},
                'doc_id': 'AAABBB 123',  # This should match the regex
                'abc': '2025-01-01T00:00:00',
                'hello': 123,
                'default': {'transaction_amount': 500}
            }

            result = self.helper.match_rule(rule_name, data)
            self.assertTrue(result, f'Rule {rule_name} should have matched with regex pattern')

            # Test with non-matching pattern
            data = {
                'transaction_type': 'purchase',
                'customer_type': 'retail',
                'transaction_amount': 600,
                'transaction_category': 'fixed',
                'transaction_time_hour': 5,
                'title': {'as_upper': 'QBC'},
                'doc_id': 'XXXYYZ 123',  # This should not match the regex
                'abc': '2025-01-01T00:00:00',
                'hello': 123,
                'default': {'transaction_amount': 500}
            }

            result = self.helper.match_rule(rule_name, data)
            self.assertFalse(result, f'Rule {rule_name} should not have matched with non-matching regex pattern')

        # For other rules with regex matching
        else:
            logger.info(f'Skipping specific tests for {rule_name} - would need custom test data')

    def test_collection_membership(self) -> 'None':
        """ Test collection membership (in operator) in rule conditions.
        """
        # Find rules with collection membership (in)
        membership_rules = []
        for rule_name, condition in self.helper.rule_conditions.items():
            if ' in ' in condition:
                membership_rules.append(rule_name)

        if not membership_rules:
            self.skipTest('No rules with collection membership found')

        # Use the first rule with collection membership
        rule_name = membership_rules[0]
        logger.info(f'Testing collection membership for rule: {rule_name}')

        # Get the rule condition to determine what data to use
        rule_condition = self.helper.get_rule_condition(rule_name)
        logger.info(f'Rule condition: {rule_condition}')

        # For a rule with critical_infrastructure_involved condition
        if 'critical_infrastructure_involved in' in rule_condition:
            # Test with matching member
            data = {
                'incident_severity': 7,
                'population_affected': 50,
                'critical_infrastructure_involved': 'power_plant'
            }

            result = self.helper.match_rule(rule_name, data)
            self.assertTrue(result, f'Rule {rule_name} should have matched with member in collection')

            # Test with non-matching member
            data = {
                'incident_severity': 7,
                'population_affected': 50,
                'critical_infrastructure_involved': 'shopping_mall'
            }

            result = self.helper.match_rule(rule_name, data)
            self.assertFalse(result, f'Rule {rule_name} should not have matched with member not in collection')

        # For other rules with collection membership
        else:
            logger.info(f'Skipping specific tests for {rule_name} - would need custom test data')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    log_format = '%(asctime)s - %(levelname)s - %(name)s:%(lineno)d - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_format)

    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
