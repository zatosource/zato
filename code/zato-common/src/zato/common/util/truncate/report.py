# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.typing_ import dictlist, stranydict, strlist
from zato.common.util.truncate.common import drop_entry_list, DropReportEntry, Kind_Aggregate, Kind_Array_Tail, \
    Kind_String_Cut, Max_Path_Length, Max_Report_Entries, Note_Aggregate, Note_Array_Tail, Note_Intro, Note_String_Cut

# ################################################################################################################################
# ################################################################################################################################

def shorten_path(path:'str') -> 'str':
    """ Shortens a path that exceeds the length cap, cutting at a segment boundary so the remainder stays readable.
    """

    # Most paths are short and pass through untouched.
    path_length = len(path)

    if path_length <= Max_Path_Length:
        out = path

    # Longer paths are cut at the last segment boundary before the cap - every path starts with the root
    # marker followed by a separator, so a boundary always exists within the cap.
    else:
        dot_boundary = path.rfind('.', 0, Max_Path_Length)
        bracket_boundary = path.rfind('[', 0, Max_Path_Length)
        boundary = max(dot_boundary, bracket_boundary)

        out = path[:boundary] + '...'

    return out

# ################################################################################################################################
# ################################################################################################################################

def _describe_array_tail(entry:'DropReportEntry') -> 'str':
    """ Builds the note sentence for an array tail drop.
    """
    path = shorten_path(entry.path)
    out = Note_Array_Tail.format(count=entry.count, total=entry.total, path=path)

    return out

# ################################################################################################################################
# ################################################################################################################################

def _describe_string_cut(entry:'DropReportEntry') -> 'str':
    """ Builds the note sentence for a string cut.
    """
    path = shorten_path(entry.path)
    out = Note_String_Cut.format(chars=entry.chars, path=path)

    return out

# ################################################################################################################################
# ################################################################################################################################

def _describe_aggregate(entry:'DropReportEntry') -> 'str':
    """ Builds the note sentence for the aggregate entry that stands in for collapsed cuts.
    """
    out = Note_Aggregate.format(count=entry.count, size=entry.size)

    return out

# ################################################################################################################################
# ################################################################################################################################

def _array_tail_to_dict(entry:'DropReportEntry') -> 'stranydict':
    """ Builds the embedded form of an array tail entry.
    """
    path = shorten_path(entry.path)
    out = {'path': path, 'kind': entry.kind, 'count': entry.count, 'total': entry.total}

    return out

# ################################################################################################################################
# ################################################################################################################################

def _string_cut_to_dict(entry:'DropReportEntry') -> 'stranydict':
    """ Builds the embedded form of a string cut entry.
    """
    path = shorten_path(entry.path)
    out = {'path': path, 'kind': entry.kind, 'chars': entry.chars}

    return out

# ################################################################################################################################
# ################################################################################################################################

def _aggregate_to_dict(entry:'DropReportEntry') -> 'stranydict':
    """ Builds the embedded form of the aggregate entry.
    """
    out = {'kind': entry.kind, 'count': entry.count, 'size': entry.size}

    return out

# ################################################################################################################################
# ################################################################################################################################

# What builds each kind of note sentence and each kind of embedded entry.
_describers = {
    Kind_Array_Tail: _describe_array_tail,
    Kind_String_Cut: _describe_string_cut,
    Kind_Aggregate:  _describe_aggregate,
}

_entry_builders = {
    Kind_Array_Tail: _array_tail_to_dict,
    Kind_String_Cut: _string_cut_to_dict,
    Kind_Aggregate:  _aggregate_to_dict,
}

# ################################################################################################################################
# ################################################################################################################################

def bound_entries(entries:'drop_entry_list') -> 'drop_entry_list':
    """ Caps the entry list at its maximum, collapsing the overflow into a single aggregate entry -
    this is what keeps the whole report within its fixed byte budget no matter how many cuts happened.
    """

    # Short lists pass through untouched.
    entry_count = len(entries)

    if entry_count <= Max_Report_Entries:
        out = entries

    # Longer lists keep their first entries and collapse the rest into one aggregate.
    else:
        kept = entries[:Max_Report_Entries]
        overflow = entries[Max_Report_Entries:]

        overflow_size = 0
        for entry in overflow:
            overflow_size += entry.size

        aggregate = DropReportEntry()
        aggregate.kind = Kind_Aggregate
        aggregate.count = len(overflow)
        aggregate.size = overflow_size

        out = kept + [aggregate]

    return out

# ################################################################################################################################
# ################################################################################################################################

def build_note(entries:'drop_entry_list') -> 'str':
    """ Builds the plain-language note - the intro followed by one sentence per entry,
    so a reader learns what was removed and from where without knowing the report format in advance.
    """
    sentences:'strlist' = []

    for entry in entries:
        describer = _describers[entry.kind]
        sentence = describer(entry)
        sentences.append(sentence)

    joined = ' '.join(sentences)

    out = Note_Intro + ' ' + joined

    return out

# ################################################################################################################################
# ################################################################################################################################

def build_report(entries:'drop_entry_list', size_before:'int') -> 'stranydict':
    """ Builds the report object embedded in truncated dict results - the bounded entry list,
    the plain-language note generated from the same entries, and the pre-truncation size.
    """
    bounded = bound_entries(entries)
    note = build_note(bounded)

    dropped:'dictlist' = []
    for entry in bounded:
        entry_builder = _entry_builders[entry.kind]
        entry_dict = entry_builder(entry)
        dropped.append(entry_dict)

    out = {
        'note': note,
        'was_truncated': True,
        'size_before': size_before,
        'dropped': dropped,
    }

    return out

# ################################################################################################################################
# ################################################################################################################################
