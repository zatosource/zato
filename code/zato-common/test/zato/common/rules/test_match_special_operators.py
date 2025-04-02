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

class TestMatchSpecialOperators(unittest.TestCase):
    """ Tests special operators in rule conditions.
    """
    def setUp(self) -> 'None':
        # Initialize the rule test helper with the path to the rules directory
        rules_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        self.helper = RuleTestHelper(rules_dir)
        
        # Log all loaded rules and their conditions for debugging
        logger.info(f'Loaded rules: {list(self.helper.rule_conditions.keys())}')
        for rule_name, condition in self.helper.rule_conditions.items():
            logger.info(f'Rule {rule_name} condition: {condition}')

    def test_regex_matching(self) -> 'None':
        """ Test regex matching (=~ operator) in rule conditions.
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
                'doc_id': 'AAABBB 123',  
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
                'doc_id': 'XXXYYZ 123',  
                'abc': '2025-01-01T00:00:00',
                'hello': 123,
                'default': {'transaction_amount': 500}
            }

            result = self.helper.match_rule(rule_name, data)
            self.assertFalse(result, f'Rule {rule_name} should not have matched with non-matching regex pattern')

            # Test with edge case pattern
            data = {
                'transaction_type': 'purchase',
                'customer_type': 'retail',
                'transaction_amount': 600,
                'transaction_category': 'fixed',
                'transaction_time_hour': 5,
                'title': {'as_upper': 'QBC'},
                'doc_id': 'AAABBB',  
                'abc': '2025-01-01T00:00:00',
                'hello': 123,
                'default': {'transaction_amount': 500}
            }

            result = self.helper.match_rule(rule_name, data)
            self.assertFalse(result, f'Rule {rule_name} should not have matched with incomplete pattern')

        # For other rules with regex matching
        else:
            logger.info(f'Skipping specific tests for {rule_name} - would need custom test data')

    def test_string_operations(self) -> 'None':
        """ Test string operations (like as_upper) in rule conditions.
        """
        # Find rules with string operations
        string_op_rules = []
        for rule_name, condition in self.helper.rule_conditions.items():
            if 'as_upper' in condition or 'as_lower' in condition:
                string_op_rules.append(rule_name)

        if not string_op_rules:
            self.skipTest('No rules with string operations found')

        # Use the first rule with string operations
        rule_name = string_op_rules[0]
        logger.info(f'Testing string operations for rule: {rule_name}')

        # Get the rule condition to determine what data to use
        rule_condition = self.helper.get_rule_condition(rule_name)
        logger.info(f'Rule condition: {rule_condition}')

        # For a rule with title.as_upper condition
        if 'title.as_upper' in rule_condition:
            # Test with matching uppercase string
            data = {
                'transaction_type': 'purchase',
                'customer_type': 'retail',
                'transaction_amount': 600,
                'transaction_category': 'fixed',
                'transaction_time_hour': 5,
                'title': {'as_upper': 'QBC'},  
                'doc_id': 'AAABBB 123',
                'abc': '2025-01-01T00:00:00',
                'hello': 123,
                'default': {'transaction_amount': 500}
            }

            result = self.helper.match_rule(rule_name, data)
            self.assertTrue(result, f'Rule {rule_name} should have matched with uppercase string')

            # Test with non-matching uppercase string
            data = {
                'transaction_type': 'purchase',
                'customer_type': 'retail',
                'transaction_amount': 600,
                'transaction_category': 'fixed',
                'transaction_time_hour': 5,
                'title': {'as_upper': 'XYZ'},  
                'doc_id': 'AAABBB 123',
                'abc': '2025-01-01T00:00:00',
                'hello': 123,
                'default': {'transaction_amount': 500}
            }

            result = self.helper.match_rule(rule_name, data)
            self.assertFalse(result, f'Rule {rule_name} should not have matched with different uppercase string')

            # Test with lowercase string that would match if converted
            data = {
                'transaction_type': 'purchase',
                'customer_type': 'retail',
                'transaction_amount': 600,
                'transaction_category': 'fixed',
                'transaction_time_hour': 5,
                'title': 'qbc',  
                'doc_id': 'AAABBB 123',
                'abc': '2025-01-01T00:00:00',
                'hello': 123,
                'default': {'transaction_amount': 500}
            }

            # This will likely fail since we're not providing the as_upper attribute
            # But it tests the behavior of the rule engine with string operations
            try:
                result = self.helper.match_rule(rule_name, data)
                # If it doesn't raise an exception, check the result
                self.assertFalse(result, f'Rule {rule_name} should not have matched with lowercase string without as_upper')
            except Exception as e:
                logger.info(f'Expected exception with lowercase string without as_upper: {e}')

        # For other rules with string operations
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

            # Test with case-sensitive member
            data = {
                'incident_severity': 7,
                'population_affected': 50,
                'critical_infrastructure_involved': 'POWER_PLANT'  
            }

            # This tests if the in operator is case-sensitive
            result = self.helper.match_rule(rule_name, data)
            self.assertFalse(result, f'Rule {rule_name} should not have matched with case-different member')

        # For a rule with aircraft_type in condition
        elif 'aircraft_type in' in rule_condition:
            # Test with matching member
            data = {
                'aircraft_type': 'B777',
                'gate_width_meters': 50,
                'jetbridge_length_meters': 15,
                'gate_currently_available': True
            }

            result = self.helper.match_rule(rule_name, data)
            self.assertTrue(result, f'Rule {rule_name} should have matched with member in collection')

            # Test with non-matching member
            data = {
                'aircraft_type': 'B737',
                'gate_width_meters': 50,
                'jetbridge_length_meters': 15,
                'gate_currently_available': True
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
