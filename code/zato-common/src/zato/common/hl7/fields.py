# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from typing import NamedTuple

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, strtuple

    anydict = anydict
    strtuple = strtuple

# ################################################################################################################################
# ################################################################################################################################

class ConnectionField(NamedTuple):
    """ One configuration field of a channel or an outgoing connection, no matter the protocol.
    """

    # The key the field is stored, imported and exported under
    name: 'str'

    # The value in force when neither the Dashboard nor enmasse supplies one
    default: 'any_'

    # Whether the field has a column of its own in generic_conn - everything else lives in the opaque blob
    is_column: 'bool' = False

# ################################################################################################################################
# ################################################################################################################################

field_list = list[ConnectionField]

# ################################################################################################################################
# ################################################################################################################################

def get_column_defaults(fields:'field_list') -> 'anydict':
    """ The defaults of the fields that generic_conn stores in a column of their own.
    """
    out:'anydict' = {}

    for field in fields:
        if field.is_column:
            out[field.name] = field.default

    return out

# ################################################################################################################################

def get_opaque_defaults(fields:'field_list') -> 'anydict':
    """ The defaults of the fields that generic_conn stores in its opaque blob.
    """
    out:'anydict' = {}

    for field in fields:
        if not field.is_column:
            out[field.name] = field.default

    return out

# ################################################################################################################################

def get_defaults(fields:'field_list') -> 'anydict':
    """ The defaults of every field, no matter where it is stored.
    """
    out:'anydict' = {}

    for field in fields:
        out[field.name] = field.default

    return out

# ################################################################################################################################

def get_int_names(fields:'field_list') -> 'strtuple':
    """ The names of the fields holding a whole number, which the Dashboard and opaque storage
    may both hand over as text.
    """
    names = []

    for field in fields:
        is_bool = isinstance(field.default, bool)
        if isinstance(field.default, int):
            if not is_bool:
                names.append(field.name)

    out = tuple(names)
    return out

# ################################################################################################################################

def get_names(fields:'field_list') -> 'strtuple':
    """ The names of every field, in declaration order.
    """
    names = []

    for field in fields:
        names.append(field.name)

    out = tuple(names)
    return out

# ################################################################################################################################
# ################################################################################################################################
