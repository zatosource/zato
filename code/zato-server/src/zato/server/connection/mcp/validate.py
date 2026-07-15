# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, stranydict, strnone

# ################################################################################################################################
# ################################################################################################################################

# Error message returned when the arguments element is not a JSON object at all
_message_not_an_object = 'Invalid arguments: expected an object'

# What Python types satisfy each JSON Schema type that io_to_json_schema generates.
# A bool satisfies neither integer nor number even though bool subclasses int - that case
# is rejected explicitly before this mapping is consulted.
_json_type_to_python = {
    'string':  (str,),
    'integer': (int,),
    'number':  (int, float),
    'boolean': (bool,),
    'array':   (list,),
    'object':  (dict,),
}

# ################################################################################################################################
# ################################################################################################################################

def _join_path(path:'str', name:'str') -> 'str':
    """ Appends a field name to a dotted path, e.g. 'customer' + 'address' -> 'customer.address'.
    """

    if path:
        out = f'{path}.{name}'
    else:
        out = name

    return out

# ################################################################################################################################

def _validate_value(value:'any_', schema:'stranydict', path:'str') -> 'strnone':
    """ Validates one value against its JSON Schema fragment, recursing into arrays and objects.
    Returns None when the value matches or an error message naming the offending field.
    """

    expected = schema['type']

    # A bool subclasses int, so it would otherwise pass as an integer or a number ..
    if isinstance(value, bool):
        if expected in ('integer', 'number'):
            out = f'Invalid type for `{path}`: expected {expected}'
            return out

    # .. the type itself must match - a null never does, optional fields are expressed by absence ..
    python_types = _json_type_to_python[expected]

    if not isinstance(value, python_types):
        out = f'Invalid type for `{path}`: expected {expected}'
        return out

    # .. arrays with a declared element schema validate each element -
    # the type check above already proved the value is a list ..
    if isinstance(value, list):
        if 'items' in schema:
            for index, element in enumerate(value):
                if error := _validate_value(element, schema['items'], f'{path}[{index}]'):
                    return error

    # .. and objects recurse, which covers nested dataclass models.
    if isinstance(value, dict):
        out = _validate_object(value, schema, path)
        return out

    return None

# ################################################################################################################################

def _validate_object(value:'anydict', schema:'stranydict', path:'str') -> 'strnone':
    """ Validates a dict against an object schema - required keys present, no unknown keys,
    each value of the declared type. Returns None when valid or an error message.
    """

    # A schema with no declared properties describes a service with no declared input,
    # which accepts any arguments at all.
    if 'properties' not in schema:
        return None

    properties = schema['properties']

    # Schemas only carry the required list when at least one field is required.
    if 'required' in schema:
        required = schema['required']
    else:
        required = []

    # Every required field must be present ..
    for name in required:
        if name not in value:
            full_path = _join_path(path, name)
            out = f'Missing required parameter: `{full_path}`'
            return out

    # .. no field outside the schema is accepted ..
    for name, field_value in value.items():

        if name not in properties:
            full_path = _join_path(path, name)
            out = f'Unknown parameter: `{full_path}`'
            return out

        # .. and each value must match its declared type.
        if error := _validate_value(field_value, properties[name], _join_path(path, name)):
            return error

    return None

# ################################################################################################################################

def validate_arguments(arguments:'any_', schema:'stranydict') -> 'strnone':
    """ Validates tools/call arguments against a tool's inputSchema, the same schema
    that io_to_json_schema generates and tools/list advertises. Returns None when
    the arguments are valid or an error message naming the offending field.
    """

    # The arguments element itself must be a JSON object ..
    if not isinstance(arguments, dict):
        return _message_not_an_object

    # .. everything else is the recursive object check.
    out = _validate_object(arguments, schema, '')
    return out

# ################################################################################################################################
# ################################################################################################################################
