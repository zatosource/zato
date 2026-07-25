# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest

# Zato
from zato.common.util.channel import Channel_URL_Path_Max_Length, validate_channel_url_path

# ################################################################################################################################
# ################################################################################################################################

class ValidateChannelURLPathTestCase(unittest.TestCase):
    """ Tests for what a channel's URL path is allowed to be.
    """

# ################################################################################################################################

    def test_a_plain_path_is_accepted(self) -> 'None':
        validate_channel_url_path('/api/invoice')

# ################################################################################################################################

    def test_a_path_with_parameters_is_accepted(self) -> 'None':
        validate_channel_url_path('/api/invoice/{invoice_id}/line/{line_id}')

# ################################################################################################################################

    def test_a_path_needs_a_leading_slash(self) -> 'None':
        with self.assertRaises(Exception) as context:
            validate_channel_url_path('api/invoice')

        self.assertIn('start with a slash', str(context.exception))

# ################################################################################################################################

    def test_a_path_cannot_exceed_the_length_limit(self) -> 'None':
        url_path = '/' + 'a' * Channel_URL_Path_Max_Length

        with self.assertRaises(Exception) as context:
            validate_channel_url_path(url_path)

        self.assertIn('characters', str(context.exception))

# ################################################################################################################################

    def test_a_path_cannot_carry_the_target_separator(self) -> 'None':
        with self.assertRaises(Exception) as context:
            validate_channel_url_path('/api/:::/invoice')

        self.assertIn(':::', str(context.exception))

# ################################################################################################################################

    def test_a_parameter_name_cannot_be_used_twice(self) -> 'None':
        with self.assertRaises(Exception) as context:
            validate_channel_url_path('/api/{invoice_id}/line/{invoice_id}')

        self.assertIn('more than once', str(context.exception))

# ################################################################################################################################

    def test_two_parameters_need_something_between_them(self) -> 'None':
        with self.assertRaises(Exception) as context:
            validate_channel_url_path('/api/{first}{second}')

        self.assertIn('between them', str(context.exception))

# ################################################################################################################################

    def test_a_parameter_needs_a_name(self) -> 'None':
        with self.assertRaises(Exception) as context:
            validate_channel_url_path('/api/{}')

        self.assertIn('no name', str(context.exception))

# ################################################################################################################################

    def test_a_parameter_has_to_be_closed(self) -> 'None':
        with self.assertRaises(Exception) as context:
            validate_channel_url_path('/api/{invoice_id')

        self.assertIn('never closed', str(context.exception))

# ################################################################################################################################

    def test_a_closing_brace_needs_an_opening_one(self) -> 'None':
        with self.assertRaises(Exception) as context:
            validate_channel_url_path('/api/invoice_id}')

        self.assertIn('never opened', str(context.exception))

# ################################################################################################################################

    def test_a_closing_brace_in_front_of_a_parameter_is_rejected_too(self) -> 'None':
        with self.assertRaises(Exception) as context:
            validate_channel_url_path('/api/}/{invoice_id}')

        self.assertIn('never opened', str(context.exception))

# ################################################################################################################################

    def test_parameters_cannot_be_nested(self) -> 'None':
        with self.assertRaises(Exception) as context:
            validate_channel_url_path('/api/{invoice{id}}')

        self.assertIn('nest', str(context.exception))

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
