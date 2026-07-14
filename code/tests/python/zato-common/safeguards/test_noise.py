# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# piigex
from piigex import scan

# Zato
from zato.common.typing_ import any_
from zato.common.util.safeguards.common import Base64_Marker_Template, Base64_Min_Length, SafeguardResult
from zato.common.util.safeguards.noise import collapse_whitespace, strip_base64, strip_nulls

# ################################################################################################################################
# ################################################################################################################################

def _new_result() -> 'SafeguardResult':
    """ Returns a fresh result for direct stage calls.
    """
    out = SafeguardResult()
    out.pii_removed = {}
    out.signals = {}

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestStripNulls:

    def test_top_level_nulls_are_removed(self) -> 'None':

        result = _new_result()
        value = {'name': 'First invoice', 'reference': None, 'amount': 14.5, 'comment': None}

        cleaned = strip_nulls(value, result)

        assert cleaned == {'name': 'First invoice', 'amount': 14.5}
        assert result.nulls_removed == 2

    def test_nested_nulls_are_removed(self) -> 'None':

        result = _new_result()
        value = {'customer': {'name': 'Alder Trading', 'fax': None}, 'rows': [{'id': 'inv-0001', 'note': None}]}

        cleaned = strip_nulls(value, result)

        assert cleaned == {'customer': {'name': 'Alder Trading'}, 'rows': [{'id': 'inv-0001'}]}
        assert result.nulls_removed == 2

    def test_array_elements_are_never_removed(self) -> 'None':

        # Null array elements stay in place - positions must not shift.
        result = _new_result()
        value = {'readings': [1, None, 3, None]}

        cleaned = strip_nulls(value, result)

        assert cleaned == {'readings': [1, None, 3, None]}
        assert result.nulls_removed == 0

    def test_node_cap_stops_the_walk(self) -> 'None':

        # The walk budget runs out inside the long array, so the dict after it is never cleaned.
        result = _new_result()
        items = [0] * 10_000
        value = {'items': items, 'tail': {'gone': None}}

        cleaned = strip_nulls(value, result)

        assert cleaned['tail'] == {'gone': None}
        assert result.nulls_removed == 0

    def test_depth_cap_stops_the_walk(self) -> 'None':

        # A null buried below the depth cap survives because the walk never reaches it.
        result = _new_result()
        value:'any_' = {'leaf': None}

        for _ in range(105):
            value = {'child': value}

        cleaned = strip_nulls(value, result)

        assert result.nulls_removed == 0

        # The document itself is otherwise unchanged.
        node = cleaned

        for _ in range(105):
            node = node['child']

        assert node == {'leaf': None}

# ################################################################################################################################
# ################################################################################################################################

class TestStripBase64:

    def test_short_strings_are_never_blobs(self) -> 'None':

        result = _new_result()
        value = {'token': 'QUJD' * 10}

        cleaned = strip_base64(value, result)

        assert cleaned == {'token': 'QUJD' * 10}
        assert result.base64_blobs_removed == 0

    def test_long_non_base64_strings_are_untouched(self) -> 'None':

        result = _new_result()
        text = 'A log line with spaces and punctuation, repeated over and over. ' * 10
        value = {'log': text}

        cleaned = strip_base64(value, result)

        assert cleaned == {'log': text}
        assert result.base64_blobs_removed == 0

    def test_blob_is_replaced_with_marker(self) -> 'None':

        result = _new_result()
        blob = 'QUJD' * 100
        value = {'attachment': blob}

        cleaned = strip_base64(value, result)

        marker = Base64_Marker_Template.format(size=len(blob))

        assert cleaned == {'attachment': marker}
        assert result.base64_blobs_removed == 1
        assert result.base64_chars_removed == len(blob)

    def test_data_uri_blob_is_replaced(self) -> 'None':

        result = _new_result()
        blob = 'data:image/png;base64,' + 'QUJD' * 100 + '=='
        value = {'image': blob}

        cleaned = strip_base64(value, result)

        marker = Base64_Marker_Template.format(size=len(blob))

        assert cleaned == {'image': marker}
        assert result.base64_blobs_removed == 1

    def test_floor_boundary_is_respected(self) -> 'None':

        # A blob exactly one character under the floor survives.
        result = _new_result()
        blob = 'A' * (Base64_Min_Length - 1)
        value = {'attachment': blob}

        cleaned = strip_base64(value, result)

        assert cleaned == {'attachment': blob}
        assert result.base64_blobs_removed == 0

# ################################################################################################################################
# ################################################################################################################################

class TestCollapseWhitespace:

    def test_runs_collapse_to_single_spaces(self) -> 'None':

        result = _new_result()
        value = {'note': 'First  line\n\nsecond\t\tline'}

        cleaned = collapse_whitespace(value, result)

        assert cleaned == {'note': 'First line second line'}
        assert result.whitespace_chars_removed == 3

    def test_single_spaces_are_left_alone(self) -> 'None':

        result = _new_result()
        value = {'note': 'One space between every word'}

        cleaned = collapse_whitespace(value, result)

        assert cleaned == {'note': 'One space between every word'}
        assert result.whitespace_chars_removed == 0

    def test_spaced_iban_still_matches_after_collapsing(self) -> 'None':

        # Collapsing preserves single spaces, so a spaced IBAN still matches PII detectors afterwards.
        result = _new_result()
        value = {'payment': 'Send to  ES91 2100 0418 4502 0005 1332  by Friday'}

        cleaned = collapse_whitespace(value, result)

        matches = scan(cleaned['payment'])

        found = []

        for match in matches:
            if match.name == 'intl_iban':
                found.append(match)

        assert len(found) == 1
        assert found[0].valid is True

    def test_node_cap_stops_the_walk(self) -> 'None':

        # The walk budget runs out inside the long array, so the string after it keeps its whitespace runs.
        result = _new_result()
        items = [0] * 10_000
        value = {'items': items, 'tail': '  end  '}

        cleaned = collapse_whitespace(value, result)

        assert cleaned['tail'] == '  end  '
        assert result.whitespace_chars_removed == 0

    def test_depth_cap_stops_the_walk(self) -> 'None':

        # A string buried below the depth cap keeps its whitespace runs.
        result = _new_result()
        value:'any_' = {'text': 'two  spaces'}

        for _ in range(105):
            value = {'child': value}

        _ = collapse_whitespace(value, result)

        assert result.whitespace_chars_removed == 0

# ################################################################################################################################
# ################################################################################################################################
