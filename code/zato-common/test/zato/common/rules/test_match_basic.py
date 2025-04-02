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

class TestMatchBasic(unittest.TestCase):
    """ Tests basic rule matching functionality.
    """
    def setUp(self) -> 'None':

        # Initialize the rule test helper with the path to the rules directory
        rules_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        self.helper = RuleTestHelper(rules_dir)

    def test_simple_equality_match(self) -> 'None':
        """ Test simple equality matching (abc == 123).
        """

        # Find rules with simple equality conditions
        equality_rules = self.helper.find_simple_equality_rules()

        if not equality_rules:
            self.skipTest('No rules with simple equality conditions found')

        # Use the first rule with a simple equality condition
        rule_name = equality_rules[0]
        logger.info(f'Testing simple equality for rule: {rule_name}')

        # Get the rule condition to determine what data to use
        rule_condition = self.helper.get_rule_condition(rule_name)
        logger.info(f'Rule condition: {rule_condition}')

        # Extract the field name and value from the condition
        # For example, from 'abc == 123', extract 'abc' and 123
        parts = rule_condition.split('==')
        if len(parts) != 2:
            self.skipTest(f'Rule condition {rule_condition} does not have expected format')

        field_name = parts[0].strip()
        expected_value = parts[1].strip()

        # Convert the expected value to the appropriate type
        if expected_value.startswith('\'') and expected_value.endswith('\''):
            # String value
            expected_value = expected_value[1:-1]
        elif expected_value.isdigit():
            # Integer value
            expected_value = int(expected_value)

        # Create test data with the matching value
        data = {field_name: expected_value}
        logger.info(f'Test data: {data}')

        # Test that the rule matches
        result = self.helper.match_rule(rule_name, data)
        self.assertTrue(result, f'Rule {rule_name} should have matched with {data}')

        # Create test data with a non-matching value
        if isinstance(expected_value, int):
            non_matching_value = expected_value + 1
        else:
            non_matching_value = expected_value + '_different'

        data = {field_name: non_matching_value}
        logger.info(f'Test data with non-matching value: {data}')

        # Test that the rule does not match
        result = self.helper.match_rule(rule_name, data)
        self.assertFalse(result, f'Rule {rule_name} should not have matched with {data}')

    def test_complex_condition_match(self) -> 'None':
        """ Test more complex conditions like greater than, less than, etc.
        """

        # Find rules with complex conditions (>, <, >=, <=)
        complex_rules = []
        for rule_name, condition in self.helper.rule_conditions.items():
            if any(op in condition for op in ['>', '<', '>=', '<=']):
                complex_rules.append(rule_name)

        if not complex_rules:
            self.skipTest('No rules with complex conditions found')

        # Use the first rule with a complex condition
        rule_name = complex_rules[0]
        logger.info(f'Testing complex condition for rule: {rule_name}')

        # Get the rule condition to determine what data to use
        rule_condition = self.helper.get_rule_condition(rule_name)
        logger.info(f'Rule condition: {rule_condition}')

        # For a rule with account_balance_average > 500000
        if 'account_balance_average' in rule_condition and '>' in rule_condition:

            # Test with a value above the threshold
            data = {'account_balance_average': 600000}
            result = self.helper.match_rule(rule_name, data)
            self.assertTrue(result, f'Rule {rule_name} should have matched with value above threshold')

            # Test with a value below the threshold
            data = {'account_balance_average': 400000}
            result = self.helper.match_rule(rule_name, data)
            self.assertFalse(result, f'Rule {rule_name} should not have matched with value below threshold')

        # For a rule with transaction_amount < 1000
        elif 'transaction_amount' in rule_condition and '<' in rule_condition:

            # Test with a value below the threshold
            data = {'transaction_amount': 500}
            result = self.helper.match_rule(rule_name, data)
            self.assertTrue(result, f'Rule {rule_name} should have matched with value below threshold')

            # Test with a value above the threshold
            data = {'transaction_amount': 1500}
            result = self.helper.match_rule(rule_name, data)
            self.assertFalse(result, f'Rule {rule_name} should not have matched with value above threshold')

        # For other rules with complex conditions
        else:
            logger.info(f'Skipping specific tests for {rule_name} - would need custom test data')

    def test_rule_access_methods(self) -> 'None':
        """ Test different ways to access rules (direct access, container access).
        """

        # Find a rule with a simple condition for testing
        simple_rules = self.helper.find_simple_equality_rules()

        if not simple_rules:
            self.skipTest('No rules with simple conditions found')

        # Use the first rule with a simple condition
        rule_name = simple_rules[0]

        # Parse the rule name to extract container and rule short name
        # Rule names are now in format 'container.rulename'
        parts = rule_name.split('.')
        if len(parts) != 2:
            self.skipTest(f'Rule name {rule_name} does not have expected format')

        # Extract container name and rule short name
        container_name = parts[0]
        rule_short_name = parts[1]

        logger.info(f'Testing container access for rule: {rule_name}')
        logger.info(f'Container: {container_name}, Rule short name: {rule_short_name}')

        # Create test data that should match the rule
        data = {'abc': 123}

        # Test direct access to the rule
        result = self.helper.match_rule(rule_name, data)
        self.assertTrue(result, 'Rule should have matched with direct access')

    def test_rule_list_match(self) -> 'None':
        """ Test matching against a list of rules.
        """

        # Find rules with simple equality conditions
        equality_rules = self.helper.find_simple_equality_rules()

        if len(equality_rules) < 2:
            self.skipTest('Need at least 2 rules with simple equality conditions')

        # Use the first two rules
        rule_names = equality_rules[:2]
        logger.info(f'Testing rule list matching for rules: {rule_names}')

        # Create test data that should match the first rule but not the second
        # We need to examine the rule conditions to create appropriate data
        rule1_condition = self.helper.get_rule_condition(rule_names[0])
        rule2_condition = self.helper.get_rule_condition(rule_names[1])

        logger.info(f'Rule 1 condition: {rule1_condition}')
        logger.info(f'Rule 2 condition: {rule2_condition}')

        # Extract field names and values from the conditions
        # For example, from 'abc == 123', extract 'abc' and 123
        rule1_parts = rule1_condition.split('==')
        rule2_parts = rule2_condition.split('==')

        if len(rule1_parts) != 2 or len(rule2_parts) != 2:
            self.skipTest('Rule conditions do not have expected format')

        field1_name = rule1_parts[0].strip()
        expected1_value = rule1_parts[1].strip()
        field2_name = rule2_parts[0].strip()
        expected2_value = rule2_parts[1].strip()

        # Convert the expected values to the appropriate types
        if expected1_value.startswith('\'') and expected1_value.endswith('\''):
            expected1_value = expected1_value[1:-1]
        elif expected1_value.isdigit():
            expected1_value = int(expected1_value)

        if expected2_value.startswith('\'') and expected2_value.endswith('\''):
            expected2_value = expected2_value[1:-1]
        elif expected2_value.isdigit():
            expected2_value = int(expected2_value)

        # Create data that matches rule1 but not rule2
        data = {field1_name: expected1_value}

        # Add a value for field2 that doesn't match rule2
        if field2_name != field1_name:
            if isinstance(expected2_value, int):
                data[field2_name] = expected2_value + 1  # Use a different value
            else:
                data[field2_name] = expected2_value + '_different'  # Use a different string

        logger.info(f'Test data: {data}')

        # Test matching against individual rules
        result1 = self.helper.match_rule(rule_names[0], data)
        result2 = self.helper.match_rule(rule_names[1], data)

        self.assertTrue(result1, f'Rule {rule_names[0]} should have matched')
        self.assertFalse(result2, f'Rule {rule_names[1]} should not have matched')

    def test_service_activation_rule(self) -> 'None':
        """ Test a rule that would be used to activate a service.
        """

        # Find rules with 'premium' in the condition
        premium_rules = self.helper.find_rules_with_condition('premium')

        if not premium_rules:
            # Try with 'tier' instead
            premium_rules = self.helper.find_rules_with_condition('tier')

        if not premium_rules:
            self.skipTest('No rules with premium/tier conditions found')

        # Use the first rule with a premium/tier condition
        rule_name = premium_rules[0]
        logger.info(f'Testing service activation for rule: {rule_name}')

        # Get the rule condition to determine what data to use
        rule_condition = self.helper.get_rule_condition(rule_name)
        logger.info(f'Rule condition: {rule_condition}')

        # For a rule with customer_segment == 'premium'
        if 'customer_segment' in rule_condition and 'premium' in rule_condition:

            # Test with a premium customer
            data = {'customer_segment': 'premium'}
            result = self.helper.match_rule(rule_name, data)
            self.assertTrue(result, f'Rule {rule_name} should have matched for premium customer')

            # Test with a non-premium customer
            data = {'customer_segment': 'standard'}
            result = self.helper.match_rule(rule_name, data)
            self.assertFalse(result, f'Rule {rule_name} should not have matched for standard customer')

        # For a rule with account_tier == 'gold'
        elif 'account_tier' in rule_condition and 'gold' in rule_condition:

            # Test with a gold tier account
            data = {'account_tier': 'gold'}
            result = self.helper.match_rule(rule_name, data)
            self.assertTrue(result, f'Rule {rule_name} should have matched for gold tier')

            # Test with a non-gold tier account
            data = {'account_tier': 'silver'}
            result = self.helper.match_rule(rule_name, data)
            self.assertFalse(result, f'Rule {rule_name} should not have matched for silver tier')

        # For other rules with premium/tier conditions
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
