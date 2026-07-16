# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import typing
from base64 import b64decode
from contextlib import closing
from hashlib import pbkdf2_hmac
from hmac import compare_digest
from inspect import isclass

# SQLAlchemy
from sqlalchemy import text

# Zato
from zato.common.api import OpenAPI_Console_Auth, URL_TYPE
from zato.common.crypto.api import is_string_equal
from zato.common.typing_ import cast_
from zato.openapi.generator.io_scanner import TypeMapper, extract_model_fields_recursive
from zato.openapi.generator.openapi_ import OpenAPIGenerator

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, dictlist, intnone, stranydict, tuple_
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

# The only password hash algorithm the Dashboard's Django users are stored with
_django_hash_algorithm = 'pbkdf2_sha256'

# The Dashboard keeps its users in the same database the server uses, in Django's own table
_dashboard_user_query = 'select password from auth_user where username = :username and is_active = :is_active'

# ################################################################################################################################
# ################################################################################################################################

def _verify_django_password(password:'str', encoded:'str') -> 'bool':
    """ Checks a password against a hash in Django's storage format - algorithm$iterations$salt$hash.
    """
    algorithm, iterations, salt, stored_hash = encoded.split('$', 3)

    # Only the one algorithm the Dashboard uses is supported
    if algorithm != _django_hash_algorithm:
        return False

    # Derive the hash from the incoming password the same way Django does ..
    derived = pbkdf2_hmac('sha256', password.encode('utf8'), salt.encode('utf8'), int(iterations))

    # .. and compare in constant time.
    out = compare_digest(derived, b64decode(stored_hash))

    return out

# ################################################################################################################################

def is_dashboard_admin(server:'ParallelServer', username:'str', password:'str') -> 'bool':
    """ Checks the credentials against the Dashboard's own users - anyone who can sign in
    to the Dashboard is the console's admin, with the same username and password.
    """
    with closing(server.odb.session()) as session:
        row = session.execute(text(_dashboard_user_query), {'username':username, 'is_active':True}).fetchone()

    # No such Dashboard user
    if row is None:
        return False

    out = _verify_django_password(password, row[0])

    return out

# ################################################################################################################################

def validate_credentials(server:'ParallelServer', username:'str', password:'str') -> 'intnone':
    """ Checks the username and password against all the active security definitions of the types
    REST channels support - Basic Auth, API keys and Bearer tokens. API key callers sign in with
    the definition's name as the username and the key itself as the password, Bearer token callers
    with the definition's username and its secret.
    Returns the matching definition's ID or None if the credentials are not valid.
    """
    url_data = server.config_manager.request_dispatcher.url_data

    # Go through all the Basic Auth definitions and find one whose username and password match ..
    for sec_def in url_data.basic_auth_config.values():
        config = sec_def['config']

        # .. inactive definitions can never match ..
        if not config['is_active']:
            continue

        # .. both the username and the password have to be equal ..
        if config['username'] == username:
            if is_string_equal(password, config['password']):
                return config['id']

    # .. then through the API key definitions, whose generated usernames mean nothing to callers,
    # so it is the definition's name that identifies it on the sign-in form ..
    for name, sec_def in url_data.apikey_config.items():
        config = sec_def['config']

        # .. inactive definitions can never match ..
        if not config['is_active']:
            continue

        # .. the name has to match and the password field has to carry the key.
        if name == username:
            if is_string_equal(password, config['password']):
                return config['id']

    # .. and finally through the Bearer token definitions, whose secrets are stored
    # in the password field, so they are checked the same way Basic Auth ones are.
    for sec_def in url_data.oauth_config.values():
        config = sec_def['config']

        # .. inactive definitions can never match ..
        if not config['is_active']:
            continue

        # .. both the username and the secret have to be equal.
        if config['username'] == username:
            if is_string_equal(password, config['password']):
                return config['id']

# ################################################################################################################################

def resolve_caller(server:'ParallelServer', fields:'anydict') -> 'tuple_[intnone, bool]':
    """ Resolves a console command's auth fields into the caller's security definition ID and admin flag.
    A caller with no ID and no admin flag could not be identified and gets nothing.
    """
    username = fields['username']

    # Entra ID has already authenticated this caller
    if fields['auth_type'] == OpenAPI_Console_Auth.Type_Entra:
        return None, True

    # Dashboard users are the console's admins, so their credentials are checked first ..
    if is_dashboard_admin(server, username, fields['password']):
        return None, True

    # .. and every other caller is checked against the security definitions.
    security_id = validate_credentials(server, username, fields['password'])

    return security_id, False

# ################################################################################################################################

def _io_from_string(value:'str') -> 'anydict':
    """ Turns a single string input or output declaration into a generator definition.
    """
    is_required = not value.startswith('-')

    out = {
        'type': 'string',
        'name': value.lstrip('-'),
        'required': is_required,
    }

    return out

# ################################################################################################################################

def _io_from_sequence(value:'any_') -> 'anydict':
    """ Turns a tuple or list of input or output elements into a generator definition.
    Elements are either plain strings or typed elements that carry .name and .is_required.
    """
    elements = []

    for item in value:
        if isinstance(item, str):
            element = {
                'name': item.lstrip('-'),
                'required': not item.startswith('-'),
            }
        else:
            element = {
                'name': item.name,
                'required': item.is_required,
            }
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

def is_channel_visible(channel_item:'anydict', security_id:'int') -> 'bool':
    """ Decides whether a channel is visible to the caller identified by the given security definition.
    The caller's credentials were already verified at sign-in, so visibility is pure membership.
    """
    # A channel whose own security definition is the caller's one is always visible ..
    if channel_item.get('security_id') == security_id:
        return True

    # .. otherwise, the caller's definition may belong to one of the channel's security groups,
    # which covers Basic Auth, API key and Bearer token members alike.
    if security_groups_ctx := channel_item.get('security_groups_ctx'):
        if security_groups_ctx.has_security_id(security_id):
            return True

    return False

# ################################################################################################################################

def _service_entries(server:'ParallelServer', channel_item:'anydict', models:'stranydict') -> 'dictlist':
    """ Builds generator service entries for one channel, one entry per HTTP method the service handles.
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

    # .. find out which HTTP methods the service responds to ..
    if method_handlers := class_.http_method_handlers:
        http_methods = sorted(method_handlers)
    else:
        http_methods = [_default_http_method]

    # .. deprecation attributes are opaque ones, so channels that predate them carry no value ..
    is_deprecated = channel_item.get('is_deprecated') is True
    deprecation_sunset = channel_item.get('deprecation_sunset') or ''
    deprecation_successor = channel_item.get('deprecation_successor') or ''

    # .. and build one entry per method.
    out = []

    for http_method in http_methods:
        entry = {
            'name': service_name,
            'class_name': class_.__name__,
            'url_path': channel_item['url_path'],
            'http_method': http_method.lower(),
            'input': input_definition,
            'output': output_definition,
            'is_deprecated': is_deprecated,
            'deprecation_sunset': deprecation_sunset,
            'deprecation_successor': deprecation_successor,
        }
        out.append(entry)

    return out

# ################################################################################################################################

def build_full_spec(server:'ParallelServer') -> 'tuple_[anydict, anydict]':
    """ Builds the complete OpenAPI document out of all the eligible channels, with no per-caller filtering.
    Returns the document and a channel map of path -> HTTP method -> channel ID, which is what
    per-caller filtering later uses to decide which operations a caller can see.
    """
    url_data = server.config_manager.request_dispatcher.url_data

    models:'stranydict' = {}
    services = []
    channel_map:'anydict' = {}

    for channel_item in url_data.channel_data:

        # Only active, non-internal REST channels are documented ..
        if channel_item['connection'] != 'channel':
            continue
        if channel_item['transport'] != URL_TYPE.PLAIN_HTTP:
            continue
        if not channel_item['is_active']:
            continue
        if channel_item['is_internal']:
            continue

        # .. channels without a service of their own, e.g. dispatcher-handled ones, are skipped ..
        if not channel_item['service_name']:
            continue

        # .. channels can opt out of OpenAPI documents - only an explicit off flag excludes them,
        # channels that predate the flag carry no value and are included ..
        if channel_item.get('should_include_in_openapi') is False:
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
    security_id:'int',
) -> 'anydict':
    """ Filters the cached full document down to the operations the caller's credentials can invoke.
    Tags and component schemas that no remaining operation uses are dropped too, so the filtered
    document reveals nothing about endpoints the caller cannot see.
    """
    url_data = server.config_manager.request_dispatcher.url_data

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

            if not is_channel_visible(channel_item, security_id):
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
