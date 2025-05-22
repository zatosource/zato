# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

This file is a proprietary product, not an open-source one.
"""

# stdlib
import inspect
from typing import Any, Dict, List, Optional, Type, Union

# Zato
from zato.common.typing_ import any_, anydict, list_, optional, strnone, union_
from zato.server.service import Model

# ################################################################################################################################
# ################################################################################################################################

def is_optional_type(field_type):
    """ Determines if a type is Optional[T]. """
    return (
        hasattr(field_type, '__origin__') and 
        field_type.__origin__ is union_ and 
        type(None) in field_type.__args__
    )

# ################################################################################################################################

def extract_optional_type(field_type):
    """ Extracts the type T from Optional[T]. """
    if not is_optional_type(field_type):
        return field_type
        
    for arg in field_type.__args__:
        if arg is not type(None):  # noqa
            return arg
            
    return str  # Default to string if no type found

# ################################################################################################################################

def convert_type_to_schema(field_type, is_model_class_fn=None):
    """ Converts a Python type to an OpenAPI schema. """
    
    # Handle Optional types
    if is_optional_type(field_type):
        return convert_type_to_schema(extract_optional_type(field_type), is_model_class_fn)
    
    # Basic types
    type_mapping = {
        str: {'type': 'string'},
        int: {'type': 'integer'},
        float: {'type': 'number'},
        bool: {'type': 'boolean'},
        list: {'type': 'array', 'items': {}},
        dict: {'type': 'object'}
    }
    
    # Check for direct type matches
    if field_type in type_mapping:
        return type_mapping[field_type]
    
    # Check for type name matches (for imported types)
    type_name = getattr(field_type, '__name__', '')
    for py_type, schema in type_mapping.items():
        if type_name == py_type.__name__:
            return schema
    
    # Handle List[T] types
    if hasattr(field_type, '__origin__') and field_type.__origin__ is list:
        item_type = field_type.__args__[0]
        return {
            'type': 'array',
            'items': convert_type_to_schema(item_type, is_model_class_fn)
        }
    
    # Handle Dict[K, V] types
    if hasattr(field_type, '__origin__') and field_type.__origin__ is dict:
        return {'type': 'object'}
    
    # Handle custom model types
    if inspect.isclass(field_type) and is_model_class_fn and is_model_class_fn(field_type):
        model_name = field_type.__name__
        return {'$ref': f'#/components/schemas/{model_name}'}
    
    # Special Zato types
    zato_type_mapping = {
        'strnone': {'type': 'string'},
        'intnone': {'type': 'integer'},
        'floatnone': {'type': 'number'},
        'boolnone': {'type': 'boolean'},
        'datetime_': {'type': 'string', 'format': 'date-time'},
        'date_': {'type': 'string', 'format': 'date'},
        'bytesnone': {'type': 'string', 'format': 'binary'},
    }
    
    # Check for Zato type name matches
    if type_name in zato_type_mapping:
        return zato_type_mapping[type_name]
    
    # Default to string for unknown types
    return {'type': 'string'}

# ################################################################################################################################
# ################################################################################################################################

def extract_model_fields(model_class, type_hints):
    """ Extracts field information from a model class. """
    properties = {}
    required = []
    
    for field_name, field_type in type_hints.items():
        # Skip internal fields
        if field_name.startswith('_'):
            continue
        
        # Determine if field is required
        is_optional = is_optional_type(field_type)
        has_default = hasattr(model_class, field_name) and getattr(model_class, field_name) is not None
        
        if not is_optional and not has_default:
            required.append(field_name)
        
        # Convert field type to OpenAPI schema
        properties[field_name] = convert_type_to_schema(
            field_type, 
            lambda cls: inspect.isclass(cls) and issubclass(cls, Model)
        )
    
    return properties, required

# ################################################################################################################################
# ################################################################################################################################
