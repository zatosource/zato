# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The one check every numeric alert setting passes before it is stored, whichever way it arrives - through the
# generic connection services or through enmasse. A threshold is a count, a share, a number of seconds, an amount
# or a size, and each of them is a number that is not negative - a `max_tools` of -1 or a `volume_budget` of
# `lots` is refused with a message naming the field.

from __future__ import annotations

# Zato
from zato.common.alerting import config_map
from zato.common.alerting.object_config import get_field_kinds

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict
    anydict = anydict

# ################################################################################################################################
# ################################################################################################################################

# The kinds whose value is a number - a toggle is a boolean, a text is a string and the slots are a list
_number_kinds = (
    config_map.Kind_Number,
    config_map.Kind_Duration,
    config_map.Kind_Seconds,
    config_map.Kind_Amount,
    config_map.Kind_Size,
)

# ################################################################################################################################
# ################################################################################################################################

def validate_number_settings(alert_type:'str', values:'anydict') -> 'None':
    """ Refuses, with a ValueError naming the field, any numeric setting among the values that is not a number
    or is negative - the values keyed by field name, only the ones present being checked.
    """
    kinds = get_field_kinds(alert_type)

    for name, value in values.items():

        # A field outside the type is someone else's to refuse
        if name not in kinds:
            continue

        if kinds[name] not in _number_kinds:
            continue

        # A boolean is a number to Python and to no one else
        is_number = isinstance(value, (int, float)) and not isinstance(value, bool)

        if not is_number:
            raise ValueError(f'Alert setting `{name}` must be a number, not `{value}`')

        if value < 0:
            raise ValueError(f'Alert setting `{name}` must not be negative, not `{value}`')

# ################################################################################################################################
# ################################################################################################################################
