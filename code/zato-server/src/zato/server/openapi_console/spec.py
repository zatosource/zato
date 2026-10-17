# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import typing
from inspect import isclass

# Zato
from zato.common.api import HTTP_SOAP, URL_TYPE
from zato.common.typing_ import cast_
from zato.openapi.generator.io_scanner import TypeMapper, extract_model_fields_recursive, get_element_info
from zato.openapi.generator.openapi_ import OpenAPIGenerator

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, dictlist, intnone, intset, stranydict, tuple_
    from zato.server.base.parallel import ParallelServer

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# The document title that the console shows for every spec
_spec_title = 'Zato API'

# The HTTP method used when a service has no method-specific handlers
_default_http_method = 'post'

# The Accept value of channels that every request reaches, whatever it accepts
_accept_any = HTTP_SOAP.ACCEPT.ANY

# ################################################################################################################################
# ################################################################################################################################

def _io_from_string(value:'str') -> 'anydict':
    """ Turns a single string input or output declaration into a generator definition,
    with the type that the server gives the element.
    """
    element = get_element_info(value)

    out = {
        'type': 'string',
        'name': element['name'],
        'required': element['required'],
        'schema_type': element['schema_type'],
    }

    return out

# ################################################################################################################################

def _io_from_sequence(value:'any_') -> 'anydict':
    """ Turns a tuple or list of input or output elements into a generator definition.
    Elements are either plain strings or typed elements, each with the type that the server gives it.
    """
    elements = []

    for item in value:
        element = get_element_info(item)
        elements.append(element)

    out = {'type': 'tuple', 'elements': elements}

    return out

# ################################################################################################################################

def _io_definition(value:'any_', models:'stranydict') -> 'anydict':
    """ Converts a service's runtime input or output attribute into the definition format the generator consumes.
    Models referenced by the attribute are extracted into the shared models dictionary.
    """
    # No typed I/O means any JSON object is accepted or returned
    if value is None:
        out = {'type': 'any'}

    # A single string element
    elif isinstance(value, str):
        out = _io_from_string(value)

    # A tuple or list of elements
    elif isinstance(value, (tuple, list)):
        out = _io_from_sequence(value)

    # A dataclass-based model
    elif isclass(value):
        extract_model_fields_recursive(value, models)
        out = {'type': 'model', 'model_name': value.__name__}

    # A generic alias such as list_[Model]
    elif typing.get_origin(value) is list:
        args = typing.get_args(value)
        element = args[0]
        extract_model_fields_recursive(element, models)
        out = {
            'type': 'container',
            'container_type': 'list_',
            'element_type': element.__name__,
        }

    # .. anything else is documented as an untyped JSON object.
    else:
        out = {'type': 'any'}

    return out

# ################################################################################################################################

def is_channel_documented(channel_item:'anydict') -> 'bool':
    """ Whether a channel is one that OpenAPI documents describe, which are the only channels
    the console can invoke too.
    """
    # Only active, non-internal REST channels are documented ..
    if channel_item['connection'] != 'channel':
        return False

    if channel_item['transport'] != URL_TYPE.PLAIN_HTTP:
        return False

    if not channel_item['is_active']:
        return False

    if channel_item['is_internal']:
        return False

    # .. channels without a service of their own are skipped ..
    if not channel_item['service_name']:
        return False

    # .. and channels can opt out of OpenAPI documents - only an explicit off flag excludes them,
    # channels that predate the flag have no value and are included.
    if channel_item.get('should_include_in_openapi') is False:
        return False

    return True

# ################################################################################################################################

def get_accepted_security_id(channel_item:'anydict', security_ids:'intset') -> 'intnone':
    """ Returns the ID of the one among the given security definitions that the channel accepts,
    or None if the channel accepts none of them.
    """
    security_groups_ctx = channel_item.get('security_groups_ctx')

    # Security groups with members apply alongside the channel's own definition, if it has one ..
    if security_groups_ctx:
        has_group_members = security_groups_ctx.has_members()
    else:
        has_group_members = False

    # .. a channel with a definition of its own accepts only that definition ..
    if channel_security_id := channel_item.get('security_id'):
        if channel_security_id not in security_ids:
            return None
        candidates = [channel_security_id]

    # .. a channel with group members accepts each member, in the order of their IDs ..
    elif has_group_members:
        candidates = sorted(security_ids)

    # .. and a channel with neither a definition nor group members accepts no console caller.
    else:
        return None

    if not has_group_members:
        return channel_security_id

    # The definition, if there is one, has to be a member of one of the groups too,
    # which exist whenever they have members.
    security_groups_ctx = cast_('any_', security_groups_ctx)

    for security_id in candidates:
        if security_groups_ctx.has_security_id(security_id):
            return security_id

    return None

# ################################################################################################################################

def is_channel_visible(channel_item:'anydict', security_ids:'intset') -> 'bool':
    """ Whether a channel is visible to a caller whose credentials the given security definitions accept,
    which is the case when the channel itself accepts one of these definitions.
    """
    security_id = get_accepted_security_id(channel_item, security_ids)

    out = security_id is not None
    return out

# ################################################################################################################################

def _service_entries(server:'ParallelServer', channel_item:'anydict', models:'stranydict') -> 'dictlist':
    """ Builds generator service entries for one channel, one entry per HTTP method the channel accepts.
    """
    service_name = channel_item['service_name']
    service_store = server.service_store

    # The channel may point to a service that is not deployed on this server
    if not (impl_name := service_store.name_to_impl_name.get(service_name)):
        return []

    service_info = service_store.services[impl_name]
    class_ = service_info['service_class']

    # Convert the runtime I/O attributes into generator definitions ..
    input_definition = _io_definition(getattr(class_, 'input', None), models)
    output_definition = _io_definition(getattr(class_, 'output', None), models)

    # .. a channel with a method of its own accepts that one method only, a channel accepting any method
    # documents the ones its service has handlers for, and a service with no such handlers is a POST one ..
    if channel_method := channel_item['method']:
        http_methods = [channel_method]
    elif method_handlers := class_.http_method_handlers:
        http_methods = sorted(method_handlers)
    else:
        http_methods = [_default_http_method]

    # .. deprecation attributes are opaque ones, so channels that predate them carry no value ..
    is_deprecated         = channel_item.get('is_deprecated') is True
    deprecation_sunset    = channel_item.get('deprecation_sunset', '')
    deprecation_successor = channel_item.get('deprecation_successor', '')

    # .. the service's own docstring, never an inherited one, describes the operation as a single paragraph ..
    if docstring := class_.__doc__:
        docstring = ' '.join(docstring.split())
    else:
        docstring = ''

    # .. a channel that names an Accept value of its own is reached only by requests that send it,
    # so the document gives that value as the media type of the operation's responses ..
    response_media_type = ''

    if http_accept := channel_item['http_accept']:
        if http_accept != _accept_any:
            response_media_type = http_accept

    # .. and build one entry per method.
    out = []

    for http_method in http_methods:
        entry = {
            'name': service_name,
            'class_name': class_.__name__,
            'docstring': docstring,
            'url_path': channel_item['url_path'],
            'http_method': http_method.lower(),
            'input': input_definition,
            'output': output_definition,
            'is_deprecated': is_deprecated,
            'deprecation_sunset': deprecation_sunset,
            'deprecation_successor': deprecation_successor,
            'response_media_type': response_media_type,
        }
        out.append(entry)

    return out

# ################################################################################################################################

def build_full_spec(server:'ParallelServer') -> 'tuple_[anydict, anydict]':
    """ Builds the complete OpenAPI document out of all the eligible channels, with no per-caller filtering.
    Returns the document and a channel map of path -> HTTP method -> channel ID, which is what
    per-caller filtering later uses to decide which operations a caller can see.
    """
    url_data = server.url_data

    models:'stranydict' = {}
    services = []
    channel_map:'anydict' = {}

    for channel_item in url_data.channel_data:

        # Only the channels that documents describe are part of it ..
        if not is_channel_documented(channel_item):
            continue

        # .. each remaining channel contributes one entry per HTTP method,
        # and the channel map remembers which channel produced which operation.
        entries = _service_entries(server, channel_item, models)

        for entry in entries:
            path_methods = channel_map.setdefault(entry['url_path'], {})
            path_methods[entry['http_method']] = channel_item['id']

        services.extend(entries)

    # Feed the collected metadata into the shared generator ..
    scan_results = {'services': services, 'models': models}
    generator = OpenAPIGenerator(TypeMapper())

    # .. the generator itself is annotated, so its result needs no cast ..
    out = generator.build_spec(scan_results)

    # .. and give the document a title the console shows to users.
    info = cast_('anydict', out['info'])
    info['title'] = _spec_title

    return out, channel_map

# ################################################################################################################################

def get_spec_inputs(server:'ParallelServer') -> 'anylist':
    """ Returns what the complete document is built out of - each channel that it describes, together with
    the class of the service behind that channel - which a document built earlier is current for while it remains the same.
    """
    service_store = server.service_store
    out = []

    for channel_item in server.url_data.channel_data:

        if not is_channel_documented(channel_item):
            continue

        # A channel whose service is not deployed contributes no operations, and a redeployed service has a new class
        if impl_name := service_store.name_to_impl_name.get(channel_item['service_name']):
            service_info = service_store.services[impl_name]
            service_class = service_info['service_class']
        else:
            service_class = None

        out.append((channel_item['id'], service_class))

    return out

# ################################################################################################################################

def _collect_schema_refs(node:'any_', out:'any_') -> 'None':
    """ Walks a document fragment and adds the names of all the referenced component schemas to the output set.
    """
    if isinstance(node, dict):
        for key, value in node.items():
            if key == '$ref':
                schema_name = value.rsplit('/', 1)[1]
                out.add(schema_name)
            else:
                _collect_schema_refs(value, out)

    elif isinstance(node, list):
        for item in node:
            _collect_schema_refs(item, out)

# ################################################################################################################################

def filter_spec(
    server:'ParallelServer',
    spec:'anydict',
    channel_map:'anydict',
    security_ids:'intset',
) -> 'anydict':
    """ Filters the cached full document down to the operations the caller's credentials can invoke.
    Tags and component schemas that no remaining operation uses are dropped too, so the filtered
    document reveals nothing about endpoints the caller cannot see.
    """
    url_data = server.url_data

    # Visibility is checked against live channel data so that security changes take effect immediately
    channel_by_id = {item['id']: item for item in url_data.channel_data}

    paths = {}

    for path, path_item in spec['paths'].items():

        kept_operations = {}

        for http_method, operation in path_item.items():

            channel_id = channel_map[path][http_method]

            # The channel may have just been deleted and the rebuild not have completed yet,
            # in which case the operation is simply not visible.
            channel_item = channel_by_id.get(channel_id)
            if channel_item is None:
                continue

            if not is_channel_visible(channel_item, security_ids):
                continue

            kept_operations[http_method] = operation

        if kept_operations:
            paths[path] = kept_operations

    # Only the schemas the remaining operations reference are kept, including schemas
    # that other kept schemas reference, hence the loop runs until no new names appear.
    schemas = cast_('anydict', spec['components']['schemas'])
    kept_schema_names:'any_' = set()
    _collect_schema_refs(paths, kept_schema_names)

    while True:
        new_names:'any_' = set()
        for schema_name in kept_schema_names:
            if schema_name in schemas:
                _collect_schema_refs(schemas[schema_name], new_names)

        # No schema referenced anything new, so the closure is complete
        if new_names <= kept_schema_names:
            break

        kept_schema_names |= new_names

    kept_schemas = {name: schema for name, schema in schemas.items() if name in kept_schema_names}

    # Only the tags the remaining operations use are kept
    tag_names:'any_' = set()
    for path_item in paths.values():
        for operation in path_item.values():
            tag_names.update(operation['tags'])

    # The filtered document shares the operation and schema objects with the cached one,
    # which is safe because callers only ever serialize the document, never modify it.
    out:'anydict' = {
        'openapi': spec['openapi'],
        'info': spec['info'],
        'paths': paths,
        'components': {'schemas': kept_schemas},
    }

    if tag_names:
        out['tags'] = [{'name': tag_name} for tag_name in sorted(tag_names)]

    return out

# ################################################################################################################################
# ################################################################################################################################
