# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.typing_ import any_, anylist
from zato.common.util.truncate.common import Max_Node_Count, Max_Recursion_Depth, Min_String_Length
from zato.common.util.truncate.walker import collect_candidates

# ################################################################################################################################
# ################################################################################################################################

_long_text = 'A long descriptive value that repeats itself. ' * 10

# ################################################################################################################################
# ################################################################################################################################

def _make_nested_lists(level_count:'int') -> 'anylist':
    """ Builds nested lists with the innermost, empty list at depth level_count - 1.
    """
    out:'anylist' = []

    for _ in range(level_count - 1):
        out = [out]

    return out

# ################################################################################################################################

def _make_nested_dicts(level_count:'int') -> 'any_':
    """ Builds nested dicts with the innermost, empty dict at depth level_count - 1.
    """
    out:'any_' = {}

    for _ in range(level_count - 1):
        out = {'level': out}

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestCollectCandidates:

    def test_arrays_and_strings_are_found_with_paths(self) -> 'None':

        document = {
            'rows': [1, 2, 3],
            'details': {'description': _long_text},
            'sections': [{'body': _long_text}, {'body': 'short'}],
        }

        result = collect_candidates(document)

        array_paths = []
        for candidate in result.arrays:
            array_paths.append(candidate.path)

        string_paths = []
        for candidate in result.strings:
            string_paths.append(candidate.path)

        assert array_paths == ['$.rows', '$.sections']
        assert string_paths == ['$.details.description', '$.sections[0].body']
        assert result.hit_node_cap is False
        assert result.hit_depth_cap is False

    def test_array_candidate_records_items_and_total(self) -> 'None':

        document = {'rows': [10, 20, 30, 40]}
        result = collect_candidates(document)

        candidate = result.arrays[0]

        assert candidate.items is document['rows']
        assert candidate.total == 4

    def test_string_candidate_records_parent_and_key(self) -> 'None':

        document = {'details': {'description': _long_text}}
        result = collect_candidates(document)

        candidate = result.strings[0]

        assert candidate.parent is document['details']
        assert candidate.key == 'description'
        assert candidate.length == len(_long_text)

    def test_string_candidate_in_array_uses_index_as_key(self) -> 'None':

        document = {'entries': [_long_text, _long_text]}
        result = collect_candidates(document)

        first = result.strings[0]

        assert first.parent is document['entries']
        assert first.key == 0
        assert first.path == '$.entries[0]'

    def test_single_element_array_is_not_a_candidate(self) -> 'None':

        document = {'rows': [1]}
        result = collect_candidates(document)

        assert result.arrays == []

    def test_string_at_the_floor_is_not_a_candidate(self) -> 'None':

        document = {'exact': 'a' * Min_String_Length, 'above': 'b' * (Min_String_Length + 1)}
        result = collect_candidates(document)

        string_paths = []
        for candidate in result.strings:
            string_paths.append(candidate.path)

        assert string_paths == ['$.above']

    def test_root_string_is_not_a_candidate(self) -> 'None':

        # A root-level string has no container to shorten it in, so the walk skips it.
        result = collect_candidates('c' * (Min_String_Length + 100))

        assert result.strings == []
        assert result.arrays == []

    def test_short_root_string_is_not_a_candidate(self) -> 'None':

        result = collect_candidates('short')

        assert result.strings == []

    def test_scalars_are_ignored(self) -> 'None':

        document = {'count': 123, 'ratio': 0.5, 'flag': True, 'missing': None}
        result = collect_candidates(document)

        assert result.arrays == []
        assert result.strings == []

    def test_empty_array_is_not_a_candidate(self) -> 'None':

        document = {'rows': []}
        result = collect_candidates(document)

        assert result.arrays == []

    def test_node_cap_stops_the_walk(self) -> 'None':

        # One node for the root list plus one per element crosses the cap by exactly one.
        document = list(range(Max_Node_Count))
        result = collect_candidates(document)

        assert result.hit_node_cap is True

    def test_node_count_at_the_cap_is_allowed(self) -> 'None':

        # One node for the root list plus one per element lands exactly on the cap.
        document = list(range(Max_Node_Count - 1))
        result = collect_candidates(document)

        assert result.hit_node_cap is False

    def test_depth_cap_stops_the_descent(self) -> 'None':

        # One level deeper than the walk descends.
        document = _make_nested_lists(Max_Recursion_Depth + 2)
        result = collect_candidates(document)

        assert result.hit_depth_cap is True

    def test_depth_at_the_cap_is_allowed(self) -> 'None':

        # The deepest node sits exactly at the recursion cap.
        document = _make_nested_lists(Max_Recursion_Depth + 1)
        result = collect_candidates(document)

        assert result.hit_depth_cap is False

    def test_depth_cap_applies_to_dicts_too(self) -> 'None':

        over_cap = _make_nested_dicts(Max_Recursion_Depth + 2)
        at_cap = _make_nested_dicts(Max_Recursion_Depth + 1)

        assert collect_candidates(over_cap).hit_depth_cap is True
        assert collect_candidates(at_cap).hit_depth_cap is False

# ################################################################################################################################
# ################################################################################################################################
