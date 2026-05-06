# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import dataclasses
import types
from datetime import date as stdlib_date
from datetime import datetime as stdlib_datetime
from decimal import Decimal as stdlib_Decimal
from logging import getLogger
from typing import get_args, get_origin, Union
from uuid import UUID as stdlib_UUID

# Zato
from zato.common.marshal_.simpleio import DataClassSimpleIO
from zato.cy.simpleio import AsIs, Bool, CSV, CySimpleIO, Date, DateTime, Decimal, Dict, DictList, Elem, Float, \
    Int, List, Secret, Text, UTC, UUID

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, stranydict
    from zato.cy.simpleio import SIODefinition

    SIODefinition = SIODefinition

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato')

# ################################################################################################################################
# ################################################################################################################################

# Maps each CySimpleIO Elem subclass to the JSON Schema dict
# that describes values of that type in an MCP tool's inputSchema.
_elem_class_to_json_schema:'anydict' = {
    AsIs:     {'type': 'string'},
    Bool:     {'type': 'boolean'},
    CSV:      {'type': 'string'},
    Date:     {'type': 'string', 'format': 'date'},
    DateTime: {'type': 'string', 'format': 'date-time'},
    Decimal:  {'type': 'string'},
    Dict:     {'type': 'object'},
    DictList: {'type': 'array', 'items': {'type': 'object'}},
    Float:    {'type': 'number'},
    Int:      {'type': 'integer'},
    List:     {'type': 'array'},
    Secret:   {'type': 'string'},
    Text:     {'type': 'string'},
    UTC:      {'type': 'string', 'format': 'date-time'},
    UUID:     {'type': 'string', 'format': 'uuid'},
}

# Default for unknown or user-defined Elem subclasses
_default_elem_schema:'stranydict' = {'type': 'string'}

# Python type annotation to JSON Schema mapping for dataclass-based IO
_python_type_to_json_schema:'anydict' = {
    str:              {'type': 'string'},
    int:              {'type': 'integer'},
    float:            {'type': 'number'},
    bool:             {'type': 'boolean'},
    list:             {'type': 'array'},
    dict:             {'type': 'object'},
    stdlib_date:      {'type': 'string', 'format': 'date'},
    stdlib_datetime:  {'type': 'string', 'format': 'date-time'},
    stdlib_Decimal:   {'type': 'string'},
    stdlib_UUID:      {'type': 'string', 'format': 'uuid'},
}

# ################################################################################################################################
# ################################################################################################################################

def _get_elem_json_schema(elem:'Elem') -> 'stranydict':
    """ Returns the JSON Schema fragment for a single CySimpleIO Elem instance.
    Looks up the elem's class in the mapping, uses default for unknown types.
    """

    # Try the exact class first ..
    elem_class = type(elem)
    schema = _elem_class_to_json_schema.get(elem_class)

    if schema:
        out = dict(schema)
        return out

    # .. walk the MRO for subclasses of known types ..
    for parent_class in elem_class.__mro__:
        schema = _elem_class_to_json_schema.get(parent_class)

        if schema:
            out = dict(schema)
            return out

    # .. otherwise use the default.
    out = dict(_default_elem_schema)
    return out

# ################################################################################################################################
# ################################################################################################################################

def cy_sio_to_schema(definition:'SIODefinition') -> 'stranydict':
    """ Converts a CySimpleIO SIODefinition into a JSON Schema dict.
    Walks the required and optional input element lists,
    maps each Elem to its JSON Schema type, and builds the schema.
    """

    # Our response to produce
    out:'stranydict' = {'type': 'object'}

    # Check if there is any input declared at all ..
    if not definition.has_input_declared:
        return out

    properties:'stranydict' = {}
    required:'list[str]' = []

    # .. collect required input elements ..
    required_elems = definition.get_input_required()

    for elem in required_elems:
        properties[elem.name] = _get_elem_json_schema(elem)
        required.append(elem.name)

    # .. collect optional input elements ..
    optional_elems = definition.get_input_optional()

    for elem in optional_elems:
        properties[elem.name] = _get_elem_json_schema(elem)

    # .. only include properties and required if we have any.
    if properties:
        out['properties'] = properties

    if required:
        out['required'] = sorted(required)

    return out

# ################################################################################################################################
# ################################################################################################################################

def _python_annotation_to_schema(annotation:'any_') -> 'stranydict':
    """ Converts a Python type annotation to a JSON Schema dict.
    Handles basic types, Optional, List[T], and nested dataclasses.
    """

    # Check if it's a direct match in the mapping ..
    schema = _python_type_to_json_schema.get(annotation)

    if schema:
        out = dict(schema)
        return out

    # .. handle generic types like Optional[T], List[T], Dict[str, T] ..
    origin = get_origin(annotation)

    # Both typing.Union and the X | Y syntax (types.UnionType) need handling
    if origin is Union or isinstance(annotation, types.UnionType):

        args = get_args(annotation)

        # Optional[T] is Union[T, None] ..
        non_none_args:'list' = []

        for arg in args:
            if arg is not type(None):
                non_none_args.append(arg)

        if len(non_none_args) == 1:
            out = _python_annotation_to_schema(non_none_args[0])
            return out

        # .. multi-type Union uses string as the default.
        out:'stranydict' = {'type': 'string'}
        return out

    if origin is list:

        args = get_args(annotation)

        if args:
            items_schema = _python_annotation_to_schema(args[0])
            out:'stranydict' = {'type': 'array', 'items': items_schema}
            return out

        out:'stranydict' = {'type': 'array'}
        return out

    if origin is dict:
        out:'stranydict' = {'type': 'object'}
        return out

    # .. handle nested dataclasses ..
    if dataclasses.is_dataclass(annotation):
        if isinstance(annotation, type):
            out = dataclass_model_to_schema(annotation)
            return out

    # .. unknown type uses string as the default.
    out:'stranydict' = {'type': 'string'}
    return out

# ################################################################################################################################
# ################################################################################################################################

def _is_field_required(field:'dataclasses.Field', annotation:'any_') -> 'bool':
    """ A dataclass field is required if it has no default, no default_factory,
    and its type is not Optional.
    """

    # If it has a default value, it is not required ..
    if field.default is not dataclasses.MISSING:
        return False

    # .. same for default_factory ..
    if field.default_factory is not dataclasses.MISSING: # pyright: ignore[reportArgumentType]
        return False

    # .. if the type is Optional[T] (Union[T, None]) or T | None, it is not required.
    origin = get_origin(annotation)

    if origin is Union or isinstance(annotation, types.UnionType):

        args = get_args(annotation)

        for arg in args:
            if arg is type(None):
                return False

    return True

# ################################################################################################################################
# ################################################################################################################################

def dataclass_model_to_schema(input_class:'type') -> 'stranydict':
    """ Converts a dataclass class to a JSON Schema dict.
    Walks dataclasses.fields() and __annotations__ to build properties and required lists.
    """

    # Our response to produce
    out:'stranydict' = {'type': 'object'}

    fields = dataclasses.fields(input_class)

    if not fields:
        return out

    annotations = input_class.__annotations__

    properties:'stranydict' = {}
    required:'list[str]' = []

    for field in fields:
        annotation = annotations[field.name]
        properties[field.name] = _python_annotation_to_schema(annotation)

        if _is_field_required(field, annotation):
            required.append(field.name)

    out['properties'] = properties

    if required:
        out['required'] = sorted(required)

    return out

# ################################################################################################################################
# ################################################################################################################################

def sio_to_json_schema(service_class:'any_') -> 'stranydict':
    """ Top-level dispatcher. Takes a service class and returns a JSON Schema dict
    for its input, suitable for use as an MCP tool's inputSchema.
    """
    sio = getattr(service_class, '_sio', None)

    if sio is None:
        out:'stranydict' = {'type': 'object'}
        return out

    if isinstance(sio, DataClassSimpleIO):
        out = dataclass_model_to_schema(sio.user_declaration.input)
        return out

    if isinstance(sio, CySimpleIO):
        out = cy_sio_to_schema(sio.definition)
        return out

    out:'stranydict' = {'type': 'object'}
    return out

# ################################################################################################################################
# ################################################################################################################################
