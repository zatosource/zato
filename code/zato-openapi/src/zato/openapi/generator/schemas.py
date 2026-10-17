# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

This file is a proprietary product, not an open-source one.
"""

# Zato
from zato.openapi.generator.annotation import JSON_Value_Types
from zato.openapi.generator.basic_types import Any_Type_Schema

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, callnone
    any_ = any_
    callnone = callnone

# ################################################################################################################################
# ################################################################################################################################

def make_nullable(schema:'anydict') -> 'anydict':
    """ Returns a schema that also accepts null, expressed the OpenAPI 3.1 way - references
    and composed schemas are wrapped in anyOf, plain schemas get null added to their type.
    """
    # References and composed schemas cannot have a type of their own ..
    if 'type' not in schema:
        out = {'anyOf': [schema, {'type': 'null'}]}
        return out

    # .. plain schemas express nullability with a type list.
    out = dict(schema)
    type_value = out['type']

    if isinstance(type_value, list):
        if 'null' not in type_value:
            out['type'] = type_value + ['null']
    elif type_value != 'null':
        out['type'] = [type_value, 'null']

    return out

# ################################################################################################################################

def get_enum_schema(values:'any_') -> 'anydict':
    """ Returns the schema of a value that is one of the given values, with the OpenAPI types that the values have.
    """
    schema_types:'any_' = []

    for value in values:
        value_type = type(value)
        schema_type = JSON_Value_Types[value_type]
        if schema_type not in schema_types:
            schema_types.append(schema_type)

    out:'anydict' = {'enum': values}
    type_count = len(schema_types)

    # Values of a single type have that type ..
    if type_count == 1:
        out['type'] = schema_types[0]

    # .. while values of several types have the list of them.
    else:
        out['type'] = schema_types

    return out

# ################################################################################################################################

def _get_array_schema(element_schema:'anydict') -> 'anydict':
    """ Returns the schema of a list or a tuple with elements of the given schema.
    """
    out = {'type': 'array', 'items': element_schema}
    return out

# ################################################################################################################################

def _get_set_schema(element_schema:'anydict') -> 'anydict':
    """ Returns the schema of a set with elements of the given schema.
    """
    out = {'type': 'array', 'items': element_schema, 'uniqueItems': True}
    return out

# ################################################################################################################################

def _get_dict_schema(element_schema:'anydict') -> 'anydict':
    """ Returns the schema of a dict with values of the given schema.
    """
    out:'anydict' = {'type': 'object'}

    # A dict of values of any type has no constraint on its values
    if element_schema != Any_Type_Schema:
        out['additionalProperties'] = element_schema

    return out

# ################################################################################################################################

# The builders of the schemas of containers, by the kind of a container
_container_schema_builders = {
    'list': _get_array_schema,
    'tuple': _get_array_schema,
    'set': _get_set_schema,
    'dict': _get_dict_schema,
}

# ################################################################################################################################

def get_container_schema_builder(kind:'any_') -> 'callnone':
    """ Returns the builder of the schemas of containers of the given kind, or None if the kind is not one of them.
    """
    out = _container_schema_builders.get(kind)
    return out

# ################################################################################################################################
# ################################################################################################################################
