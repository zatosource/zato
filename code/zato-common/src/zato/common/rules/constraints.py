# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.rules.document import Comparator, NodeKind

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist

# ################################################################################################################################
# ################################################################################################################################

class ConstraintKind:
    """ What kind of value space a constraint describes.
    """
    Any     = 'any'      # A blank cell - every value satisfies it
    Number  = 'number'   # A union of numeric intervals
    Text    = 'text'     # An included or excluded set of texts
    Boolean = 'boolean'  # An included set of the two truth values
    Unknown = 'unknown'  # Nothing provable - regex matches, references, mixed types

# How a text constraint holds its values - as the allowed set or as the forbidden set.
Mode_Include = 'include'
Mode_Exclude = 'exclude'

# The two ends of the number line, for intervals open on either side.
Lowest  = float('-inf')
Highest = float('inf')

# ################################################################################################################################
# ################################################################################################################################

def _new_interval(low:'float', low_closed:'bool', high:'float', high_closed:'bool') -> 'anydict':
    out = {'low': low, 'low_closed': low_closed, 'high': high, 'high_closed': high_closed}
    return out

# ################################################################################################################################

def _number_constraint(intervals:'anylist') -> 'anydict':
    out = {'kind': ConstraintKind.Number, 'intervals': intervals}
    return out

# ################################################################################################################################

def _text_constraint(mode:'str', values:'anylist') -> 'anydict':
    out = {'kind': ConstraintKind.Text, 'mode': mode, 'values': set(values)}
    return out

# ################################################################################################################################

def _boolean_constraint(values:'anylist') -> 'anydict':
    out = {'kind': ConstraintKind.Boolean, 'values': set(values)}
    return out

# ################################################################################################################################

def _unknown_constraint() -> 'anydict':
    out = {'kind': ConstraintKind.Unknown}
    return out

# ################################################################################################################################

def any_constraint() -> 'anydict':
    """ The constraint a blank cell carries - every value satisfies it.
    """
    out = {'kind': ConstraintKind.Any}
    return out

# ################################################################################################################################
# ################################################################################################################################

def _literal_value(node:'anydict') -> 'anydict | None':
    """ Returns a wrapper with the plain value of a literal node, or None for anything unprovable.

    The wrapper is needed because None, unwrapped, would be ambiguous with the not-a-literal answer.
    """

    # Only plain literals have a value we can reason about ..
    if node['kind'] != NodeKind.Literal:
        return None

    # .. and datetime literals are texts whose ordering we do not model.
    if 'value_type' in node:
        return None

    out = {'value': node['value']}
    return out

# ################################################################################################################################

def _point(value:'float') -> 'anydict':
    """ An interval holding exactly one number.
    """
    out = _new_interval(value, True, value, True)
    return out

# ################################################################################################################################

def _from_equality(value:'any_') -> 'anydict':
    """ Builds the constraint of an is comparison against a literal.
    """

    # Booleans first - a bool is also an int in Python, so this check has to lead.
    if isinstance(value, bool):
        out = _boolean_constraint([value])

    elif isinstance(value, (int, float)):
        out = _number_constraint([_point(value)])

    elif isinstance(value, str):
        out = _text_constraint(Mode_Include, [value])

    else:
        out = _unknown_constraint()

    return out

# ################################################################################################################################

def _from_inequality(value:'any_') -> 'anydict':
    """ Builds the constraint of an is not comparison - everything but the value.
    """
    if isinstance(value, bool):
        out = _boolean_constraint([not value])

    elif isinstance(value, (int, float)):
        below = _new_interval(Lowest, False, value, False)
        above = _new_interval(value, False, Highest, False)
        out = _number_constraint([below, above])

    elif isinstance(value, str):
        out = _text_constraint(Mode_Exclude, [value])

    else:
        out = _unknown_constraint()

    return out

# ################################################################################################################################

def _from_membership(values:'anylist', is_negated:'bool') -> 'anydict':
    """ Builds the constraint of a membership comparison over literal values.
    """

    # Mixed-type memberships are not something we can reason about ..
    all_text = True
    all_bool = True

    for value in values:
        if not isinstance(value, str):
            all_text = False
        if not isinstance(value, bool):
            all_bool = False

    # .. texts are the common case for sets ..
    if all_text:
        mode = Mode_Exclude if is_negated else Mode_Include
        out = _text_constraint(mode, values)

    # .. booleans reduce to an included set either way ..
    elif all_bool:
        if is_negated:
            remaining = {True, False} - set(values)
            out = _boolean_constraint(list(remaining))
        else:
            out = _boolean_constraint(values)

    else:
        out = _unknown_constraint()

    return out

# ################################################################################################################################

def condition_constraint(condition:'anydict') -> 'anydict':
    """ Turns the comparator and values of a parsed condition into a value-space constraint.

    Whatever cannot be reasoned about - regex matches, references to other terms,
    datetimes, mixed-type sets - becomes an unknown constraint, which every check
    then treats conservatively.
    """
    comparator = condition['comparator']

    # Truth checks carry no values at all ..
    if comparator == Comparator.Is_True:
        out = _boolean_constraint([True])
        return out

    if comparator == Comparator.Is_False:
        out = _boolean_constraint([False])
        return out

    # .. regex matches are never provable ..
    if comparator == Comparator.Matches:
        out = _unknown_constraint()
        return out

    # .. everything else needs its literal values first.
    values = []
    for node in condition['values']:
        wrapper = _literal_value(node)
        if wrapper is None:
            out = _unknown_constraint()
            return out
        values.append(wrapper['value'])

    if comparator == Comparator.Is:
        out = _from_equality(values[0])

    elif comparator == Comparator.Is_Not:
        out = _from_inequality(values[0])

    elif comparator == Comparator.Is_Less_Than:
        out = _number_constraint([_new_interval(Lowest, False, values[0], False)])

    elif comparator == Comparator.Is_At_Most:
        out = _number_constraint([_new_interval(Lowest, False, values[0], True)])

    elif comparator == Comparator.Is_At_Least:
        out = _number_constraint([_new_interval(values[0], True, Highest, False)])

    elif comparator == Comparator.Is_More_Than:
        out = _number_constraint([_new_interval(values[0], False, Highest, False)])

    elif comparator == Comparator.Is_Between:
        out = _number_constraint([_new_interval(values[0], True, values[1], True)])

    elif comparator == Comparator.Is_One_Of:
        out = _from_membership(values, False)

    elif comparator == Comparator.Is_Not_One_Of:
        out = _from_membership(values, True)

    else:
        out = _unknown_constraint()

    return out

# ################################################################################################################################
# ################################################################################################################################
