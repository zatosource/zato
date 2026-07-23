# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.rules.constraints import ConstraintKind, Highest, Lowest, Mode_Exclude, Mode_Include

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist, boolnone

# ################################################################################################################################
# ################################################################################################################################

def _interval_intersection_nonempty(first:'anydict', second:'anydict') -> 'bool':
    """ Whether two intervals share at least one number.
    """

    # The intersection runs from the higher low to the lower high ..
    if first['low'] > second['low']:
        low = first['low']
        low_closed = first['low_closed']
    elif second['low'] > first['low']:
        low = second['low']
        low_closed = second['low_closed']
    else:
        low = first['low']
        low_closed = first['low_closed'] and second['low_closed']

    if first['high'] < second['high']:
        high = first['high']
        high_closed = first['high_closed']
    elif second['high'] < first['high']:
        high = second['high']
        high_closed = second['high_closed']
    else:
        high = first['high']
        high_closed = first['high_closed'] and second['high_closed']

    # .. and it holds a number when it has positive width, or zero width with both ends closed.
    if low < high:
        return True

    out = low == high and low_closed and high_closed
    return out

# ################################################################################################################################

def _interval_contains(outer:'anydict', inner:'anydict') -> 'bool':
    """ Whether one interval wholly contains another.
    """

    # The outer low end has to reach at least as far down ..
    low_ok = outer['low'] < inner['low']
    if not low_ok:
        if outer['low'] == inner['low']:
            low_ok = outer['low_closed'] or not inner['low_closed']

    # .. and the outer high end at least as far up.
    high_ok = outer['high'] > inner['high']
    if not high_ok:
        if outer['high'] == inner['high']:
            high_ok = outer['high_closed'] or not inner['high_closed']

    out = low_ok and high_ok
    return out

# ################################################################################################################################

def _numbers_overlap(first:'anydict', second:'anydict') -> 'bool':
    """ Whether two numeric constraints share at least one number.
    """
    for first_interval in first['intervals']:
        for second_interval in second['intervals']:
            if _interval_intersection_nonempty(first_interval, second_interval):
                return True

    return False

# ################################################################################################################################

def _numbers_cover(outer:'anydict', inner:'anydict') -> 'bool':
    """ Whether one numeric constraint wholly contains another.

    The intervals of a single condition never touch, so an inner interval is covered
    exactly when one outer interval contains it whole.
    """
    for inner_interval in inner['intervals']:

        # Look for one outer interval holding this inner one entirely ..
        for outer_interval in outer['intervals']:
            if _interval_contains(outer_interval, inner_interval):
                break

        # .. and give up on the first inner interval nothing holds.
        else:
            return False

    return True

# ################################################################################################################################

def _texts_overlap(first:'anydict', second:'anydict') -> 'bool':
    """ Whether two text constraints share at least one text.
    """
    first_includes = first['mode'] == Mode_Include
    second_includes = second['mode'] == Mode_Include

    # Two allowed sets overlap when they share a member ..
    if first_includes and second_includes:
        out = bool(first['values'] & second['values'])

    # .. an allowed set survives a forbidden one when something allowed is not forbidden ..
    elif first_includes:
        out = bool(first['values'] - second['values'])

    elif second_includes:
        out = bool(second['values'] - first['values'])

    # .. and two forbidden sets always overlap - the space of texts is unbounded.
    else:
        out = True

    return out

# ################################################################################################################################

def _texts_cover(outer:'anydict', inner:'anydict') -> 'bool':
    """ Whether one text constraint wholly contains another.
    """
    outer_includes = outer['mode'] == Mode_Include
    inner_includes = inner['mode'] == Mode_Include

    # An allowed set contains a smaller allowed set ..
    if outer_includes and inner_includes:
        out = inner['values'] <= outer['values']

    # .. a forbidden set contains an allowed set that avoids it entirely ..
    elif inner_includes:
        out = not (inner['values'] & outer['values'])

    # .. a forbidden set contains a forbidden superset of itself ..
    elif not outer_includes:
        out = outer['values'] <= inner['values']

    # .. and an allowed set never contains a forbidden one - texts are unbounded.
    else:
        out = False

    return out

# ################################################################################################################################
# ################################################################################################################################

def constraints_overlap(first:'anydict', second:'anydict') -> 'bool':
    """ Whether some single value satisfies both constraints.

    Unknown constraints overlap everything - a check may only report what it can prove.
    """
    first_kind = first['kind']
    second_kind = second['kind']

    # A blank cell or an unprovable one never rules an overlap out ..
    if first_kind in (ConstraintKind.Any, ConstraintKind.Unknown):
        return True

    if second_kind in (ConstraintKind.Any, ConstraintKind.Unknown):
        return True

    # .. constraints over different kinds of values never overlap ..
    if first_kind != second_kind:
        return False

    # .. and same-kind constraints compare by their own rules.
    if first_kind == ConstraintKind.Number:
        out = _numbers_overlap(first, second)

    elif first_kind == ConstraintKind.Text:
        out = _texts_overlap(first, second)

    else:
        out = bool(first['values'] & second['values'])

    return out

# ################################################################################################################################

def constraint_covers(outer:'anydict', inner:'anydict') -> 'bool':
    """ Whether every value satisfying the inner constraint also satisfies the outer one.

    Unknown constraints cover nothing and are covered by nothing except a blank cell -
    a check may only report what it can prove.
    """
    outer_kind = outer['kind']
    inner_kind = inner['kind']

    # A blank cell covers everything ..
    if outer_kind == ConstraintKind.Any:
        return True

    # .. nothing else covers a blank or an unprovable cell ..
    if inner_kind in (ConstraintKind.Any, ConstraintKind.Unknown):
        return False

    # .. an unprovable cell covers nothing ..
    if outer_kind == ConstraintKind.Unknown:
        return False

    # .. constraints over different kinds of values never cover each other ..
    if outer_kind != inner_kind:
        return False

    # .. and same-kind constraints compare by their own rules.
    if outer_kind == ConstraintKind.Number:
        out = _numbers_cover(outer, inner)

    elif outer_kind == ConstraintKind.Text:
        out = _texts_cover(outer, inner)

    else:
        out = inner['values'] <= outer['values']

    return out

# ################################################################################################################################
# ################################################################################################################################

def _numbers_cover_domain(constraints:'anylist') -> 'bool':
    """ Whether a union of numeric constraints covers the whole number line.
    """

    # Gather and order every interval by its low end ..
    intervals = []
    for constraint in constraints:
        intervals.extend(constraint['intervals'])

    def _interval_low(interval:'anydict') -> 'float':
        out = interval['low']
        return out

    intervals.sort(key=_interval_low)

    # .. the sweep has to start at the very bottom ..
    reach = Lowest
    reach_closed = False

    for interval in intervals:

        # .. an interval starting past the reach leaves a gap ..
        if interval['low'] > reach:
            return False

        # .. one starting exactly at the reach still needs the boundary point itself covered ..
        if interval['low'] == reach:
            has_boundary = reach_closed or interval['low_closed']

            # The bottom end of the line is not a real point, so no boundary is needed there.
            if reach != Lowest:
                if not has_boundary:
                    return False

        # .. and each interval extends the reach as far as it goes.
        if interval['high'] > reach:
            reach = interval['high']
            reach_closed = interval['high_closed']
        elif interval['high'] == reach:
            reach_closed = reach_closed or interval['high_closed']

    out = reach == Highest
    return out

# ################################################################################################################################

def _texts_cover_domain(constraints:'anylist') -> 'bool':
    """ Whether a union of text constraints covers every possible text.

    Only a forbidden set reaches the unbounded rest of the space, so coverage needs
    at least one and every text all of them forbid has to be allowed somewhere.
    """
    excludes = []
    included = set()

    for constraint in constraints:
        if constraint['mode'] == Mode_Exclude:
            excludes.append(constraint['values'])
        else:
            included |= constraint['values']

    if not excludes:
        return False

    # Only texts every forbidden set forbids are left uncovered by the excludes.
    still_forbidden = set(excludes[0])
    for values in excludes[1:]:
        still_forbidden &= values

    out = still_forbidden <= included
    return out

# ################################################################################################################################

def constraints_cover_domain(constraints:'anylist') -> 'boolnone':
    """ Whether the given constraints jointly cover every possible value, or None when unprovable.
    """
    kinds = set()
    for constraint in constraints:
        kinds.add(constraint['kind'])

    # A blank cell on its own covers everything.
    if ConstraintKind.Any in kinds:
        return True

    # An unprovable constraint makes the whole answer unprovable.
    if ConstraintKind.Unknown in kinds:
        return None

    # Mixed kinds live in different value spaces so neither covers the other's.
    if len(kinds) != 1:
        return False

    kind = kinds.pop()

    if kind == ConstraintKind.Number:
        out = _numbers_cover_domain(constraints)

    elif kind == ConstraintKind.Text:
        out = _texts_cover_domain(constraints)

    else:
        union = set()
        for constraint in constraints:
            union |= constraint['values']
        out = union == {True, False}

    return out

# ################################################################################################################################
# ################################################################################################################################
