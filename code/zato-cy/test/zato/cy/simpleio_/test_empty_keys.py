# -*- coding: utf-8 -*-

"""
Copyright (C) 2020, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.common.test import BaseSIOTestCase, test_class_name

# ################################################################################################################################
# ################################################################################################################################

class SkipEmptyTestCase(BaseSIOTestCase):

    def test_raw_skip_and_class_not_allowed(self):

        class SimpleIO:
            skip_empty_keys = True

            class SkipEmpty:
                pass

        with self.assertRaises(ValueError) as ctx:
            self.get_sio(SimpleIO, test_class_name)

        e = ctx.exception # type: ValueError
        self.assertEqual(e.args[0], 'Cannot specify both skip_empty_input and SkipEmpty in a SimpleIO definition')

# ################################################################################################################################

    def test_raw_skip_one_string(self):

        class SimpleIO:
            input = 'abc'
            skip_empty_keys = 'abc'

        result = self.get_sio(SimpleIO, test_class_name)

        # The single string should be converted to a set
        self.assertTrue(isinstance(result.definition.skip_empty.skip_input_set, set))
        self.assertEqual(list(result.definition.skip_empty.skip_output_set), ['abc'])

        # This should be False because skip_empty_keys deals with responses, not requests
        self.assertFalse(result.definition.skip_empty.skip_all_empty_input)

# ################################################################################################################################

    def test_raw_skip_tuple(self):

        class SimpleIO:
            input = 'abc', 'def'
            skip_empty_keys = 'def', 'abc'

        result = self.get_sio(SimpleIO, test_class_name)

        self.assertTrue(isinstance(result.definition.skip_empty.skip_input_set, set))
        self.assertEqual(sorted(result.definition.skip_empty.skip_output_set), ['abc', 'def'])

        # This should be False as we gave a tuple on input, rather than True
        self.assertFalse(result.definition.skip_empty.skip_all_empty_input)

# ################################################################################################################################

    def test_raw_skip_bool_input_true(self):

        class SimpleIO:
            skip_empty_keys = True

        result = self.get_sio(SimpleIO, test_class_name)

        self.assertTrue(isinstance(result.definition.skip_empty.skip_input_set, set))
        self.assertEqual(list(result.definition.skip_empty.skip_input_set), [])
        self.assertFalse(result.definition.skip_empty.skip_all_empty_input)

        # This should be False if only skip_empty_keys is used, no matter if skip_empty_keys is True or False
        self.assertTrue(result.definition.skip_empty.skip_all_empty_output)

# ################################################################################################################################

    def test_raw_skip_bool_input_false(self):

        class SimpleIO:
            skip_empty_keys = False

        result = self.get_sio(SimpleIO, test_class_name)

        self.assertTrue(isinstance(result.definition.skip_empty.skip_input_set, set))
        self.assertEqual(list(result.definition.skip_empty.skip_input_set), [])
        self.assertFalse(result.definition.skip_empty.skip_all_empty_input)

        # This should be False if only skip_empty_keys is used, no matter if skip_empty_keys is True or False
        self.assertFalse(result.definition.skip_empty.skip_all_empty_output)

# ################################################################################################################################

    def test_raw_force_empty_keys_true(self):

        class SimpleIO:
            force_empty_keys = True

        result = self.get_sio(SimpleIO, test_class_name)
        self.assertTrue(result.has_bool_force_empty_keys)
        self.assertEqual(list(result.definition.skip_empty.skip_output_set), [])
        self.assertEqual(list(result.definition.skip_empty.force_empty_output_set), [])
        self.assertFalse(result.definition.skip_empty.skip_all_empty_output)

# ################################################################################################################################

    def test_raw_force_empty_keys_false(self):

        class SimpleIO:
            force_empty_keys = False

        result = self.get_sio(SimpleIO, test_class_name)
        self.assertTrue(result.has_bool_force_empty_keys)
        self.assertEqual(list(result.definition.skip_empty.skip_output_set), [])
        self.assertEqual(list(result.definition.skip_empty.force_empty_output_set), [])
        self.assertFalse(result.definition.skip_empty.skip_all_empty_output)

# ################################################################################################################################

    def test_raw_force_empty_keys_not_provided(self):

        class SimpleIO:
            # Commented out on purpose to signal that we do not want to provide it
            # force_empty_keys = True
            pass

        result = self.get_sio(SimpleIO, test_class_name)
        self.assertFalse(result.has_bool_force_empty_keys)
        self.assertEqual(list(result.definition.skip_empty.skip_output_set), [])
        self.assertEqual(list(result.definition.skip_empty.force_empty_output_set), [])
        self.assertFalse(result.definition.skip_empty.skip_all_empty_output)

# ################################################################################################################################
# ################################################################################################################################
