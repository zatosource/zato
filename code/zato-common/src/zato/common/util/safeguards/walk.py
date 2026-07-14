# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.typing_ import any_, anydict, anylist, callable_
from zato.common.util.truncate.common import Max_Node_Count, Max_Recursion_Depth

# ################################################################################################################################
# ################################################################################################################################

# Type aliases - a visitor receives a string value and its path and returns the replacement string.
str_visitor = callable_

# ################################################################################################################################
# ################################################################################################################################

def _visit(value:'any_', visit:'str_visitor', path:'str', depth:'int', parent:'any_', key:'any_', node_count:'int') -> 'int':
    """ Visits one node of the document, replacing string values with what the visitor returns, and descends into containers.
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

    # Dicts are walked value by value - keys are never visited because they are never modified.
    if isinstance(value, dict):
        node_count = _visit_dict(value, visit, path, depth, node_count)

    # Arrays keep their length - only their elements are visited.
    elif isinstance(value, list):
        node_count = _visit_list(value, visit, path, depth, node_count)

    # Strings are handed to the visitor and whatever it returns takes their place -
    # a root-level string has no container and is handled by walk_strings directly.
    elif isinstance(value, str):
        parent[key] = visit(value, path)

    return node_count

# ################################################################################################################################
# ################################################################################################################################

def _visit_dict(value:'anydict', visit:'str_visitor', path:'str', depth:'int', node_count:'int') -> 'int':
    """ Descends into every value of a dict.
    """
    child_depth = depth + 1

    for child_key, child_value in value.items():
        child_path = f'{path}.{child_key}'
        node_count = _visit(child_value, visit, child_path, child_depth, value, child_key, node_count)

    return node_count

# ################################################################################################################################
# ################################################################################################################################

def _visit_list(value:'anylist', visit:'str_visitor', path:'str', depth:'int', node_count:'int') -> 'int':
    """ Descends into every element of a list.
    """
    child_depth = depth + 1

    for child_index, child_value in enumerate(value):
        child_path = f'{path}[{child_index}]'
        node_count = _visit(child_value, visit, child_path, child_depth, value, child_index, node_count)

    return node_count

# ################################################################################################################################
# ################################################################################################################################

def walk_strings(value:'any_', visit:'str_visitor') -> 'any_':
    """ Applies a visitor to every string value in a document, replacing each with what the visitor returns.
    Containers are modified in place and a root-level string is replaced through the return value.
    """

    # A document that is a single string has no container - the visitor's output is the new document.
    if isinstance(value, str):
        out = visit(value, '$')
        return out

    _ = _visit(value, visit, '$', 0, None, None, 0)

    out = value

    return out

# ################################################################################################################################
# ################################################################################################################################
