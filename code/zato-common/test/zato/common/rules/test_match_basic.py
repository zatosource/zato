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
from zato.common.rules.api import RulesManager

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class TestMatchBasic(unittest.TestCase):
    """ Tests basic rule matching functionality.
    """

    def setUp(self):
        # Get the current directory where the test files are located
        self.current_dir = Path(os.path.dirname(os.path.abspath(__file__)))

        # Create a rules manager
        self.rules_manager = RulesManager()

        # Load all the rules files
        _ = self.rules_manager.load_rules_from_directory(self.current_dir)

        # Ensure we have loaded the test rules
        self.assertTrue(self.rules_manager._all_rules, 'No rules were loaded')

        # Log the loaded rules for debugging
        logger.info(f'Loaded rules: {list(self.rules_manager._all_rules.keys())}')

        # Log the rule conditions for debugging
        for rule_name, rule in self.rules_manager._all_rules.items():
            if rule_name.startswith('test_parser_'):
                logger.info(f'Rule {rule_name} conditions: {rule.when}')

    def test_simple_equality_match(self):
        """ Test that a rule with a simple equality condition matches correctly.
        """
        # Rule: test_parser_rule_4 has condition: abc == 123 or abc == 456

        # Test with matching data
        data = {'abc': 123}
        result = self.rules_manager.test_parser_rule_4.match(data)

        # Verify the match
        self.assertTrue(result, 'Rule should have matched')
        self.assertEqual(result.full_name, 'test_parser_rule_4')
        self.assertTrue(hasattr(result, 'then'))
        self.assertEqual(result.then.fee_waiver, True)
        self.assertEqual(result.then.dedicated_advisor, True)
        self.assertEqual(result.then.status, {'key1': 'value1', 'key2': 'value2'})

        # Test with alternative matching data
        data = {'abc': 456}
        result = self.rules_manager.test_parser_rule_4.match(data)
        self.assertTrue(result, 'Rule should have matched with alternative value')

        # Test with non-matching data
        data = {'abc': 789}
        result = self.rules_manager.test_parser_rule_4.match(data)
        self.assertFalse(result, 'Rule should not have matched')

    def test_complex_conditions(self):
        """ Test a rule with more complex conditions.
        """
        # Use the Payments_003 rule which has simpler conditions
        # account_balance_average > 500000 and
        # customer_segment == 'private_banking' and
        # relationship_tenure_years > 2

        # Test with matching data
        data = {
            'account_balance_average': 600000,
            'customer_segment': 'private_banking',
            'relationship_tenure_years': 3
        }
        result = self.rules_manager.test_parser_Payments_003.match(data)

        # Verify the match
        self.assertTrue(result, 'Rule should have matched')
        self.assertEqual(result.full_name, 'test_parser_Payments_003')
        self.assertTrue(hasattr(result, 'then'))
        self.assertEqual(result.then.fee_waiver, True)
        self.assertEqual(result.then.dedicated_advisor, True)
        self.assertEqual(result.then.status, {'key1': 'value1', 'key2': 'value2'})

        # Test with non-matching data (one condition fails)
        data = {
            'account_balance_average': 600000,
            'customer_segment': 'retail',  # Not 'private_banking'
            'relationship_tenure_years': 3
        }
        result = self.rules_manager.test_parser_Payments_003.match(data)
        self.assertFalse(result, 'Rule should not have matched')

    def test_access_rule_by_container(self):
        """ Test accessing rules through their container.
        """
        # Access rule through container by attribute
        data = {'abc': 123}
        result = self.rules_manager.test_parser.rule_4.match(data)
        self.assertTrue(result, 'Rule should have matched when accessed through container')

        # Access rule through container by dictionary key
        result = self.rules_manager.test_parser['rule_4'].match(data)
        self.assertTrue(result, 'Rule should have matched when accessed through container dictionary')

    def test_direct_rule_access(self):
        """ Test accessing a rule directly by its full name.
        """
        # Access rule directly by its full name
        data = {'abc': 123}
        result = self.rules_manager['test_parser_rule_4'].match(data)
        self.assertTrue(result, 'Rule should have matched when accessed directly')

        # Access rule directly by attribute
        result = self.rules_manager.test_parser_rule_4.match(data)
        self.assertTrue(result, 'Rule should have matched when accessed directly by attribute')

    def test_match_with_rule_list(self):
        """ Test matching against a specific list of rules.
        """
        # Define data that would match rule_4
        data = {'abc': 123}

        # Match against rule_4 specifically
        result = self.rules_manager.match(data, rules=['test_parser_rule_4'])

        # Verify we got a match
        self.assertTrue(result, 'Should have found a matching rule')
        self.assertEqual(result.full_name, 'test_parser_rule_4')

        # Try with a list where no rules match by providing data that doesn't match rule_4
        no_match_data = {'abc': 789}  # rule_4 only matches 123 or 456
        result = self.rules_manager.match(no_match_data, rules=['test_parser_rule_4'])
        self.assertFalse(result, 'Should not have found a matching rule')

    def test_bss_rule(self):
        """ Test a BSS rule from the test_exec.zrules file.
        """
        # First, find the correct rule name for the BSS rule
        bss_rule_names = [name for name in self.rules_manager._all_rules.keys() if name.startswith('test_exec_') and 'BSS' in name]

        if not bss_rule_names:
            self.skipTest('No BSS rules found')

        # Use the first BSS rule found
        bss_rule_name = bss_rule_names[0]
        logger.info(f'Testing BSS rule: {bss_rule_name}')

        # Get the rule to inspect its conditions
        bss_rule = self.rules_manager._all_rules[bss_rule_name]
        logger.info(f'Rule conditions: {bss_rule.when}')

        # For test_exec_02_BSS_Service_Activation
        if 'Service_Activation' in bss_rule_name:
            # Test with matching data
            data = {
                'address_serviceable': True,
                'infrastructure_available': True,
                'outstanding_balance': 0,
                'service_restrictions_count': 0,
                'credit_score': 700
            }
            result = self.rules_manager[bss_rule_name].match(data)

            # Verify the match
            self.assertTrue(result, f'Rule {bss_rule_name} should have matched')
            self.assertEqual(result.full_name, bss_rule_name)
            self.assertTrue(hasattr(result, 'then'))
            self.assertEqual(result.then.service_activation_eligible, True)

            # Test with non-matching data
            data['credit_score'] = 500  # Below required 600
            result = self.rules_manager[bss_rule_name].match(data)
            self.assertFalse(result, f'Rule {bss_rule_name} should not have matched')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    log_format = '%(asctime)s - %(levelname)s - %(name)s:%(lineno)d - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_format)

    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
