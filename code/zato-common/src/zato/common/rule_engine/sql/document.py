# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import hashlib
import json

# Zato
from zato.common.typing_ import cast_

# Local
from .data import any_, anydict, strlist
from .errors import InvalidDocumentError

# ################################################################################################################################
# ################################################################################################################################

JSON_Separators = (',', ':')

# The character encoding the content hash is computed over, fixed so an approval binds to identical bytes everywhere.
Content_Hash_Encoding = 'utf-8'

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

def content_hash(document_text:'str') -> 'str':
    """ Returns the SHA-256 hex digest binding an approval to one exact serialized document.
    """
    # Hash the canonical TEXT the version already stores, so the approved bytes equal the published bytes ..
    encoded = document_text.encode(Content_Hash_Encoding)
    digest = hashlib.sha256(encoded)

    # .. and return the stable hex form recorded on the approval.
    out = digest.hexdigest()
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

def serialize_string_list(values:'strlist') -> 'str':
    """ Serializes a compact list of stable rule identifiers.
    """
    # Preserve list order while removing insignificant whitespace ..
    try:
        out = json.dumps(values, ensure_ascii=False, separators=JSON_Separators)

    # .. and translate representation failures into the layer's public error.
    except (TypeError, ValueError) as e:
        message = f'Rule identifier list is not valid JSON -> {e}'
        raise InvalidDocumentError(message) from e

    return out

# ################################################################################################################################

def deserialize_string_list(values:'str') -> 'strlist':
    """ Deserializes a compact list of stable rule identifiers.
    """
    # Decode the compact promoted list ..
    try:
        value:'any_' = json.loads(values)

    # .. and translate corrupt storage into the layer's public error.
    except json.JSONDecodeError as e:
        message = f'Stored rule identifier list is not valid JSON -> {e}'
        raise InvalidDocumentError(message) from e

    # .. enforce the promoted-column container contract at the storage boundary ..
    value_is_list = isinstance(value, list)
    if not value_is_list:
        raise InvalidDocumentError('Stored rule identifier list must be a JSON list')

    # .. enforce each stable identifier's type ..
    for rule_id in value:
        rule_id_is_string = isinstance(rule_id, str)
        if not rule_id_is_string:
            raise InvalidDocumentError('Stored rule identifier list must contain strings only')

    # .. and return the typed list.
    out = cast_(strlist, value)
    return out

# ################################################################################################################################
# ################################################################################################################################
