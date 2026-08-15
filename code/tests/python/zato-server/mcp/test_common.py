# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import sys
from unittest import TestCase

# Zato
from zato.server.connection.mcp.common import _max_embed_length, get_depth, printable

# ################################################################################################################################
# ################################################################################################################################

class Printable(TestCase):

    def test_a_plain_string_is_returned_unchanged(self) -> 'None':
        """ A short string of ordinary text renders as itself.
        """

        value = 'crm.get-customer'

        out = printable(value)
        self.assertEqual(out, value)

    def test_control_characters_become_spaces(self) -> 'None':
        """ CR, LF, tab and other control characters render as spaces,
        so the value always stays on one line.
        """

        value = 'first\r\nsecond\tthird\x00fourth\x85fifth'

        out = printable(value)
        self.assertEqual(out, 'first  second third fourth fifth')

    def test_a_non_string_value_renders_as_text(self) -> 'None':
        """ A number or a None renders as its text form.
        """

        self.assertEqual(printable(123), '123')
        self.assertEqual(printable(None), 'None')

    def test_a_value_past_the_bound_renders_as_its_length(self) -> 'None':
        """ A value longer than the embed bound is described by its length
        instead of being embedded.
        """

        over_length = _max_embed_length + 50
        value = 'a' * over_length

        out = printable(value)
        self.assertEqual(out, f'(value of {over_length} characters)')

# ################################################################################################################################
# ################################################################################################################################

class GetDepth(TestCase):

    def test_a_scalar_has_depth_zero(self) -> 'None':
        """ Strings, numbers, booleans and None nest nothing.
        """

        self.assertEqual(get_depth('customer'), 0)
        self.assertEqual(get_depth(123), 0)
        self.assertEqual(get_depth(None), 0)

    def test_an_empty_container_has_depth_one(self) -> 'None':
        """ An empty dict or list is one level of nesting.
        """

        self.assertEqual(get_depth({}), 1)
        self.assertEqual(get_depth([]), 1)

    def test_nested_containers_are_counted(self) -> 'None':
        """ Each container level adds one, whichever branch is the deepest.
        """

        value = {
            'shallow': 'customer',
            'deeper': {'orders': [{'order_id': 'abc-123'}]},
        }

        # The deepest branch is dict -> dict -> list -> dict
        self.assertEqual(get_depth(value), 4)

    def test_a_structure_past_the_recursion_limit_is_measured(self) -> 'None':
        """ Depth is measured iteratively, so a structure nested past the interpreter's
        recursion limit is measured rather than raising.
        """

        nesting = sys.getrecursionlimit() * 5

        value:'object' = 'bottom'

        for _ in range(nesting):
            value = [value]

        self.assertEqual(get_depth(value), nesting)

# ################################################################################################################################
# ################################################################################################################################
