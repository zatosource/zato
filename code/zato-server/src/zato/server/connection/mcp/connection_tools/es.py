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

# The client methods an Elasticsearch tool accepts
_methods = ['search', 'get', 'index', 'delete', 'count', 'exists']

# What every Elasticsearch tool advertises as its input
input_schema:'stranydict' = {
    'type': 'object',
    'properties': {
        'method': {
            'type': 'string',
            'enum': _methods,
            'description': 'The Elasticsearch client method to call',
        },
        'index_name': {
            'type': 'string',
            'description': 'The index to operate on',
        },
        'arguments': {
            'type': 'object',
            'description': 'Keyword arguments of the method, e.g. id, query or document',
        },
    },
    'required': ['method', 'index_name'],
}

# ################################################################################################################################
# ################################################################################################################################

def get_config_dict(config_manager:'ConfigManager') -> 'any_':
    """ Elasticsearch connection names resolve in the config manager's Elasticsearch dict.
    """

    out = config_manager.outconn_es
    return out

# ################################################################################################################################

def build_description(connection_name:'str', item:'any_') -> 'str':
    """ Describes an Elasticsearch tool through the addresses the connection points to.
    """

    address_list = item['address_list']

    out = f'Invokes the Elasticsearch connection `{connection_name}` ({address_list})'
    return out

# ################################################################################################################################

def invoke(cid:'str', item:'any_', arguments:'stranydict') -> 'any_':
    """ Calls the requested method on the connection's Elasticsearch client,
    refusing anything outside the method table.
    """

    method = arguments['method']
    index_name = arguments['index_name']

    if (call_arguments := arguments.get('arguments')) is None:
        call_arguments = {}

    # Anything outside the method table is refused ..
    if method not in _methods:
        raise Exception(f'Unknown Elasticsearch method `{method}`')

    # .. the wrapper holds the underlying client ..
    client = item['conn'].client
    func = getattr(client, method)

    result = func(index=index_name, **call_arguments)

    # .. and the client's response object carries the plain body to return.
    out = result.body
    return out

# ################################################################################################################################
# ################################################################################################################################

definition = GroupDefinition(
    group = 'es',
    config_key = 'es_connections',
    tool_prefix = 'es',
    get_config_dict = get_config_dict,
    input_schema = input_schema,
    build_description = build_description,
    invoke = invoke,
)

# ################################################################################################################################
# ################################################################################################################################
