# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json

# Zato
from zato.common.typing_ import cast_

# Local
from .data import anydict
from .errors import InvalidDocumentError

# ################################################################################################################################
# ################################################################################################################################

JSON_Separators = (',', ':')

# ################################################################################################################################
# ################################################################################################################################

def serialize_document(document:'anydict') -> 'str':
    """ Serializes one complete rule document into its canonical TEXT representation.
    """
    # Encode keys in a stable order so equal documents always have equal stored text ..
    try:
        out = json.dumps(document, ensure_ascii=False, separators=JSON_Separators, sort_keys=True)

    # .. and translate representation failures into the layer's public error.
    except (TypeError, ValueError) as e:
        message = f'Rule document is not valid JSON -> {e}'
        raise InvalidDocumentError(message) from e

    return out

# ################################################################################################################################

def deserialize_document(document:'str') -> 'anydict':
    """ Deserializes one complete rule document from TEXT.
    """
    # Decode the complete stored document ..
    try:
        value = json.loads(document)

    # .. and translate corrupt storage into the layer's public error.
    except json.JSONDecodeError as e:
        message = f'Stored rule document is not valid JSON -> {e}'
        raise InvalidDocumentError(message) from e

    # .. enforce the definition contract at the storage boundary ..
    value_is_dict = isinstance(value, dict)
    if not value_is_dict:
        raise InvalidDocumentError('Stored rule document must be a JSON object')

    # .. and return the typed document.
    out = cast_(anydict, value)
    return out

# ################################################################################################################################
# ################################################################################################################################
