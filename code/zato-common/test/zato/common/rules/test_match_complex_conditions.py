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

class TestMatchComplexConditions(unittest.TestCase):
    """ Tests conditions that combine several comparator kinds within one rule.
    """
    def setUp(self) -> 'None':
        rules_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        self.helper = RuleTestHelper(rules_dir)

# ################################################################################################################################

    def test_all_comparator_kinds_in_one_rule(self) -> 'None':
        """ Field-to-field, default references, membership, regex, dates and equality all hold together.
        """
        data = {
            'transaction_type': 'purchase',
            'customer_type': 'retail',
            'transaction_amount': 6000,
            'transaction_category': 'variable',
            'title': 'QBC',
            'doc_id': 'AAABBB 123',
            'abc': datetime(2025, 1, 1),
            'hello': 123,
        }
        result = self.helper.match_rule('parser_TELCO_002', data)
        self.assertTrue(result)
        self.assertEqual(result.then['score'], 85)
        self.assertEqual(result.then['block_transaction'], True)

# ################################################################################################################################

    def test_each_condition_can_break_the_match(self) -> 'None':
        """ Whichever single condition fails, the whole and-chain fails with it.
        """
        base = {
            'transaction_type': 'purchase',
            'customer_type': 'retail',
            'transaction_amount': 6000,
            'transaction_category': 'fixed',
            'title': 'QBC',
            'doc_id': 'AAABBB 123',
            'abc': datetime(2025, 1, 1),
            'hello': 123,
        }

        # Each override below breaks exactly one condition.
        overrides = {
            'customer_type': 'purchase',
            'transaction_amount': 100,
            'transaction_category': 'recurring',
            'title': 'XYZ',
            'doc_id': 'CCCDDD 123',
            'abc': datetime(2024, 6, 1),
            'hello': 456,
        }

        for key, value in overrides.items():
            data = dict(base)
            data[key] = value

            result = self.helper.match_rule('parser_TELCO_002', data)
            self.assertFalse(result, f'Overriding {key} should have broken the match')

# ################################################################################################################################

    def test_date_comparison(self) -> 'None':
        """ A datetime literal compares against real datetime input values.
        """
        data = {
            'transaction_type': 'purchase',
            'customer_type': 'retail',
            'transaction_amount': 6000,
            'transaction_category': 'fixed',
            'title': 'QBC',
            'doc_id': 'AAABBB 123',
            'abc': datetime(2025, 1, 1, 0, 0, 0),
            'hello': 123,
        }
        result = self.helper.match_rule('parser_TELCO_002', data)
        self.assertTrue(result)

        # A different timestamp does not equal the literal.
        data['abc'] = datetime(2025, 1, 1, 0, 0, 1)
        result = self.helper.match_rule('parser_TELCO_002', data)
        self.assertFalse(result)

# ################################################################################################################################

    def test_between_combined_with_or(self) -> 'None':
        """ An is between condition takes part in an or-chain like any other condition.
        """

        # The defect count inside the range matches through the middle or-branch.
        data = {
            'dimensional_deviation': 1,
            'tolerance_threshold': 5,
            'surface_defect_count': 5,
            'material_strength': 100,
            'minimum_strength_requirement': 50,
        }
        result = self.helper.match_rule('exec_04_Manufacturing_QualityControl_Rejection', data)
        self.assertTrue(result)
        self.assertEqual(result.then['product_status'], 'rejected')

        # A defect count outside the range, with everything else healthy, does not match.
        data['surface_defect_count'] = 2
        result = self.helper.match_rule('exec_04_Manufacturing_QualityControl_Rejection', data)
        self.assertFalse(result)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
