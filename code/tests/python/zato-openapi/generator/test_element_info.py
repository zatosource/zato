# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main, TestCase

# Zato
from zato.input_output import Bool, Int, Text
from zato.openapi.generator.io_scanner import get_element_info

# ################################################################################################################################
# ################################################################################################################################

class ElementInfoTestCase(TestCase):
    """ Flat input and output elements are documented with the types that the server gives them.
    """

    def test_a_flag_name_is_a_boolean(self) -> 'None':
        self.assertEqual(get_element_info('is_active'), {'name': 'is_active', 'required': True, 'schema_type': 'boolean'})

    def test_a_count_name_is_an_integer(self) -> 'None':
        self.assertEqual(get_element_info('-order_count'), {'name': 'order_count', 'required': False, 'schema_type': 'integer'})

    def test_any_other_name_is_a_string(self) -> 'None':
        self.assertEqual(get_element_info('name'), {'name': 'name', 'required': True, 'schema_type': 'string'})

    def test_an_optional_flag(self) -> 'None':
        self.assertEqual(get_element_info('-has_items'), {'name': 'has_items', 'required': False, 'schema_type': 'boolean'})

    def test_an_int_element(self) -> 'None':
        self.assertEqual(get_element_info(Int('total')), {'name': 'total', 'required': True, 'schema_type': 'integer'})

    def test_a_bool_element(self) -> 'None':
        self.assertEqual(get_element_info(Bool('enabled')), {'name': 'enabled', 'required': True, 'schema_type': 'boolean'})

    def test_a_text_element_whose_name_implies_a_count(self) -> 'None':
        self.assertEqual(get_element_info(Text('order_count')), {'name': 'order_count', 'required': True, 'schema_type': 'string'})

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
