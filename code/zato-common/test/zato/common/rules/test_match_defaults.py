# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import unittest
from datetime import datetime
from pathlib import Path

# Zato
from zato.common.test.rules import RuleTestHelper

# ################################################################################################################################
# ################################################################################################################################

class TestMatchDefaults(unittest.TestCase):
    """ Tests default value handling in rule conditions.
    """
    def setUp(self) -> 'None':
        rules_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        self.helper = RuleTestHelper(rules_dir)

# ################################################################################################################################

    def test_default_values_used_when_missing(self) -> 'None':
        """ A missing input field is filled in from the rule's defaults.
        """

        # The thresholds come from the defaults - 100 for data usage, 24 for loyalty months ..
        data = {
            'monthly_data_usage': 150,
            'subscription_months': 30,
            'premium_services_enrolled': True,
        }
        result = self.helper.match_rule('exec_01_BSS_PremiumTier_Assignment', data)
        self.assertTrue(result)
        self.assertEqual(result.then['billing_tier'], 'Premium')

        # .. and usage below the default threshold does not match.
        data = {
            'monthly_data_usage': 90,
            'subscription_months': 30,
            'premium_services_enrolled': True,
        }
        result = self.helper.match_rule('exec_01_BSS_PremiumTier_Assignment', data)
        self.assertFalse(result)

# ################################################################################################################################

    def test_provided_values_override_defaults(self) -> 'None':
        """ A value provided on input takes precedence over the same-named default.
        """

        # With the default threshold of 100, usage of 150 matches ..
        data = {
            'monthly_data_usage': 150,
            'subscription_months': 30,
            'premium_services_enrolled': True,
        }
        result = self.helper.match_rule('exec_01_BSS_PremiumTier_Assignment', data)
        self.assertTrue(result)

        # .. but an explicit higher threshold on input overrides the default and blocks the match.
        data = {
            'monthly_data_usage': 150,
            'premium_data_threshold': 200,
            'subscription_months': 30,
            'premium_services_enrolled': True,
        }
        result = self.helper.match_rule('exec_01_BSS_PremiumTier_Assignment', data)
        self.assertFalse(result)

# ################################################################################################################################

    def test_default_reference_in_condition(self) -> 'None':
        """ A default.x reference in a condition reads the default value.
        """

        # The default minimum transaction amount is 5000 ..
        data = {
            'transaction_type': 'purchase',
            'customer_type': 'retail',
            'transaction_amount': 6000,
            'transaction_category': 'fixed',
            'title': 'QBC',
            'doc_id': 'AAABBB 123',
            'abc': datetime(2025, 1, 1),
            'hello': 123,
            'channel': 'push',
        }
        result = self.helper.match_rule('parser_TELCO_002', data)
        self.assertTrue(result)

        # .. and an amount at the default boundary does not exceed it.
        data['transaction_amount'] = 5000
        result = self.helper.match_rule('parser_TELCO_002', data)
        self.assertFalse(result)

# ################################################################################################################################

    def test_default_list_in_membership(self) -> 'None':
        """ A default holding a list backs an is one of membership condition.
        """
        data = {'critical_infrastructure_involved': 'water_treatment', 'incident_severity': 6}
        result = self.helper.match_rule('special_operators_03_Special_Collection_Membership_Test', data)
        self.assertTrue(result)
        self.assertEqual(result.then['priority_level'], 'high')

        data = {'critical_infrastructure_involved': 'office_building', 'incident_severity': 6}
        result = self.helper.match_rule('special_operators_03_Special_Collection_Membership_Test', data)
        self.assertFalse(result)

# ################################################################################################################################

    def test_defaults_on_loaded_rule(self) -> 'None':
        """ Loaded rules expose their defaults as plain values.
        """
        rule = self.helper.rules_manager['exec_01_BSS_PremiumTier_Assignment']
        self.assertDictEqual(rule.defaults, {'premium_data_threshold': 100, 'loyalty_months_threshold': 24})

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
