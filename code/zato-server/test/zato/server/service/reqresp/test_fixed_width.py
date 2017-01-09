# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from unittest import TestCase

# Zato
from zato.server.service import fixed_width
from zato.server.service.reqresp.fixed_width import FixedWidth

String = fixed_width.String

class TestParser(TestCase):

    def compare_line(self, expected, actual):
        for expected_line in expected:
            expected_key = expected_line['key']
            expected_value = expected_line['value']
            actual_value = getattr(actual, expected_key)
            self.assertEquals(expected_value, actual_value)

    def test_parse_line_string_only(self):

        data = 'abbcccdddd\nABBCCCDDDD'
        a = String(1, 'a')
        b = String(2, 'b')
        c = String(3, 'c')
        d = String(4, 'd')
        definition = (a, b, c, d)

        expected1 = [
            {'key':'a', 'value':'a'},
            {'key':'b', 'value':'bb'},
            {'key':'c', 'value':'ccc'},
            {'key':'d', 'value':'dddd'},
        ]

        expected2 = [
            {'key':'a', 'value':'A'},
            {'key':'b', 'value':'BB'},
            {'key':'c', 'value':'CCC'},
            {'key':'d', 'value':'DDDD'},
        ]

        fw = FixedWidth(data, definition)
        elems = list(fw)

        actual1 = elems[0]
        actual2 = elems[1]

        self.compare_line(expected1, actual1)
        self.compare_line(expected2, actual2)
