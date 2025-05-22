# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

This file is a proprietary product, not an open-source one.
"""

# stdlib
import re

# ################################################################################################################################
# ################################################################################################################################

def convert_type_to_schema(type_hint:'str | None') -> 'dict | None':
    """ Converts a Python type hint to an OpenAPI schema.
    """
    # Handle None/null type
    if type_hint is None or type_hint == 'None':
        return {'type': 'null'}

    # Handle string type
    if type_hint == 'str' or type_hint == 'string':
        return {'type': 'string'}

    # Handle integer types
    if type_hint in ('int', 'integer'):
        return {'type': 'integer', 'format': 'int32'}

    # Handle floating point types
    if type_hint in ('float', 'decimal', 'Decimal'):
        return {'type': 'number', 'format': 'float'}

    # Handle boolean type
    if type_hint in ('bool', 'boolean'):
        return {'type': 'boolean'}

    # Handle array/list types
    list_match = re.match(r'(?:list|List|array)\[(.*?)\]', type_hint)
    if list_match:
        item_type = list_match.group(1).strip()
        item_schema = convert_type_to_schema(item_type)
        if item_schema:
            return {
                'type': 'array',
                'items': item_schema
            }

    # Handle dictionary/object types
    dict_match = re.match(r'(?:dict|Dict|object)\[(.*?),\s*(.*?)\]', type_hint)
    if dict_match:
        # For dictionaries, we only care about the value type for OpenAPI
        value_type = dict_match.group(2).strip()
        value_schema = convert_type_to_schema(value_type)
        if value_schema:
            return {
                'type': 'object',
                'additionalProperties': value_schema
            }

    # Handle optional types
    optional_match = re.match(r'(?:Optional|optional)\[(.*?)\]', type_hint)
    if optional_match:
        inner_type = optional_match.group(1).strip()
        inner_schema = convert_type_to_schema(inner_type)
        if inner_schema:
            # In OpenAPI, nullable is used for optional fields
            inner_schema['nullable'] = True
            return inner_schema

    # Handle Union types
    union_match = re.match(r'(?:Union|union)\[(.*?)\]', type_hint)
    if union_match:
        types = [t.strip() for t in union_match.group(1).split(',')]
        schemas = [convert_type_to_schema(t) for t in types if t != 'None']
        schemas = [s for s in schemas if s is not None]

        if 'None' in types or 'NoneType' in types:
            if len(schemas) == 1:
                # If it's just one type and None, make it nullable
                schemas[0]['nullable'] = True
                return schemas[0]

        if schemas:
            return {'oneOf': schemas}

    # Handle Any type
    if type_hint in ('any', 'Any', 'object'):
        return {}

    # For unknown types, assume they are references to models
    if type_hint not in ('', 'None', 'NoneType'):
        # Clean up the type name
        type_name = type_hint.strip('\'"')
        return {'$ref': f'#/components/schemas/{type_name}'}

    # Default to empty schema if we can't determine the type
    return {}

# ################################################################################################################################
# ################################################################################################################################
