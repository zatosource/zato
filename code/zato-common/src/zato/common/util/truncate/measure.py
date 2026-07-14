# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import dumps

# Zato
from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

# The canonical serializer settings - every size measured in this module uses exactly these,
# so per-element arithmetic in the trimming loop matches the final output byte for byte.
_Serializer_Separators = (',', ':')

# ################################################################################################################################
# ################################################################################################################################

def serialize(value:'any_') -> 'str':
    """ Serializes a value to its canonical JSON form.
    """
    out = dumps(value, ensure_ascii=False, separators=_Serializer_Separators)

    return out

# ################################################################################################################################
# ################################################################################################################################

def get_size(value:'any_') -> 'int':
    """ Returns the size in bytes of the canonical JSON form of a value.
    """
    serialized = serialize(value)
    encoded = serialized.encode('utf-8')

    out = len(encoded)

    return out

# ################################################################################################################################
# ################################################################################################################################
