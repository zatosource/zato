# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from heapq import heappop, heappush

# Zato
from zato.common.typing_ import anydict, anytuple
from zato.common.util.truncate.common import Array_Element_Floor, array_candidate_list, drop_entry_dict, DropReportEntry, \
    Kind_Array_Tail, Kind_String_Cut, Min_String_Length, string_candidate_list, Truncation_Marker
from zato.common.util.truncate.measure import get_size

# ################################################################################################################################
# ################################################################################################################################

# Type aliases for the ranking heaps - each entry is (negative size, path).
heap_entry_list = list[anytuple]

# ################################################################################################################################
# ################################################################################################################################

def _find_last_whitespace(text:'str') -> 'int':
    """ Returns the index of the last whitespace character in the text, or -1 if there is none.
    """
    index = len(text) - 1

    # Walk backwards until whitespace is found or the text is exhausted.
    while index >= 0:
        character = text[index]
        if character.isspace():
            break
        index -= 1

    out = index

    return out

# ################################################################################################################################
# ################################################################################################################################

def _has_digit(token:'str') -> 'bool':
    """ Returns True if the token contains at least one digit.
    """
    for character in token:
        if character.isdigit():
            out = True
            break
    else:
        out = False

    return out

# ################################################################################################################################
# ################################################################################################################################

def cut_string(value:'str', keep_length:'int') -> 'str':
    """ Cuts a string down to at most keep_length characters plus the marker, never leaving a partial token behind.
    The cut lands on a whitespace boundary and any trailing digit-bearing tokens are then dropped whole,
    so account numbers and similar values are either fully present or fully absent, never halved.
    """

    # Walk back from the keep point to the nearest whitespace, so no token is ever split in the middle ..
    cut_index = keep_length

    while cut_index > 0:
        character = value[cut_index]
        if character.isspace():
            break
        cut_index -= 1

    kept = value[:cut_index].rstrip()

    # .. then drop trailing digit-bearing tokens whole - a value like an account number spans several
    # whitespace-separated groups, and keeping only some of them would leave a misleading fragment ..
    while kept:
        boundary = _find_last_whitespace(kept)
        last_token = kept[boundary + 1:]

        if _has_digit(last_token):
            kept = kept[:boundary + 1].rstrip()
        else:
            break

    # .. and append the marker so the cut is visible exactly where it happened.
    if kept:
        out = kept + ' ' + Truncation_Marker
    else:
        out = Truncation_Marker

    return out

# ################################################################################################################################
# ################################################################################################################################

def drop_array_tails(
    arrays:'array_candidate_list',
    current_size:'int',
    target_size:'int',
    entries_by_path:'drop_entry_dict',
    ) -> 'int':
    """ Drops elements from the tails of arrays, longest array first, until the running size reaches the target
    or every array is down to its element floor. Returns the updated running size.
    """
    heap:'heap_entry_list' = []
    by_path:'anydict' = {}

    # Rank the candidates by length, with the path as a deterministic tie-break ..
    for candidate in arrays:
        item_count = len(candidate.items)
        heap_entry = (-item_count, candidate.path)
        heappush(heap, heap_entry)
        by_path[candidate.path] = candidate

    # .. and keep dropping tail elements from whichever array is currently the longest.
    while current_size > target_size and heap:

        heap_entry = heappop(heap)
        path = heap_entry[1]
        candidate = by_path[path]
        items = candidate.items

        # Removing the element also removes the comma that separated it from its predecessor -
        # the element floor guarantees a predecessor always exists, so this arithmetic is exact.
        dropped = items.pop()
        saved = get_size(dropped) + 1
        current_size -= saved

        # Record the cut, accumulating into the entry for this path if one exists already ..
        if entry := entries_by_path.get(path):
            entry.count += 1
            entry.size += saved
        else:
            entry = DropReportEntry()
            entry.path = path
            entry.kind = Kind_Array_Tail
            entry.count = 1
            entry.total = candidate.total
            entry.size = saved
            entries_by_path[path] = entry

        # .. and put the array back in the ranking if it can still be drained.
        remaining = len(items)

        if remaining > Array_Element_Floor:
            heap_entry = (-remaining, path)
            heappush(heap, heap_entry)

    out = current_size

    return out

# ################################################################################################################################
# ################################################################################################################################

def shorten_strings(
    strings:'string_candidate_list',
    current_size:'int',
    target_size:'int',
    entries_by_path:'drop_entry_dict',
    ) -> 'int':
    """ Shortens string values, longest string first, until the running size reaches the target
    or no string can be shortened any further. Returns the updated running size.
    """
    heap:'heap_entry_list' = []
    by_path:'anydict' = {}

    # Rank the candidates by length, with the path as a deterministic tie-break ..
    for candidate in strings:
        heap_entry = (-candidate.length, candidate.path)
        heappush(heap, heap_entry)
        by_path[candidate.path] = candidate

    # .. and keep halving whichever string is currently the longest.
    while current_size > target_size and heap:

        heap_entry = heappop(heap)
        path = heap_entry[1]
        candidate = by_path[path]
        parent = candidate.parent
        key = candidate.key

        # Aim at half the current length but never go below the floor.
        old_value = parent[key]
        old_length = len(old_value)
        keep_length = old_length // 2

        if keep_length < Min_String_Length:
            keep_length = Min_String_Length

        new_value = cut_string(old_value, keep_length)
        new_length = len(new_value)

        # A cut that does not make the value shorter saves nothing - the marker overhead
        # outweighs the removal - so such a candidate is simply retired from the ranking.
        if new_length >= old_length:
            continue

        # The saving is measured on the serialized forms, so escapes and multi-byte characters are exact.
        old_size = get_size(old_value)
        new_size = get_size(new_value)
        saved = old_size - new_size

        parent[key] = new_value
        current_size -= saved

        # Record the cut, accumulating into the entry for this path if one exists already ..
        chars_removed = old_length - new_length

        if entry := entries_by_path.get(path):
            entry.chars += chars_removed
            entry.size += saved
        else:
            entry = DropReportEntry()
            entry.path = path
            entry.kind = Kind_String_Cut
            entry.chars = chars_removed
            entry.size = saved
            entries_by_path[path] = entry

        # .. and put the string back in the ranking if it can still be shortened.
        if new_length > Min_String_Length:
            heap_entry = (-new_length, path)
            heappush(heap, heap_entry)

    out = current_size

    return out

# ################################################################################################################################
# ################################################################################################################################
