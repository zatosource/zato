# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import operator

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict, strlist

# ################################################################################################################################
# ################################################################################################################################

# The comparison prefixes a date search parameter may carry, per the spec's search.html#prefix.
_date_search_prefixes = ('eq', 'ne', 'gt', 'lt', 'ge', 'le')

# Maps each date search prefix to the comparison it stands for.
_date_comparators = {
    'eq': operator.eq,
    'ne': operator.ne,
    'gt': operator.gt,
    'lt': operator.lt,
    'ge': operator.ge,
    'le': operator.le,
}

# How many leading characters a leaf needs for the date check.
_date_digit_count = 4

# ################################################################################################################################
# ################################################################################################################################

def collect_string_leaves(value:'any_', out:'strlist') -> 'None':
    """ Recursively collects all string values found in a JSON-like structure.
    Booleans are collected in their JSON form, so token searches like active=true can match them.
    """
    if isinstance(value, bool):
        if value:
            out.append('true')
        else:
            out.append('false')

    elif isinstance(value, str):
        out.append(value)

    elif isinstance(value, list):
        for item in value:
            collect_string_leaves(item, out)

    elif isinstance(value, dict):
        for item in value.values():
            collect_string_leaves(item, out)

# ################################################################################################################################

def _matches_date(leaves:'strlist', prefix:'str', value:'str') -> 'bool':
    """ Returns True if any date-shaped leaf satisfies the prefixed comparison, e.g. ge2024-01-01.
    Each leaf is truncated to the search value's precision before the comparison.
    """

    # Our response to produce
    out = False

    # The prefix always names one of the comparators above.
    comparator = _date_comparators[prefix]

    value_length = len(value)

    for leaf in leaves:

        # Only leaves that start like a date take part in the comparison.
        leaf_length = len(leaf)

        if leaf_length < _date_digit_count:
            continue

        leaf_start = leaf[:_date_digit_count]

        if not leaf_start.isdigit():
            continue

        truncated = leaf[:value_length]

        # The first satisfied comparison is enough.
        if comparator(truncated, value):
            out = True
            break

    return out

# ################################################################################################################################

def matches(resource:'stranydict', field_name:'str', value:'str') -> 'bool':
    """ Returns True if the resource matches one search parameter. Matching is a case-insensitive
    prefix match over string values, which covers the spec's string search (prefix match) and,
    in practice, its token search (exact match). Date parameters may carry a comparison prefix,
    e.g. date=ge2024-01-01. Search parameters address nested elements, e.g. Patient's family
    parameter targets Patient.name.family, so when the parameter is not a top-level field,
    the match is evaluated over all strings in the whole resource.
    """

    # The _id parameter always matches against the logical ID exactly.
    if field_name == '_id':
        out = resource['id'] == value
        return out

    # A top-level field of the same name narrows the match to that field,
    # otherwise the whole resource takes part in it ..
    field_value = resource.get(field_name)
    if field_value is None:
        field_value = resource

    # .. collect every string in whatever we match against, no matter how deeply nested ..
    leaves:'strlist' = []
    collect_string_leaves(field_value, leaves)

    # A value like ge2024-01-01 is a prefixed date comparison, not a string match.
    prefix = value[:2]

    if prefix in _date_search_prefixes:
        first_after_prefix = value[2:3]

        if first_after_prefix.isdigit():
            date_value = value[2:]

            out = _matches_date(leaves, prefix, date_value)
            return out

    leaves_lower = [leaf.lower() for leaf in leaves]

    # A token search in the system|code form, per the spec's search.html#token,
    # matches when both the system and the code appear in the element searched.
    if '|' in value:
        system, code = value.split('|', 1)
        out = system.lower() in leaves_lower and code.lower() in leaves_lower
        return out

    # .. and checking each one for a case-insensitive prefix match.
    value_lower = value.lower()

    for leaf_lower in leaves_lower:
        if leaf_lower.startswith(value_lower):
            out = True
            break
    else:
        out = False

    return out

# ################################################################################################################################
# ################################################################################################################################
