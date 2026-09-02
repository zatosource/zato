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

# What every REST tool advertises as its input
input_schema:'stranydict' = {
    'type': 'object',
    'properties': {
        'method': {
            'type': 'string',
            'enum': ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
            'description': 'HTTP method to invoke the connection with',
        },
        'params': {
            'type': 'object',
            'description': 'Query string and path parameters',
        },
        'data': {
            'type': 'object',
            'description': 'Request body',
        },
    },
    'required': ['method'],
}

# ################################################################################################################################
# ################################################################################################################################

def get_config_dict(config_manager:'ConfigManager') -> 'any_':
    """ REST connection names resolve in the outgoing plain HTTP config dict.
    """

    out = config_manager.config_store.out_plain_http
    return out

# ################################################################################################################################

def build_description(connection_name:'str', item:'any_') -> 'str':
    """ Describes a REST tool through the host and URL path the connection points to.
    """

    config = item['config']
    host = config['host']
    url_path = config['url_path']

    out = f'Invokes the outgoing REST connection `{connection_name}` ({host}{url_path})'
    return out

# ################################################################################################################################

def invoke(cid:'str', item:'any_', arguments:'stranydict') -> 'any_':
    """ Invokes a REST connection with the method, parameters and body from the tool call.
    """

    wrapper = item.conn

    method = arguments['method']
    params = arguments.get('params')

    if (data := arguments.get('data')) is None:
        data = ''

    response = wrapper.http_request(method, cid, data, params)

    out = {
        'status_code': response.status_code,
        'data': response.data,
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

definition = GroupDefinition(
    group = 'rest',
    config_key = 'rest_connections',
    tool_prefix = 'rest',
    get_config_dict = get_config_dict,
    input_schema = input_schema,
    build_description = build_description,
    invoke = invoke,
)

# ################################################################################################################################
# ################################################################################################################################
