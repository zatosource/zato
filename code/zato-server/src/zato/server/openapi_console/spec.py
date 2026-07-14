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
from zato.common.api import URL_TYPE
from zato.common.const import ServiceConst
from zato.common.crypto.api import is_string_equal
from zato.common.util.api import new_cid
from zato.openapi.generator.io_scanner import TypeMapper, extract_model_fields_recursive
from zato.openapi.generator.openapi_ import OpenAPIGenerator

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anydictnone, dictlist, intnone, stranydict
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

# ################################################################################################################################
# ################################################################################################################################

def validate_credentials(server:'ParallelServer', username:'str', password:'str') -> 'intnone':
    """ Checks the username and password against all the active Basic Auth security definitions.
    Returns the matching definition's ID or None if the credentials are not valid.
    """
    url_data = server.config_manager.request_dispatcher.url_data

    # Go through all the definitions and find one whose username and password match ..
    for sec_def in url_data.basic_auth_config.values():
        config = sec_def['config']

        # .. inactive definitions can never match ..
        if not config['is_active']:
            continue

        # .. both the username and the password have to be equal ..
        if config['username'] == username:
            if is_string_equal(password, config['password']):
                return config['id']

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

def _is_channel_visible(channel_item:'anydict', security_id:'int', username:'str', password:'str') -> 'bool':
    """ Decides whether a channel is visible to the caller identified by the given security definition.
    """
    # A channel whose own security definition is the caller's one is always visible ..
    if channel_item.get('security_id') == security_id:
        return True

    # .. otherwise, the caller may be a member of one of the channel's security groups.
    if security_groups_ctx := channel_item.get('security_groups_ctx'):
        cid = new_cid()
        if security_groups_ctx.check_security_basic_auth(cid, channel_item['name'], username, password):
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
        }
        out.append(entry)

    return out

# ################################################################################################################################

def build_spec(server:'ParallelServer', username:'str', password:'str') -> 'anydictnone':
    """ Builds an OpenAPI document filtered down to what the caller's credentials give access to.
    Returns None if the credentials are not valid. Admin credentials see all non-internal channels.
    """
    # Reject the request outright if the credentials do not match any active definition ..
    security_id = validate_credentials(server, username, password)
    if not security_id:
        return None

    # .. the admin account sees every endpoint, other accounts only what they can invoke ..
    is_admin = username == ServiceConst.API_Admin_Invoke_Username

    url_data = server.config_manager.request_dispatcher.url_data

    models:'stranydict' = {}
    services = []

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

        # .. non-admin callers only see channels their credentials can invoke ..
        if not is_admin:
            if not _is_channel_visible(channel_item, security_id, username, password):
                continue

        # .. and each remaining channel contributes one entry per HTTP method.
        entries = _service_entries(server, channel_item, models)
        services.extend(entries)

    # Feed the collected metadata into the shared generator ..
    scan_results = {'services': services, 'models': models}
    generator = OpenAPIGenerator(TypeMapper())
    out = generator.build_spec(scan_results)

    # .. and give the document a title the console shows to users.
    out['info']['title'] = _spec_title

    return out

# ################################################################################################################################
# ################################################################################################################################
