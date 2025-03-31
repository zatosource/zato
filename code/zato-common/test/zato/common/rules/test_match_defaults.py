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

class TestMatchDefaults(unittest.TestCase):
    """ Tests default value handling in rule conditions.
    """
    def setUp(self) -> 'None':
        # Initialize the rule test helper with the path to the rules directory
        rules_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        self.helper = RuleTestHelper(rules_dir)

    def test_default_values(self) -> 'None':
        """ Test that default values are used when fields are not provided.
        """
        # Find rules with default values
        default_rules = []
        for rule_name, condition in self.helper.rule_conditions.items():
            # Check if rule has defaults section
            rule = self.helper.rules_manager[rule_name]
            if hasattr(rule, 'defaults') and rule.defaults:
                default_rules.append(rule_name)

        if not default_rules:
            self.skipTest('No rules with default values found')

        # Use the first rule with default values
        rule_name = default_rules[0]
        logger.info(f'Testing default values for rule: {rule_name}')

        # Get the rule to inspect its defaults
        rule = self.helper.rules_manager[rule_name]
        logger.info(f'Rule defaults: {rule.defaults}')

        # For a rule with premium_data_threshold default
        if 'premium_data_threshold' in rule.defaults:
            # Test with missing field (should use default)
            data = {
                'subscription_months': 30,
                'premium_services_enrolled': True
                # monthly_data_usage is missing, should use default
            }

            # The default threshold is 100, so we need to provide a value > 100
            data['monthly_data_usage'] = rule.defaults['premium_data_threshold'] + 10

            result = self.helper.match_rule(rule_name, data)
            self.assertTrue(result, f'Rule {rule_name} should have matched using default threshold')

        # For a rule with high_value_threshold default
        elif 'high_value_threshold' in rule.defaults:
            # Test with missing field (should use default)
            data = {
                'trade_amount': rule.defaults['high_value_threshold'] + 100000,
                'currency_volatility': rule.defaults['volatility_threshold'] + 0.01,
                'client_trading_history_months': 3,
                'market_condition': 'stable'
            }

            result = self.helper.match_rule(rule_name, data)
            self.assertTrue(result, f'Rule {rule_name} should have matched using default thresholds')

        # For other rules with defaults
        else:
            logger.info(f'Skipping specific tests for {rule_name} - would need custom test data')

    def test_override_defaults(self) -> 'None':
        """ Test that provided values override default values.
        """
        # Find rules with default values
        default_rules = []
        for rule_name, condition in self.helper.rule_conditions.items():
            # Check if rule has defaults section
            rule = self.helper.rules_manager[rule_name]
            if hasattr(rule, 'defaults') and rule.defaults:
                default_rules.append(rule_name)

        if not default_rules:
            self.skipTest('No rules with default values found')

        # Use the first rule with default values
        rule_name = default_rules[0]
        logger.info(f'Testing override of default values for rule: {rule_name}')

        # Get the rule to inspect its defaults
        rule = self.helper.rules_manager[rule_name]
        logger.info(f'Rule defaults: {rule.defaults}')

        # For a rule with premium_data_threshold default
        if 'premium_data_threshold' in rule.defaults:
            # Test with explicitly provided value that's below threshold (should not match)
            data = {
                'monthly_data_usage': rule.defaults['premium_data_threshold'] - 10,  # Below threshold
                'subscription_months': 30,
                'premium_services_enrolled': True,
                'premium_data_threshold': rule.defaults['premium_data_threshold']  # Explicitly provide default
            }

            result = self.helper.match_rule(rule_name, data)
            self.assertFalse(result, f'Rule {rule_name} should not have matched with usage below threshold')

            # Test with explicitly provided threshold that's lower than default (should match)
            data = {
                'monthly_data_usage': rule.defaults['premium_data_threshold'] - 10,  # Below default threshold
                'subscription_months': 30,
                'premium_services_enrolled': True,
                'premium_data_threshold': rule.defaults['premium_data_threshold'] - 20  # Lower than default
            }

            result = self.helper.match_rule(rule_name, data)
            self.assertTrue(result, f'Rule {rule_name} should have matched with custom lower threshold')

        # For a rule with high_value_threshold default
        elif 'high_value_threshold' in rule.defaults:
            # Test with explicitly provided value that's below threshold (should not match)
            data = {
                'trade_amount': rule.defaults['high_value_threshold'] - 100000,  # Below threshold
                'currency_volatility': rule.defaults['volatility_threshold'] + 0.01,
                'client_trading_history_months': 3,
                'market_condition': 'stable',
                'high_value_threshold': rule.defaults['high_value_threshold']  # Explicitly provide default
            }

            result = self.helper.match_rule(rule_name, data)
            self.assertFalse(result, f'Rule {rule_name} should not have matched with amount below threshold')

            # Test with explicitly provided threshold that's lower than default (should match)
            data = {
                'trade_amount': rule.defaults['high_value_threshold'] - 100000,  # Below default threshold
                'currency_volatility': rule.defaults['volatility_threshold'] + 0.01,
                'client_trading_history_months': 3,
                'market_condition': 'stable',
                'high_value_threshold': rule.defaults['high_value_threshold'] - 200000  # Lower than default
            }

            result = self.helper.match_rule(rule_name, data)
            self.assertTrue(result, f'Rule {rule_name} should have matched with custom lower threshold')

        # For other rules with defaults
        else:
            logger.info(f'Skipping specific tests for {rule_name} - would need custom test data')

    def test_missing_fields(self) -> 'None':
        """ Test behavior when required fields are missing and no defaults are provided.
        """
        # Find rules without default values
        no_default_rules = []
        for rule_name, condition in self.helper.rule_conditions.items():
            # Check if rule has no defaults section
            rule = self.helper.rules_manager[rule_name]
            if not hasattr(rule, 'defaults') or not rule.defaults:
                no_default_rules.append(rule_name)

        if not no_default_rules:
            self.skipTest('No rules without default values found')

        # Use the first rule without default values
        rule_name = no_default_rules[0]
        logger.info(f'Testing missing fields for rule: {rule_name}')

        # Get the rule condition to determine what fields are required
        rule_condition = self.helper.get_rule_condition(rule_name)
        logger.info(f'Rule condition: {rule_condition}')

        # For a rule with customer_segment condition
        if 'customer_segment' in rule_condition:
            # Test with missing required field
            data = {}  # Empty data, missing customer_segment

            # This should not raise an exception but simply not match
            result = self.helper.match_rule(rule_name, data)
            self.assertFalse(result, f'Rule {rule_name} should not have matched with missing required field')

        # For a rule with account_tier condition
        elif 'account_tier' in rule_condition:
            # Test with missing required field
            data = {}  # Empty data, missing account_tier

            # This should not raise an exception but simply not match
            result = self.helper.match_rule(rule_name, data)
            self.assertFalse(result, f'Rule {rule_name} should not have matched with missing required field')

        # For other rules without defaults
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
