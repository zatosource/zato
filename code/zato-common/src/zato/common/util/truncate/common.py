# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass

# Zato
from zato.common.typing_ import any_, anylist

# ################################################################################################################################
# ################################################################################################################################

# Type aliases - the classes are defined below in this module.
array_candidate_list  = list['ArrayCandidate']
string_candidate_list = list['StringCandidate']
drop_entry_list       = list['DropReportEntry']
drop_entry_dict       = dict[str, 'DropReportEntry']

# ################################################################################################################################
# ################################################################################################################################

# Key under which the truncation report is embedded in dict results.
Report_Key = '_truncation'

# Marker appended in place of removed string content.
Truncation_Marker = '[... truncated]'

# Strings at or below this many characters are never shortened.
Min_String_Length = 256

# The candidate walk never descends deeper than this.
Max_Recursion_Depth = 100

# The candidate walk never visits more nodes than this.
Max_Node_Count = 10_000

# Arrays are never drained below this many elements.
Array_Element_Floor = 1

# Bytes reserved below the size cap for the embedded truncation report.
Report_Budget = 3072

# At most this many drop entries are listed individually in a report.
Max_Report_Entries = 5

# Paths longer than this many characters are shortened at a segment boundary.
Max_Path_Length = 100

# Size caps below this value cannot accommodate meaningful degradation and are refused.
Min_Usable_Cap = 4096

# Kinds of drops that can appear in a report.
Kind_Array_Tail = 'array_tail'
Kind_String_Cut = 'string_cut'
Kind_Aggregate  = 'aggregate'

# Templates for the plain-language note attached to every report.
Note_Intro      = 'This response was truncated to fit a size limit. It is still valid JSON. ' + \
                  'Removed content is listed under dropped, by JSONPath.'
Note_Array_Tail = '{count} of {total} items were removed from {path}.'
Note_String_Cut = '{chars} characters were removed from the end of {path} at the marker.'
Note_Aggregate  = 'There were also {count} more cuts, {size} bytes in total.'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class DropReportEntry:
    """ One cut recorded during graceful degradation - which path it happened at, what kind of cut it was and how much it removed.
    """
    path:  str = ''
    kind:  str = ''
    count: int = 0
    total: int = 0
    chars: int = 0
    size:  int = 0

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class ArrayCandidate:
    """ An array that graceful degradation may drain from its tail.
    """
    path:  str
    items: anylist
    total: int

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class StringCandidate:
    """ A string value that graceful degradation may shorten, along with the container that holds it.
    """
    path:   str
    parent: any_
    key:    any_
    length: int

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class WalkResult:
    """ Everything the candidate walk found in a document.
    """
    arrays:  array_candidate_list
    strings: string_candidate_list
    hit_node_cap:  bool
    hit_depth_cap: bool

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class TruncateResult:
    """ The outcome of truncating a value - the possibly degraded value itself plus a full account of what happened.
    """
    value:  any_
    report: drop_entry_list
    size_before:   int = 0
    size_after:    int = 0
    was_truncated: bool = False
    was_refused:   bool = False
    did_fit:       bool = False

# ################################################################################################################################
# ################################################################################################################################
