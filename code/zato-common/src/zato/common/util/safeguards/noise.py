# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.typing_ import any_, anylist
from zato.common.util.safeguards.common import Base64_Marker_Template, Base64_Min_Length, Base64_Pattern, SafeguardResult, \
    Whitespace_Pattern
from zato.common.util.safeguards.walk import walk_strings
from zato.common.util.truncate.common import Max_Node_Count, Max_Recursion_Depth

# ################################################################################################################################
# ################################################################################################################################

def _strip_nulls_visit(value:'any_', result:'SafeguardResult', depth:'int', node_count:'int') -> 'int':
    """ Visits one node, removing null-valued keys from dicts and descending into containers.
    Returns the updated node count.
    """

    # Every visited node spends one unit of the walk budget ..
    node_count += 1

    # .. and once the budget is gone, the walk stops so pathological documents stay cheap.
    if node_count > Max_Node_Count:
        return node_count

    # Containers below this depth are not descended into.
    if depth > Max_Recursion_Depth:
        return node_count

    if isinstance(value, dict):

        # Null-valued keys are collected first and deleted after - a dict must not change while it is iterated over ..
        null_keys:'anylist' = []

        for child_key, child_value in value.items():
            if child_value is None:
                null_keys.append(child_key)

        for child_key in null_keys:
            del value[child_key]

        result.nulls_removed += len(null_keys)

        # .. and the values that remain are descended into.
        child_depth = depth + 1

        for child_value in value.values():
            node_count = _strip_nulls_visit(child_value, result, child_depth, node_count)

    # Array elements are never removed - positions must not shift - but dicts inside them are still cleaned.
    elif isinstance(value, list):
        child_depth = depth + 1

        for child_value in value:
            node_count = _strip_nulls_visit(child_value, result, child_depth, node_count)

    return node_count

# ################################################################################################################################
# ################################################################################################################################

def strip_nulls(value:'any_', result:'SafeguardResult') -> 'any_':
    """ Removes dict keys whose value is null, recursively - array elements are never removed, so positions do not shift.
    """
    _ = _strip_nulls_visit(value, result, 0, 0)

    out = value

    return out

# ################################################################################################################################
# ################################################################################################################################

def strip_base64(value:'any_', result:'SafeguardResult') -> 'any_':
    """ Replaces base64-looking strings above the length floor with a marker naming the original size.
    """

    def visit(text:'str', path:'str') -> 'str':

        # Short strings are never blobs ..
        length = len(text)

        if length < Base64_Min_Length:
            return text

        # .. and neither is anything shaped unlike base64.
        if not Base64_Pattern.fullmatch(text):
            return text

        # What remains is a blob - it is replaced whole and the removal is accounted for.
        result.base64_blobs_removed += 1
        result.base64_chars_removed += length

        out = Base64_Marker_Template.format(size=length)

        return out

    out = walk_strings(value, visit)

    return out

# ################################################################################################################################
# ################################################################################################################################

def collapse_whitespace(value:'any_', result:'SafeguardResult') -> 'any_':
    """ Collapses whitespace runs inside string values to a single space.
    """

    def visit(text:'str', path:'str') -> 'str':

        out = Whitespace_Pattern.sub(' ', text)

        removed = len(text) - len(out)
        result.whitespace_chars_removed += removed

        return out

    out = walk_strings(value, visit)

    return out

# ################################################################################################################################
# ################################################################################################################################
