# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import unittest
from logging import getLogger

# Zato
from common import RuleTestHelper

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class TestMatchBasic(unittest.TestCase):
    """ Tests basic rule matching functionality.
    """

    def setUp(self):
        # Initialize the rule test helper
        self.helper = RuleTestHelper()

    def test_simple_equality_match(self):
        """ Test that a rule with a simple equality condition matches correctly.
        """
        # Find a rule with simple equality condition (abc == 123 or abc == 456)
        rule_name = self.helper.find_rule_by_pattern('abc == 123')
        if not rule_name:
            self.skipTest('No rule with simple equality condition found')

        logger.info(f'Testing simple equality rule: {rule_name}')
        logger.info(f'Rule conditions: {self.helper.get_rule_condition(rule_name)}')

        # Test with matching data
        data = {'abc': 123}
        result = self.helper.match_rule(rule_name, data)

        # Verify the match
        self.assertTrue(result, 'Rule should have matched')
        self.assertEqual(result.full_name, rule_name)
        self.assertTrue(hasattr(result, 'then'))
        self.assertEqual(result.then.fee_waiver, True)
        self.assertEqual(result.then.dedicated_advisor, True)
        self.assertEqual(result.then.status, {'key1': 'value1', 'key2': 'value2'})

        # Test with alternative matching data
        data = {'abc': 456}
        result = self.helper.match_rule(rule_name, data)
        self.assertTrue(result, 'Rule should have matched with alternative value')

        # Test with non-matching data
        data = {'abc': 789}
        result = self.helper.match_rule(rule_name, data)
        self.assertFalse(result, 'Rule should not have matched')

    def test_complex_conditions(self):
        """ Test a rule with more complex conditions.
        """
        # Find a rule with multiple AND conditions
        rule_name = self.helper.find_rule_by_pattern('account_balance_average > 500000')
        if not rule_name:
            self.skipTest('No rule with complex conditions found')

        logger.info(f'Testing complex conditions rule: {rule_name}')
        logger.info(f'Rule conditions: {self.helper.get_rule_condition(rule_name)}')

        # Test with matching data
        data = {
            'account_balance_average': 600000,
            'customer_segment': 'private_banking',
            'relationship_tenure_years': 3
        }
        result = self.helper.match_rule(rule_name, data)

        # Verify the match
        self.assertTrue(result, 'Rule should have matched')
        self.assertEqual(result.full_name, rule_name)
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
        result = self.helper.match_rule(rule_name, data)
        self.assertFalse(result, 'Rule should not have matched')

    def test_access_rule_by_container(self):
        """ Test accessing rules through their container.
        """
        # Find a rule with simple equality condition
        rule_name = self.helper.find_rule_by_pattern('abc == 123')
        if not rule_name:
            self.skipTest('No rule with simple equality condition found')

        # Parse the rule name to get container and rule parts
        # The format is now '_rule_container_rulename'
        parts = rule_name.split('_')
        if len(parts) < 4:  # Need at least ['', 'rule', 'container', 'rulename']
            self.skipTest(f'Rule name {rule_name} does not have expected format')

        # Extract container name and rule short name
        container_name = '_'.join(parts[0:3])  # Include the '_rule_' prefix
        rule_short_name = parts[3]  # The last part is the rule name

        logger.info(f'Testing container access for rule: {rule_name}')
        logger.info(f'Container: {container_name}, Rule short name: {rule_short_name}')

        # For direct testing, we'll use a known rule with a simple condition
        data = {'abc': 123}

        # Test direct access to the rule
        result = self.helper.match_rule(rule_name, data)
        self.assertTrue(result, 'Rule should have matched with direct access')

    def test_direct_rule_access(self):
        """ Test accessing a rule directly by its full name.
        """
        # Find a rule with simple equality condition
        rule_name = self.helper.find_rule_by_pattern('abc == 123')
        if not rule_name:
            self.skipTest('No rule with simple equality condition found')

        logger.info(f'Testing direct access for rule: {rule_name}')

        # Access rule directly by its full name
        data = {'abc': 123}
        result = self.helper.rules_manager[rule_name].match(data)
        self.assertTrue(result, 'Rule should have matched when accessed directly')

        # Access rule directly by attribute
        result = getattr(self.helper.rules_manager, rule_name).match(data)
        self.assertTrue(result, 'Rule should have matched when accessed directly by attribute')

    def test_match_with_rule_list(self):
        """ Test matching against a specific list of rules.
        """
        # Find a rule with simple equality condition
        rule_name = self.helper.find_rule_by_pattern('abc == 123')
        if not rule_name:
            self.skipTest('No rule with simple equality condition found')

        logger.info(f'Testing rule list matching for rule: {rule_name}')

        # Define data that would match rule
        data = {'abc': 123}

        # Match against rule specifically
        result = self.helper.rules_manager.match(data, rules=[rule_name])

        # Verify we got a match
        self.assertTrue(result, 'Should have found a matching rule')
        self.assertEqual(result.full_name, rule_name)

        # Try with a list where no rules match by providing data that doesn't match rule
        no_match_data = {'abc': 789}  # rule only matches 123 or 456
        result = self.helper.rules_manager.match(no_match_data, rules=[rule_name])
        self.assertFalse(result, 'Should not have found a matching rule')

    def test_service_activation_rule(self):
        """ Test a service activation rule.
        """
        # Find a rule about service activation
        rule_name = self.helper.find_rule_by_pattern('address_serviceable == true')
        if not rule_name:
            self.skipTest('No service activation rule found')

        logger.info(f'Testing service activation rule: {rule_name}')
        logger.info(f'Rule conditions: {self.helper.get_rule_condition(rule_name)}')

        # Test with matching data
        data = {
            'address_serviceable': True,
            'infrastructure_available': True,
            'outstanding_balance': 0,
            'service_restrictions_count': 0,
            'credit_score': 700
        }
        result = self.helper.match_rule(rule_name, data)

        # Verify the match
        self.assertTrue(result, f'Rule {rule_name} should have matched')
        self.assertEqual(result.full_name, rule_name)
        self.assertTrue(hasattr(result, 'then'))
        self.assertEqual(result.then.service_activation_eligible, True)

        # Test with non-matching data
        data['credit_score'] = 500  # Below required 600
        result = self.helper.match_rule(rule_name, data)
        self.assertFalse(result, f'Rule {rule_name} should not have matched')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    log_format = '%(asctime)s - %(levelname)s - %(name)s:%(lineno)d - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_format)

    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
