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

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

class TestMatchSpecialOperators(unittest.TestCase):
    """ Tests the comparators beyond plain equality and ordering.
    """
    def setUp(self) -> 'None':
        rules_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        self.helper = RuleTestHelper(rules_dir)

# ################################################################################################################################

    def test_regex_matching(self) -> 'None':
        """ The matches comparator applies a regex to its subject.
        """
        data = {'doc_id': 'AAABBB 123', 'transaction_type': 'purchase'}
        result = self.helper.match_rule('special_operators_01_Special_Regex_Test', data)
        self.assertTrue(result)
        self.assertEqual(result.then['result'], 'matched_regex')

        data = {'doc_id': 'AAABBB', 'transaction_type': 'purchase'}
        result = self.helper.match_rule('special_operators_01_Special_Regex_Test', data)
        self.assertFalse(result)

# ################################################################################################################################

    def test_between_boundaries(self) -> 'None':
        """ The is between comparator includes both boundaries.
        """

        # Both boundaries are inclusive ..
        for amount in (100, 500, 1000):
            data = {'transaction_amount': amount, 'transaction_type': 'purchase'}
            result = self.helper.match_rule('special_operators_02_Special_Between_Test', data)
            self.assertTrue(result, f'Amount {amount} should be inside the range')

        # .. and values outside the range do not match.
        for amount in (99, 1001):
            data = {'transaction_amount': amount, 'transaction_type': 'purchase'}
            result = self.helper.match_rule('special_operators_02_Special_Between_Test', data)
            self.assertFalse(result, f'Amount {amount} should be outside the range')

# ################################################################################################################################

    def test_collection_membership(self) -> 'None':
        """ The is one of comparator checks membership in a defaults-provided list.
        """
        data = {'critical_infrastructure_involved': 'power_plant', 'incident_severity': 7}
        result = self.helper.match_rule('special_operators_03_Special_Collection_Membership_Test', data)
        self.assertTrue(result)
        self.assertListEqual(result.then['response_units'], ['fire', 'hazmat'])

        data = {'critical_infrastructure_involved': 'warehouse', 'incident_severity': 7}
        result = self.helper.match_rule('special_operators_03_Special_Collection_Membership_Test', data)
        self.assertFalse(result)

# ################################################################################################################################

    def test_negated_membership(self) -> 'None':
        """ The is not one of comparator matches values outside the list.
        """
        data = {'channel': 'email', 'priority': 1}
        result = self.helper.match_rule('parser_Routing_004', data)
        self.assertTrue(result)

        data = {'channel': 'pager', 'priority': 1}
        result = self.helper.match_rule('parser_Routing_004', data)
        self.assertFalse(result)

# ################################################################################################################################

    def test_boolean_comparators(self) -> 'None':
        """ The is true and is false comparators check boolean fields without literals.
        """
        data = {'premium_services_enrolled': True, 'account_suspended': False, 'amount': 2000}
        result = self.helper.match_rule('special_operators_04_Special_Boolean_Test', data)
        self.assertTrue(result)
        self.assertEqual(result.then['priority'], 'high')

        # A suspended account breaks the is false condition.
        data = {'premium_services_enrolled': True, 'account_suspended': True, 'amount': 2000}
        result = self.helper.match_rule('special_operators_04_Special_Boolean_Test', data)
        self.assertFalse(result)

# ################################################################################################################################

    def test_field_to_field_comparison(self) -> 'None':
        """ A bare term on the right side compares two input fields with each other.
        """
        data = self._telco_data()
        result = self.helper.match_rule('parser_TELCO_002', data)
        self.assertTrue(result)

        # Equal transaction and customer types break the is not condition.
        data = self._telco_data()
        data['customer_type'] = data['transaction_type']
        result = self.helper.match_rule('parser_TELCO_002', data)
        self.assertFalse(result)

# ################################################################################################################################

    def test_reference_resolution_in_then(self) -> 'None':
        """ A reference in a then action resolves against the input data.
        """
        data = self._telco_data()
        data['channel'] = 'push_notification'

        result = self.helper.match_rule('parser_TELCO_002', data)
        self.assertTrue(result)

        # The list holds one literal and one resolved reference.
        self.assertListEqual(result.then['outbound_channel'], ['sms', 'push_notification'])
        self.assertListEqual(result.then['notification_channel'], ['email', 'app_alert'])

# ################################################################################################################################

    def _telco_data(self) -> 'anydict':
        out = {
            'transaction_type': 'purchase',
            'customer_type': 'retail',
            'transaction_amount': 6000,
            'transaction_category': 'fixed',
            'title': 'QBC',
            'doc_id': 'AAABBB 123',
            'abc': datetime(2025, 1, 1),
            'hello': 123,
        }
        return out

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
