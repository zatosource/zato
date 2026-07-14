# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.util.truncate.common import DropReportEntry, drop_entry_list, Kind_Aggregate, Kind_Array_Tail, \
    Kind_String_Cut, Max_Path_Length, Max_Report_Entries
from zato.common.util.truncate.report import bound_entries, build_note, build_report, shorten_path

# ################################################################################################################################
# ################################################################################################################################

def _make_array_entry(path:'str', count:'int'=3, total:'int'=10, size:'int'=100) -> 'DropReportEntry':
    out = DropReportEntry()
    out.path = path
    out.kind = Kind_Array_Tail
    out.count = count
    out.total = total
    out.size = size

    return out

# ################################################################################################################################

def _make_string_entry(path:'str', chars:'int'=500, size:'int'=500) -> 'DropReportEntry':
    out = DropReportEntry()
    out.path = path
    out.kind = Kind_String_Cut
    out.chars = chars
    out.size = size

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestShortenPath:

    def test_short_path_passes_through(self) -> 'None':

        path = '$.rows[3].name'
        result = shorten_path(path)

        assert result == path

    def test_long_path_is_cut_at_a_dot_boundary(self) -> 'None':

        segment = 'segment_with_a_reasonably_long_name'
        path = '$.' + segment + '.' + segment + '.' + segment + '.' + segment

        result = shorten_path(path)

        assert result.endswith('...')
        assert len(result) <= Max_Path_Length + 3
        assert result.startswith('$.' + segment)

    def test_long_path_is_cut_at_a_bracket_boundary(self) -> 'None':

        # The bracket sits closer to the cap than any dot, so the cut happens there.
        long_key = 'k' * (Max_Path_Length - 10)
        path = '$.' + long_key + '[123456].name'

        result = shorten_path(path)

        assert result == '$.' + long_key + '...'

# ################################################################################################################################
# ################################################################################################################################

class TestBoundEntries:

    def test_short_list_passes_through(self) -> 'None':

        entries:'drop_entry_list' = []
        for index in range(Max_Report_Entries):
            entry = _make_array_entry(f'$.rows_{index}')
            entries.append(entry)

        result = bound_entries(entries)

        assert result is entries

    def test_overflow_collapses_into_an_aggregate(self) -> 'None':

        entries:'drop_entry_list' = []
        for index in range(Max_Report_Entries + 4):
            entry = _make_array_entry(f'$.rows_{index}', size=50)
            entries.append(entry)

        result = bound_entries(entries)

        assert len(result) == Max_Report_Entries + 1

        aggregate = result[-1]

        assert aggregate.kind == Kind_Aggregate
        assert aggregate.count == 4
        assert aggregate.size == 200

# ################################################################################################################################
# ################################################################################################################################

class TestBuildNote:

    def test_every_kind_gets_a_sentence(self) -> 'None':

        array_entry = _make_array_entry('$.rows', count=97, total=100)
        string_entry = _make_string_entry('$.body', chars=1234)

        aggregate = DropReportEntry()
        aggregate.kind = Kind_Aggregate
        aggregate.count = 7
        aggregate.size = 999

        note = build_note([array_entry, string_entry, aggregate])

        assert '97 of 100 items were removed from $.rows.' in note
        assert '1234 characters were removed from the end of $.body at the marker.' in note
        assert 'There were also 7 more cuts, 999 bytes in total.' in note

    def test_note_names_every_path(self) -> 'None':

        entries = [_make_array_entry('$.first'), _make_array_entry('$.second'), _make_string_entry('$.third')]
        note = build_note(entries)

        for entry in entries:
            assert entry.path in note

# ################################################################################################################################
# ################################################################################################################################

class TestBuildReport:

    def test_report_shape(self) -> 'None':

        entries = [_make_array_entry('$.rows', count=9997, total=10000), _make_string_entry('$.body', chars=4000)]
        report = build_report(entries, 2097152)

        assert report['was_truncated'] is True
        assert report['size_before'] == 2097152
        assert report['dropped'] == [
            {'path': '$.rows', 'kind': Kind_Array_Tail, 'count': 9997, 'total': 10000},
            {'path': '$.body', 'kind': Kind_String_Cut, 'chars': 4000},
        ]

    def test_note_and_dropped_agree(self) -> 'None':

        entries = [_make_array_entry('$.rows'), _make_string_entry('$.sections')]
        report = build_report(entries, 50000)

        for entry_dict in report['dropped']:
            assert entry_dict['path'] in report['note']

    def test_aggregate_entry_has_no_path(self) -> 'None':

        entries:'drop_entry_list' = []
        for index in range(Max_Report_Entries + 2):
            entry = _make_string_entry(f'$.body_{index}')
            entries.append(entry)

        report = build_report(entries, 50000)

        aggregate_dict = report['dropped'][-1]

        assert aggregate_dict == {'kind': Kind_Aggregate, 'count': 2, 'size': 1000}

# ################################################################################################################################
# ################################################################################################################################
