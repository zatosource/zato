# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import loads

# Zato
from zato.common.util.truncate.measure import get_size, serialize

# ################################################################################################################################
# ################################################################################################################################

class TestSerialize:

    def test_compact_form(self) -> 'None':

        # No spaces after separators - the canonical form is compact.
        value = {'name': 'First invoice', 'items': [1, 2, 3]}
        serialized = serialize(value)

        assert serialized == '{"name":"First invoice","items":[1,2,3]}'

    def test_round_trip(self) -> 'None':

        value = {'nested': {'flag': True, 'empty': None, 'ratio': 0.5}}
        serialized = serialize(value)
        parsed = loads(serialized)

        assert parsed == value

    def test_non_ascii_is_not_escaped(self) -> 'None':

        # Non-ASCII characters stay as themselves, so sizes reflect UTF-8 bytes, not escape sequences.
        value = {'city': 'Zielona Góra'}
        serialized = serialize(value)

        assert 'Góra' in serialized

# ################################################################################################################################
# ################################################################################################################################

class TestGetSize:

    def test_ascii_size(self) -> 'None':

        # {"key":"value"} is 15 bytes.
        value = {'key': 'value'}
        size = get_size(value)

        assert size == 15

    def test_non_ascii_size_counts_utf8_bytes(self) -> 'None':

        # The letter ó takes two bytes in UTF-8, so the size is one more than the character count of the JSON text.
        value = 'Góra'
        serialized = serialize(value)
        size = get_size(value)

        assert size == len(serialized) + 1

    def test_escaped_quote_counts_both_bytes(self) -> 'None':

        # A double quote inside a string serializes as two characters.
        plain_size = get_size('abc')
        quoted_size = get_size('ab"')

        assert quoted_size == plain_size + 1

    def test_element_size_matches_in_container_size(self) -> 'None':

        # An element's standalone size plus one comma is exactly what it contributes inside an array -
        # this is what makes the trimming arithmetic exact.
        element = {'id': 'inv-0001', 'note': 'A note with "quotes" and Góra'}
        single = [element]
        double = [element, element]

        single_size = get_size(single)
        double_size = get_size(double)
        element_size = get_size(element)

        assert double_size == single_size + element_size + 1

# ################################################################################################################################
# ################################################################################################################################
