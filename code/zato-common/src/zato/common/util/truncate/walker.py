# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.typing_ import any_, anydict, anylist
from zato.common.util.truncate.common import Array_Element_Floor, ArrayCandidate, Max_Node_Count, Max_Recursion_Depth, \
    Min_String_Length, StringCandidate, WalkResult

# ################################################################################################################################
# ################################################################################################################################

def _visit(result:'WalkResult', node_count:'int', value:'any_', path:'str', depth:'int', parent:'any_', key:'any_') -> 'int':
    """ Visits one node of the document, recording it as a candidate if it qualifies, and descends into containers.
    Returns the updated node count.
    """

    # Every visited node spends one unit of the walk budget ..
    node_count += 1

    # .. and once the budget is gone, the walk stops so pathological documents stay cheap -
    # the caller then degrades only what was seen.
    if node_count > Max_Node_Count:
        result.hit_node_cap = True
        return node_count

    # Containers below this depth are not descended into.
    if depth > Max_Recursion_Depth:
        result.hit_depth_cap = True
        return node_count

    # Dicts are walked value by value - keys are never candidates because they are never dropped.
    if isinstance(value, dict):
        node_count = _visit_dict(result, node_count, value, path, depth)

    # Arrays above the element floor are candidates and their elements are walked too.
    elif isinstance(value, list):
        node_count = _visit_list(result, node_count, value, path, depth)

    # Strings above the length floor are candidates, provided a container holds them -
    # a root-level string has no container and is handled by the caller directly.
    elif isinstance(value, str):
        _visit_str(result, value, path, parent, key)

    return node_count

# ################################################################################################################################
# ################################################################################################################################

def _visit_dict(result:'WalkResult', node_count:'int', value:'anydict', path:'str', depth:'int') -> 'int':
    """ Descends into every value of a dict.
    """
    child_depth = depth + 1

    for child_key, child_value in value.items():
        child_path = f'{path}.{child_key}'
        node_count = _visit(result, node_count, child_value, child_path, child_depth, value, child_key)

    return node_count

# ################################################################################################################################
# ################################################################################################################################

def _visit_list(result:'WalkResult', node_count:'int', value:'anylist', path:'str', depth:'int') -> 'int':
    """ Records an array candidate and descends into every element.
    """

    # Only arrays that can actually be drained are candidates ..
    item_count = len(value)

    if item_count > Array_Element_Floor:
        candidate = ArrayCandidate()
        candidate.path = path
        candidate.items = value
        candidate.total = item_count
        result.arrays.append(candidate)

    # .. and the elements are walked regardless, because they may hold candidates of their own.
    child_depth = depth + 1

    for child_index, child_value in enumerate(value):
        child_path = f'{path}[{child_index}]'
        node_count = _visit(result, node_count, child_value, child_path, child_depth, value, child_index)

    return node_count

# ################################################################################################################################
# ################################################################################################################################

def _visit_str(result:'WalkResult', value:'str', path:'str', parent:'any_', key:'any_') -> 'None':
    """ Records a string candidate if the value is long enough to be worth shortening.
    """

    # Short strings are never shortened - identifiers, names and other short values always survive intact.
    length = len(value)

    if length > Min_String_Length:
        if parent is not None:
            candidate = StringCandidate()
            candidate.path = path
            candidate.parent = parent
            candidate.key = key
            candidate.length = length
            result.strings.append(candidate)

# ################################################################################################################################
# ################################################################################################################################

def collect_candidates(value:'any_') -> 'WalkResult':
    """ Walks a document and returns every array and string that graceful degradation may cut.
    """

    # Our response to produce
    out = WalkResult()
    out.arrays = []
    out.strings = []
    out.hit_node_cap = False
    out.hit_depth_cap = False

    _ = _visit(out, 0, value, '$', 0, None, None)

    return out

# ################################################################################################################################
# ################################################################################################################################
