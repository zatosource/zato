# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import unittest
from pathlib import Path

# Zato
from zato.common.test.rules import RuleTestHelper

# ################################################################################################################################
# ################################################################################################################################

class TestMatchRegex(unittest.TestCase):
    """ Tests regex matching in rule conditions.
    """
    def setUp(self) -> 'None':
        # The shared zrules fixtures live one level up, next to the test subdirectories.
        rules_dir = Path(os.path.dirname(os.path.abspath(__file__))).parent
        self.helper = RuleTestHelper(rules_dir)

# ################################################################################################################################

    def test_basic_pattern(self) -> 'None':
        """ The matches comparator applies its regex pattern to the subject.
        """
        data = {'doc_id': 'AAABBB 123', 'transaction_type': 'purchase'}
        result = self.helper.match_rule('regex_01_Regex_Basic_Test', data)
        self.assertTrue(result)
        self.assertEqual(result.then['result'], 'matched_basic_regex')

        data = {'doc_id': 'CCCDDD 123', 'transaction_type': 'purchase'}
        result = self.helper.match_rule('regex_01_Regex_Basic_Test', data)
        self.assertFalse(result)

# ################################################################################################################################

    def test_digit_pattern_via_alias(self) -> 'None':
        """ The =~ alias parses and matches digit group patterns.
        """
        data = {'account_number': '1234-5678-9012-3456', 'transaction_type': 'purchase'}
        result = self.helper.match_rule('regex_02_Regex_Digit_Test', data)
        self.assertTrue(result)
        self.assertEqual(result.then['result'], 'matched_digit_regex')

        data = {'account_number': '1234-5678', 'transaction_type': 'purchase'}
        result = self.helper.match_rule('regex_02_Regex_Digit_Test', data)
        self.assertFalse(result)

# ################################################################################################################################

    def test_email_pattern(self) -> 'None':
        """ Character class patterns match email-shaped input.
        """
        data = {'email': 'first.last@example.com', 'notification_enabled': True}
        result = self.helper.match_rule('regex_03_Regex_Email_Test', data)
        self.assertTrue(result)
        self.assertEqual(result.then['result'], 'matched_email_regex')

        data = {'email': 'not-an-email', 'notification_enabled': True}
        result = self.helper.match_rule('regex_03_Regex_Email_Test', data)
        self.assertFalse(result)

# ################################################################################################################################

    def test_regex_combined_with_other_conditions(self) -> 'None':
        """ A regex condition combines with plain comparisons through and.
        """
        data = {'doc_id': 'AAABBB 123', 'transaction_type': 'purchase', 'transaction_amount': 600}
        result = self.helper.match_rule('regex_04_Regex_Combined_Test', data)
        self.assertTrue(result)
        self.assertEqual(result.then['result'], 'matched_combined_regex')

        # The regex holds but the amount is too low.
        data = {'doc_id': 'AAABBB 123', 'transaction_type': 'purchase', 'transaction_amount': 400}
        result = self.helper.match_rule('regex_04_Regex_Combined_Test', data)
        self.assertFalse(result)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
