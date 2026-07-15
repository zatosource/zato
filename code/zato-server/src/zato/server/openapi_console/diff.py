# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, strlist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# The content type under which operations carry their schemas
_content_type = 'application/json'

# The name under which each operation's flattened request fields are kept in a contract
_request_key = 'request'

# The name under which each operation's flattened response fields are kept in a contract
_response_key = 'response'

# ################################################################################################################################
# ################################################################################################################################

def _type_name(schema:'anydict') -> 'str':
    """ Returns a normalized type name for a schema - OpenAPI 3.1 nullable type lists
    are reduced to their non-null member so that adding or removing nullability alone
    does not read as a type change.
    """
    schema_type = schema.get('type')

    # A type list is the OpenAPI 3.1 spelling of a nullable type
    if isinstance(schema_type, list):
        non_null = [item for item in schema_type if item != 'null']
        return '|'.join(non_null)

    if schema_type:
        return schema_type

    return 'any'

# ################################################################################################################################

def _resolve_ref(schema:'anydict', schemas:'anydict') -> 'anydict':
    """ Returns the component schema a reference points to, or the schema itself when it is not a reference.
    Nullable references are spelled as anyOf with a null member, which resolves to the non-null member.
    """
    if ref := schema.get('$ref'):
        schema_name = ref.rsplit('/', 1)[1]

        # A reference may point to a schema the document no longer carries
        if schema_name in schemas:
            return schemas[schema_name]
        return {}

    if any_of := schema.get('anyOf'):
        for member in any_of:
            if member.get('type') != 'null':
                return _resolve_ref(member, schemas)

    return schema

# ################################################################################################################################

def _flatten_fields(schema:'anydict', schemas:'anydict', prefix:'str', out:'anydict', visited:'any_') -> 'None':
    """ Walks a schema and records every field as a dotted path mapped to its type name.
    References are resolved against the component schemas, with a visited set breaking reference cycles.
    """
    schema = _resolve_ref(schema, schemas)

    # Arrays are flattened through to their element type
    if schema.get('type') == 'array':
        items = schema.get('items')
        if items:
            _flatten_fields(items, schemas, prefix, out, visited)
        return

    properties = schema.get('properties')

    # A schema without properties is a leaf - a scalar or an untyped object
    if not properties:
        if prefix:
            out[prefix] = _type_name(schema)
        return

    for field_name, field_schema in properties.items():

        if prefix:
            field_path = f'{prefix}.{field_name}'
        else:
            field_path = field_name

        resolved = _resolve_ref(field_schema, schemas)

        # A reference already seen on this path means a cycle, which ends the walk here
        marker = id(resolved)
        if marker in visited:
            out[field_path] = 'object'
            continue

        # Nested objects and arrays of objects contribute their own fields ..
        if resolved.get('properties') or resolved.get('type') == 'array':
            visited.add(marker)
            _flatten_fields(field_schema, schemas, field_path, out, visited)
            visited.discard(marker)

        # .. and scalars are leaves.
        else:
            out[field_path] = _type_name(resolved)

# ################################################################################################################################

def _operation_fields(operation:'anydict', schemas:'anydict') -> 'anydict':
    """ Returns the flattened request and response fields of a single operation.
    """
    out = {_request_key: {}, _response_key: {}}

    if request_body := operation.get('requestBody'):
        request_schema = request_body['content'][_content_type]['schema']
        _flatten_fields(request_schema, schemas, '', out[_request_key], set())

    response_content = operation['responses']['200'].get('content')
    if response_content:
        response_schema = response_content[_content_type]['schema']
        _flatten_fields(response_schema, schemas, '', out[_response_key], set())

    return out

# ################################################################################################################################

def _build_contract(spec:'anydict') -> 'anydict':
    """ Turns a document into a flat contract - a map of (path, method) to that operation's
    flattened request and response fields, which is what the diff compares.
    """
    out = {}
    schemas = spec['components']['schemas']

    for path, path_item in spec['paths'].items():
        for http_method, operation in path_item.items():
            out[(path, http_method)] = _operation_fields(operation, schemas)

    return out

# ################################################################################################################################

def get_breaking_changes(old_spec:'anydict', new_spec:'anydict') -> 'strlist':
    """ Compares two documents and returns human-readable descriptions of the breaking changes
    the new one introduces - removed endpoints, removed fields and type changes.
    """
    old_contract = _build_contract(old_spec)
    new_contract = _build_contract(new_spec)

    out = []

    for endpoint, old_fields in sorted(old_contract.items()):

        path, http_method = endpoint
        endpoint_label = f'{http_method.upper()} {path}'

        # An endpoint that is gone is the biggest breaking change there is
        if endpoint not in new_contract:
            out.append(f'endpoint removed: {endpoint_label}')
            continue

        new_fields = new_contract[endpoint]

        # Both directions are compared the same way - fields that disappeared and fields whose type changed
        for direction in (_request_key, _response_key):

            old_direction = old_fields[direction]
            new_direction = new_fields[direction]

            for field_path, old_type in sorted(old_direction.items()):

                if field_path not in new_direction:
                    out.append(f'{direction} field removed: {field_path} in {endpoint_label}')
                    continue

                new_type = new_direction[field_path]
                if new_type != old_type:
                    out.append(f'{direction} field type changed: {field_path} in {endpoint_label} - {old_type} -> {new_type}')

    return out

# ################################################################################################################################

def report_breaking_changes(old_spec:'anydict', new_spec:'anydict') -> 'None':
    """ Logs the breaking changes between the previous document and the new one, so they show up
    in the deploy output. No output means no breaking changes.
    """
    changes = get_breaking_changes(old_spec, new_spec)

    for change in changes:
        logger.warning('OpenAPI breaking change: %s', change)

# ################################################################################################################################
# ################################################################################################################################
