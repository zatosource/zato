# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.typing_ import anydict
from zato.common.util.truncate.common import Array_Element_Floor, Kind_Array_Tail, Kind_String_Cut, Min_String_Length, \
    Truncation_Marker
from zato.common.util.truncate.degrade import cut_string, drop_array_tails, shorten_strings
from zato.common.util.truncate.measure import get_size
from zato.common.util.truncate.walker import collect_candidates

# ################################################################################################################################
# ################################################################################################################################

class TestCutString:

    def test_cut_lands_on_a_whitespace_boundary(self) -> 'None':

        value = 'alpha bravo charlie delta echo foxtrot'
        result = cut_string(value, 20)

        assert result == 'alpha bravo charlie ' + Truncation_Marker

    def test_trailing_digit_tokens_are_dropped_whole(self) -> 'None':

        # The cut point lands inside the account number, so every digit-bearing group before it goes too.
        value = 'send the payment to ES91 2100 0418 4502 0005 1332 by Friday'
        result = cut_string(value, 30)

        assert result == 'send the payment to ' + Truncation_Marker

    def test_token_without_digits_survives_the_trim(self) -> 'None':

        value = 'first second third fourth fifth'
        result = cut_string(value, 25)

        assert result == 'first second third fourth ' + Truncation_Marker

    def test_no_whitespace_leaves_only_the_marker(self) -> 'None':

        # A single unbroken token cannot be cut in half, so it disappears entirely.
        value = 'a' * 1000
        result = cut_string(value, 500)

        assert result == Truncation_Marker

    def test_all_digit_tokens_leave_only_the_marker(self) -> 'None':

        value = '1111 2222 3333 4444 5555 6666'
        result = cut_string(value, 15)

        assert result == Truncation_Marker

    def test_zero_keep_length_leaves_only_the_marker(self) -> 'None':

        value = 'alpha bravo charlie'
        result = cut_string(value, 0)

        assert result == Truncation_Marker

# ################################################################################################################################
# ################################################################################################################################

def _make_entries() -> 'anydict':
    out = {}
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestDropArrayTails:

    def test_longest_array_loses_elements_first(self) -> 'None':

        document = {'long': [1, 2, 3, 4, 5, 6], 'short': [7, 8]}
        walk = collect_candidates(document)
        entries = _make_entries()

        current = get_size(document)
        target = current - 4

        returned = drop_array_tails(walk.arrays, current, target, entries)

        # Two drops from the longest array were enough - the short one is untouched.
        assert document['long'] == [1, 2, 3, 4]
        assert document['short'] == [7, 8]
        assert returned <= target

    def test_arithmetic_matches_reality(self) -> 'None':

        document = {'rows': [{'id': 'inv-0001', 'note': 'A note with "quotes" and Góra'}] * 10}
        walk = collect_candidates(document)
        entries = _make_entries()

        current = get_size(document)
        target = current // 2

        returned = drop_array_tails(walk.arrays, current, target, entries)

        # The running size the loop maintained is exactly the size the document now has.
        assert returned == get_size(document)

    def test_entries_accumulate_per_path(self) -> 'None':

        document = {'rows': [1, 2, 3, 4, 5]}
        walk = collect_candidates(document)
        entries = _make_entries()

        current = get_size(document)
        returned = drop_array_tails(walk.arrays, current, 2, entries)

        entry = entries['$.rows']

        assert entry.kind == Kind_Array_Tail
        assert entry.count == 4
        assert entry.total == 5
        assert entry.size == current - returned

    def test_the_floor_is_never_crossed(self) -> 'None':

        document = {'rows': [1, 2, 3, 4, 5]}
        walk = collect_candidates(document)
        entries = _make_entries()

        # A target of zero can never be reached - the loop must stop at the floor instead.
        current = get_size(document)
        _ = drop_array_tails(walk.arrays, current, 0, entries)

        assert len(document['rows']) == Array_Element_Floor

    def test_no_candidates_is_a_no_op(self) -> 'None':

        entries = _make_entries()
        returned = drop_array_tails([], 1000, 10, entries)

        assert returned == 1000
        assert entries == {}

    def test_target_already_met_is_a_no_op(self) -> 'None':

        document = {'rows': [1, 2, 3]}
        walk = collect_candidates(document)
        entries = _make_entries()

        returned = drop_array_tails(walk.arrays, 50, 100, entries)

        assert returned == 50
        assert document['rows'] == [1, 2, 3]

# ################################################################################################################################
# ################################################################################################################################

class TestShortenStrings:

    def test_longest_string_is_cut_first(self) -> 'None':

        long_text = 'many words separated by spaces here ' * 40
        short_text = 'still above the floor but shorter ' * 9

        document = {'long': long_text, 'short': short_text}
        walk = collect_candidates(document)
        entries = _make_entries()

        current = get_size(document)
        target = current - 100

        _ = shorten_strings(walk.strings, current, target, entries)

        assert document['long'].endswith(Truncation_Marker)
        assert document['short'] == short_text

    def test_arithmetic_matches_reality(self) -> 'None':

        document = {
            'first': 'words with "escaped quotes" inside them repeated over and over ' * 30,
            'second': 'Zielona Góra and more non-ASCII płótno every few words ' * 30,
        }
        walk = collect_candidates(document)
        entries = _make_entries()

        current = get_size(document)
        target = current // 3

        returned = shorten_strings(walk.strings, current, target, entries)

        assert returned == get_size(document)

    def test_entries_accumulate_per_path(self) -> 'None':

        long_text = 'many words separated by spaces here ' * 100
        document = {'body': long_text}
        walk = collect_candidates(document)
        entries = _make_entries()

        # A target low enough that the same string must be halved more than once.
        current = get_size(document)
        target = current // 4

        returned = shorten_strings(walk.strings, current, target, entries)

        entry = entries['$.body']

        assert entry.kind == Kind_String_Cut
        assert entry.chars == len(long_text) - len(document['body'])
        assert entry.size == current - returned

    def test_the_floor_is_respected(self) -> 'None':

        long_text = 'many words separated by spaces here ' * 100
        document = {'body': long_text}
        walk = collect_candidates(document)
        entries = _make_entries()

        # An unreachable target - the loop must stop once the string is at or below the floor.
        current = get_size(document)
        _ = shorten_strings(walk.strings, current, 0, entries)

        assert len(document['body']) <= Min_String_Length + len(Truncation_Marker) + 1

    def test_unprofitable_cut_is_skipped(self) -> 'None':

        # A string just above the floor made of short words - the cut keeps nearly everything
        # and adds the marker on top, making the value longer, so it is skipped.
        value = ('word ' * 60)[:Min_String_Length + 1]
        document = {'body': value}
        walk = collect_candidates(document)
        entries = _make_entries()

        current = get_size(document)
        returned = shorten_strings(walk.strings, current, 0, entries)

        assert document['body'] == value
        assert returned == current
        assert entries == {}

    def test_short_kept_prefix_retires_the_candidate(self) -> 'None':

        # Whitespace exists only near the start, so the cut keeps a prefix well below the floor
        # and the string leaves the ranking after a single cut.
        value = 'alpha bravo ' + 'x' * 600
        document = {'body': value}
        walk = collect_candidates(document)
        entries = _make_entries()

        current = get_size(document)
        _ = shorten_strings(walk.strings, current, 0, entries)

        assert document['body'] == 'alpha bravo ' + Truncation_Marker

    def test_no_candidates_is_a_no_op(self) -> 'None':

        entries = _make_entries()
        returned = shorten_strings([], 1000, 10, entries)

        assert returned == 1000
        assert entries == {}

# ################################################################################################################################
# ################################################################################################################################
