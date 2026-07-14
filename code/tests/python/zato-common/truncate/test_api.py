# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from copy import deepcopy
from json import loads

# Zato
from zato.common.typing_ import dictlist, stranydict
from zato.common.util.truncate.api import truncate_json
from zato.common.util.truncate.common import Kind_Array_Tail, Kind_String_Cut, Min_Usable_Cap, Report_Key, Truncation_Marker
from zato.common.util.truncate.measure import get_size, serialize

# ################################################################################################################################
# ################################################################################################################################

_cap = Min_Usable_Cap

# ################################################################################################################################
# ################################################################################################################################

def _make_rows(count:'int') -> 'dictlist':
    out = []
    for index in range(count):
        row = {'id': f'inv-{index:05}', 'amount': index * 1.5, 'customer': 'Customer name here'}
        out.append(row)

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestPassthroughAndRefusal:

    def test_value_under_the_cap_passes_through_untouched(self) -> 'None':

        document = {'status': 'ok', 'total': 3}
        result = truncate_json(document, _cap)

        assert result.value is document
        assert result.was_truncated is False
        assert result.was_refused is False
        assert result.did_fit is True
        assert result.size_before == result.size_after
        assert result.report == []

    def test_cap_below_the_minimum_is_refused(self) -> 'None':

        document = {'body': 'x' * 20000}
        result = truncate_json(document, Min_Usable_Cap - 1)

        assert result.was_refused is True
        assert result.was_truncated is False
        assert result.did_fit is False
        assert result.value is document

# ################################################################################################################################
# ################################################################################################################################

class TestArrayPhase:

    def test_oversized_array_is_drained_and_the_report_is_embedded(self) -> 'None':

        document = {'status': 'ok', 'total': 2000, 'rows': _make_rows(2000)}
        result = truncate_json(document, _cap)

        assert result.was_truncated is True
        assert result.did_fit is True
        assert result.size_after <= _cap

        # The output parses as valid JSON and the scalar fields are untouched.
        parsed = loads(serialize(result.value))

        assert parsed['status'] == 'ok'
        assert parsed['total'] == 2000

        # The report is embedded, its note names the cut, and its numbers agree with the entry.
        report = parsed[Report_Key]
        entry = report['dropped'][0]

        assert report['was_truncated'] is True
        assert report['size_before'] == result.size_before
        assert entry['path'] == '$.rows'
        assert entry['kind'] == Kind_Array_Tail
        assert entry['count'] + len(parsed['rows']) == entry['total']
        assert f'{entry["count"]} of {entry["total"]} items were removed from $.rows.' in report['note']

    def test_root_list_is_truncated_without_an_embedded_report(self) -> 'None':

        document = _make_rows(2000)
        result = truncate_json(document, _cap)

        assert result.was_truncated is True
        assert result.did_fit is True
        assert isinstance(result.value, list)

        # The report still exists, on the result itself.
        entry = result.report[0]

        assert entry.path == '$'
        assert entry.kind == Kind_Array_Tail

    def test_input_is_never_mutated(self) -> 'None':

        document = {'rows': _make_rows(2000)}
        snapshot = deepcopy(document)

        _ = truncate_json(document, _cap)

        assert document == snapshot

# ################################################################################################################################
# ################################################################################################################################

class TestRootString:

    def test_root_string_is_shortened_to_fit(self) -> 'None':

        document = 'word ' * 840
        result = truncate_json(document, _cap)

        assert result.was_truncated is True
        assert result.did_fit is True
        assert result.size_after <= _cap
        assert result.value.endswith(Truncation_Marker)

        entry = result.report[0]

        assert entry.path == '$'
        assert entry.kind == Kind_String_Cut
        assert entry.chars == len(document) - len(result.value)

    def test_huge_root_string_takes_several_halvings(self) -> 'None':

        document = 'word ' * 100000
        result = truncate_json(document, _cap)

        assert result.did_fit is True
        assert result.size_after <= _cap
        assert result.value.endswith(Truncation_Marker)

# ################################################################################################################################
# ################################################################################################################################

class TestNothingToCut:

    def test_document_with_no_candidates_is_returned_as_is(self) -> 'None':

        # Many short values under one key each - nothing the trimming is allowed to remove.
        document = {}
        for index in range(120):
            document[f'key_{index:03}'] = 'v' * 45

        size_before = get_size(document)

        assert size_before > _cap

        result = truncate_json(document, _cap)

        assert result.was_truncated is False
        assert result.did_fit is False
        assert result.size_after == size_before
        assert result.value == document
        assert result.value is not document

# ################################################################################################################################
# ################################################################################################################################

class TestReportBackout:

    def test_report_is_backed_out_when_it_would_not_fit(self) -> 'None':

        # A document just over the cap with one small cut available - the cut brings it under the cap
        # but leaves no room for the report, so the report stays on the result only.
        first_element = {'field_a': 'x' * 100, 'field_b': 'y' * 100}
        second_element = {'field_a': 'p' * 100, 'field_b': 'q' * 100}
        document:'stranydict' = {'rows': [first_element, second_element]}

        index = 0
        while get_size(document) <= _cap:
            document[f'key_{index:03}'] = 'v' * 45
            index += 1

        size_before = get_size(document)

        assert size_before > _cap

        result = truncate_json(document, _cap)

        # The cut itself fit the document under the cap ..
        assert result.was_truncated is True
        assert result.did_fit is True
        assert result.size_after <= _cap

        # .. but the report did not fit alongside it, so it lives only on the result.
        assert Report_Key not in result.value
        assert len(result.report) == 1

# ################################################################################################################################
# ################################################################################################################################
