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

class TestMatchRegex(unittest.TestCase):
    """ Tests regex matching in rule conditions.
    """
    def setUp(self) -> 'None':
        # Initialize the rule test helper with the path to the rules directory
        rules_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        self.helper = RuleTestHelper(rules_dir)
        
        # Find rules with regex patterns
        self.regex_rules = []
        for rule_name, condition in self.helper.rule_conditions.items():
            if '=~' in condition:
                self.regex_rules.append(rule_name)
                logger.info(f'Found regex rule: {rule_name} with condition: {condition}')
        
        if not self.regex_rules:
            self.skipTest('No rules with regex matching found')

    def test_regex_matching(self) -> 'None':
        """ Test regex matching in rule conditions.
        """
        if not self.regex_rules:
            self.skipTest('No rules with regex matching found')
            
        # Use the first rule with regex matching
        rule_name = self.regex_rules[0]
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
            data['doc_id'] = 'XXXYYZ 123'  # This should not match the regex
            result = self.helper.match_rule(rule_name, data)
            self.assertFalse(result, f'Rule {rule_name} should not have matched with non-matching regex pattern')
            
            # Test with edge case pattern
            data['doc_id'] = 'AAABBB'  # Missing the space and numbers
            result = self.helper.match_rule(rule_name, data)
            self.assertFalse(result, f'Rule {rule_name} should not have matched with incomplete pattern')

    def test_regex_with_other_conditions(self) -> 'None':
        """ Test regex pattern combined with other conditions.
        """
        if not self.regex_rules:
            self.skipTest('No rules with regex matching found')
            
        # Find a rule with regex and other conditions
        regex_and_other_rules = []
        for rule_name in self.regex_rules:
            condition = self.helper.get_rule_condition(rule_name)
            if 'and' in condition and '=~' in condition:
                regex_and_other_rules.append(rule_name)
                
        if not regex_and_other_rules:
            self.skipTest('No rules with regex and other conditions found')
            
        # Use the first rule with regex and other conditions
        rule_name = regex_and_other_rules[0]
        logger.info(f'Testing regex with other conditions for rule: {rule_name}')
        
        # Get the rule condition to determine what data to use
        rule_condition = self.helper.get_rule_condition(rule_name)
        logger.info(f'Rule condition: {rule_condition}')
        
        # For a rule with doc_id regex condition and transaction_type
        if 'doc_id' in rule_condition and 'transaction_type' in rule_condition:
            # Test with all conditions matching
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
            self.assertTrue(result, f'Rule {rule_name} should have matched with all conditions true')
            
            # Test with regex matching but other condition false
            data['transaction_type'] = 'refund'  # This should not match
            result = self.helper.match_rule(rule_name, data)
            self.assertFalse(result, f'Rule {rule_name} should not have matched with non-matching transaction type')
            
            # Test with regex not matching but other conditions true
            data['transaction_type'] = 'purchase'  # Reset to matching value
            data['doc_id'] = 'XXXYYZ 123'  # This should not match the regex
            result = self.helper.match_rule(rule_name, data)
            self.assertFalse(result, f'Rule {rule_name} should not have matched with non-matching regex')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    log_format = '%(asctime)s - %(levelname)s - %(name)s:%(lineno)d - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_format)

    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
