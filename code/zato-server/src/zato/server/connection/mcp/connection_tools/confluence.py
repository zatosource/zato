# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.server.connection.mcp.connection_tools.common import GroupDefinition

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict
    from zato.server.base.config_manager import ConfigManager

    ConfigManager = ConfigManager

# ################################################################################################################################
# ################################################################################################################################

# The methods a Confluence tool accepts - a curated slice of the client's surface
_methods = ['get_page_by_id', 'get_page_by_title', 'create_page', 'update_page', 'cql', 'get_all_spaces']

# What every Confluence tool advertises as its input
input_schema:'stranydict' = {
    'type': 'object',
    'properties': {
        'method': {
            'type': 'string',
            'enum': _methods,
            'description': 'The Confluence client method to call',
        },
        'arguments': {
            'type': 'object',
            'description': 'Keyword arguments of the method, e.g. page_id, space, title or cql',
        },
    },
    'required': ['method'],
}

# ################################################################################################################################
# ################################################################################################################################

def get_config_dict(config_manager:'ConfigManager') -> 'any_':
    """ Confluence connection names resolve in the config manager's Confluence dict.
    """

    out = config_manager.cloud_confluence
    return out

# ################################################################################################################################

def build_description(connection_name:'str', item:'any_') -> 'str':
    """ Describes a Confluence tool through the address the connection points to.
    """

    address = item['address']

    out = f'Invokes the Confluence connection `{connection_name}` ({address})'
    return out

# ################################################################################################################################

def invoke(cid:'str', item:'any_', arguments:'stranydict') -> 'any_':
    """ Borrows a pooled Confluence client and calls the requested method on it,
    refusing anything outside the method table.
    """

    method = arguments['method']

    if (call_arguments := arguments.get('arguments')) is None:
        call_arguments = {}

    # Anything outside the method table is refused before a client is even borrowed ..
    if method not in _methods:
        raise Exception(f'Unknown Confluence method `{method}`')

    # .. borrow a pooled client for the duration of the one call.
    wrapper = item.conn

    with wrapper.client() as client:
        func = getattr(client, method)
        out = func(**call_arguments)

    return out

# ################################################################################################################################
# ################################################################################################################################

definition = GroupDefinition(
    group = 'confluence',
    config_key = 'confluence_connections',
    tool_prefix = 'confluence',
    get_config_dict = get_config_dict,
    input_schema = input_schema,
    build_description = build_description,
    invoke = invoke,
)

# ################################################################################################################################
# ################################################################################################################################
