# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.audit_log.common import Attr_Value_Max_Len

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist, stranydict

# ################################################################################################################################
# ################################################################################################################################

def build_attr_rows(event_id:'int', attrs:'stranydict') -> 'anylist':
    """ Turns an attribute dict into rows - every value is stored as capped text
    and numbers additionally go to the numeric column for aggregation queries.
    """
    out:'anylist' = []

    for name, value in attrs.items():

        row:'stranydict' = {
            'event_id': event_id,
            'name': name,
            'value': '',
            'value_number': None,
        }

        # Real numbers are stored twice, and everything else is text -
        # numeric-looking strings such as identifiers with leading zeros stay text only.
        if isinstance(value, bool):
            row['value'] = str(value)
        elif isinstance(value, (int, float)):
            row['value'] = str(value)
            row['value_number'] = value
        else:
            value = str(value)
            row['value'] = value[:Attr_Value_Max_Len]

        out.append(row)

    return out

# ################################################################################################################################
# ################################################################################################################################
