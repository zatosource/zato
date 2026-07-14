# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from copy import deepcopy

# Zato
from zato.common.typing_ import any_
from zato.common.util.truncate.common import drop_entry_dict, DropReportEntry, Kind_String_Cut, Min_Usable_Cap, Report_Budget, \
    Report_Key, TruncateResult
from zato.common.util.truncate.degrade import cut_string, drop_array_tails, shorten_strings
from zato.common.util.truncate.measure import get_size
from zato.common.util.truncate.report import build_report
from zato.common.util.truncate.walker import collect_candidates

# ################################################################################################################################
# ################################################################################################################################

def _shorten_root_string(value:'str', max_size:'int') -> 'str':
    """ Shortens a document that is a single string, halving the keep length until the result fits.
    """
    keep_length = len(value) // 2
    out = cut_string(value, keep_length)

    # Each halving of the keep length shrinks the result, so this always terminates -
    # in the extreme, an empty keep length leaves only the marker, which always fits.
    while get_size(out) > max_size:
        keep_length = keep_length // 2
        out = cut_string(value, keep_length)

    return out

# ################################################################################################################################
# ################################################################################################################################

def _truncate_root_string(out:'TruncateResult', work:'str', max_size:'int', size_before:'int') -> 'TruncateResult':
    """ Handles the degenerate case of a document that is a single string - there is no structure to degrade,
    so the string itself is shortened, which still yields valid JSON.
    """
    shortened = _shorten_root_string(work, max_size)
    size_after = get_size(shortened)

    # A single entry accounts for the whole cut.
    entry = DropReportEntry()
    entry.path = '$'
    entry.kind = Kind_String_Cut
    entry.chars = len(work) - len(shortened)
    entry.size = size_before - size_after

    out.value = shortened
    out.report = [entry]
    out.size_after = size_after
    out.was_truncated = True
    out.did_fit = True

    return out

# ################################################################################################################################
# ################################################################################################################################

def truncate_json(value:'any_', max_size:'int') -> 'TruncateResult':
    """ Truncates a JSON-serializable value to fit within max_size bytes through graceful degradation -
    array tails are dropped first, longest arrays first, then the longest string values are shortened,
    and the result is valid JSON at every step, with a report of every cut. The input is never mutated.
    """

    # Our response to produce
    out = TruncateResult()
    out.value = value
    out.report = []

    size_before = get_size(value)
    out.size_before = size_before
    out.size_after = size_before

    # Values already under the cap pass through untouched.
    if size_before <= max_size:
        out.did_fit = True
        return out

    # Caps too small for meaningful degradation are refused - the caller decides what to do instead.
    if max_size < Min_Usable_Cap:
        out.was_refused = True
        return out

    # Everything below works on a copy - the caller's object is never mutated.
    work = deepcopy(value)

    # A document that is a single string has no structure to degrade - the string itself is shortened.
    if isinstance(work, str):
        out = _truncate_root_string(out, work, max_size, size_before)
        return out

    # The degradation aims below the cap by the report budget, so the report always has room.
    target_size = max_size - Report_Budget
    current_size = size_before
    entries_by_path:'drop_entry_dict' = {}

    # Phase one - drop array tails, where the bulk of oversized documents lives.
    walk = collect_candidates(work)
    current_size = drop_array_tails(walk.arrays, current_size, target_size, entries_by_path)

    # Phase two - shorten the longest strings, collected anew because phase one changed the document.
    if current_size > target_size:
        walk = collect_candidates(work)
        current_size = shorten_strings(walk.strings, current_size, target_size, entries_by_path)

    entries = list(entries_by_path.values())
    size_after = get_size(work)

    # It only counts as truncated if something was actually removed.
    entry_count = len(entries)
    was_truncated = entry_count > 0

    out.report = entries
    out.was_truncated = was_truncated

    # The report is embedded only into dict documents and only when the whole result still fits -
    # this guarantees the report always costs less than the bytes it accounts for.
    if was_truncated:
        if isinstance(work, dict):
            report = build_report(entries, size_before)
            work[Report_Key] = report
            size_after = get_size(work)

            if size_after > max_size:
                del work[Report_Key]
                size_after = get_size(work)

    out.value = work
    out.size_after = size_after
    out.did_fit = size_after <= max_size

    return out

# ################################################################################################################################
# ################################################################################################################################
