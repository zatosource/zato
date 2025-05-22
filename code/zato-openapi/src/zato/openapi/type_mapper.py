# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

This file is a proprietary product, not an open-source one.
"""

# stdlib
import datetime
import inspect
from decimal import Decimal
from typing import Any, Dict, List, Optional, Set, Tuple, Union

# Zato
from zato.common.typing_ import (
    any_, anydict, anylist, bytesnone, datetime_, datetimez, decimal_,
    intnone, list_, optional, strnone, union_
)

# ################################################################################################################################
# ################################################################################################################################

# Basic type mappings from Zato types to OpenAPI types
BASIC_TYPE_MAPPINGS = {
    str: {'type': 'string'},
    int: {'type': 'integer', 'format': 'int64'},
    float: {'type': 'number', 'format': 'float'},
    bool: {'type': 'boolean'},
    datetime.datetime: {'type': 'string', 'format': 'date-time'},
    datetime.date: {'type': 'string', 'format': 'date'},
    Decimal: {'type': 'number'},
    bytes: {'type': 'string', 'format': 'binary'},
    list: {'type': 'array'},
    dict: {'type': 'object'},
    set: {'type': 'array', 'uniqueItems': True},
    tuple: {'type': 'array'},

    # Zato specific types
    datetime_: {'type': 'string', 'format': 'date-time'},
    datetimez: {'type': 'string', 'format': 'date-time'},
    decimal_: {'type': 'number'},
    bytesnone: {'type': 'string', 'format': 'binary', 'nullable': True},
    strnone: {'type': 'string', 'nullable': True},
    intnone: {'type': 'integer', 'format': 'int64', 'nullable': True},
}

# ################################################################################################################################
# ################################################################################################################################

def map_zato_type_to_openapi(zato_type: Any) -> Dict[str, Any]:
    """Map a Zato type to its OpenAPI equivalent."""

    # Handle direct mappings
    if zato_type in BASIC_TYPE_MAPPINGS:
        return BASIC_TYPE_MAPPINGS[zato_type]

    # Handle string type names
    if isinstance(zato_type, str):
        if zato_type in ['str', 'string']:
            return {'type': 'string'}
        elif zato_type in ['int', 'integer']:
            return {'type': 'integer', 'format': 'int64'}
        elif zato_type in ['float', 'number']:
            return {'type': 'number', 'format': 'float'}
        elif zato_type in ['bool', 'boolean']:
            return {'type': 'boolean'}
        elif zato_type in ['datetime', 'date-time']:
            return {'type': 'string', 'format': 'date-time'}
        elif zato_type in ['date']:
            return {'type': 'string', 'format': 'date'}
        elif zato_type in ['decimal']:
            return {'type': 'number'}
        elif zato_type in ['bytes', 'binary']:
            return {'type': 'string', 'format': 'binary'}
        # Handle model references
        else:
            return {'$ref': f'#/components/schemas/{zato_type}'}

    # Handle Union types (optional fields)
    if hasattr(zato_type, '__origin__') and zato_type.__origin__ is Union:
        # Check if it's an optional type (Union with None)
        args = zato_type.__args__
        if type(None) in args:
            # Get the non-None type
            non_none_types = [t for t in args if t is not type(None)]
            if non_none_types:
                result = map_zato_type_to_openapi(non_none_types[0])
                result['nullable'] = True
                return result
        # If it's a regular union, use the first type as default
        return map_zato_type_to_openapi(args[0])

    # Handle List types
    if hasattr(zato_type, '__origin__') and zato_type.__origin__ in (list, List):
        item_type = zato_type.__args__[0] if zato_type.__args__ else Any
        return {
            'type': 'array',
            'items': map_zato_type_to_openapi(item_type)
        }

    # Handle Dict types
    if hasattr(zato_type, '__origin__') and zato_type.__origin__ in (dict, Dict):
        return {'type': 'object'}

    # Handle Optional types
    if hasattr(zato_type, '__origin__') and zato_type.__origin__ is optional:
        base_type = zato_type.__args__[0]
        result = map_zato_type_to_openapi(base_type)
        result['nullable'] = True
        return result

    # Handle list_ types
    if hasattr(zato_type, '__origin__') and getattr(zato_type.__origin__, '__name__', '') == 'list_':
        item_type = zato_type.__args__[0] if zato_type.__args__ else Any
        return {
            'type': 'array',
            'items': map_zato_type_to_openapi(item_type)
        }

    # Default to string if type cannot be determined
    return {'type': 'string'}

# ################################################################################################################################
# ################################################################################################################################
