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

# The model methods an Odoo tool accepts
_methods = ['search', 'read', 'search_read', 'create', 'write']

# What every Odoo tool advertises as its input
input_schema:'stranydict' = {
    'type': 'object',
    'properties': {
        'model': {
            'type': 'string',
            'description': 'The Odoo model to operate on, e.g. res.partner',
        },
        'method': {
            'type': 'string',
            'enum': _methods,
            'description': 'The model method to call',
        },
        'arguments': {
            'type': 'object',
            'description': 'Keyword arguments of the method, e.g. domain, fields, ids or values',
        },
    },
    'required': ['model', 'method'],
}

# ################################################################################################################################
# ################################################################################################################################

def get_config_dict(config_manager:'ConfigManager') -> 'any_':
    """ Odoo connection names resolve in the outgoing Odoo config dict.
    """

    out = config_manager.config_store.out_odoo
    return out

# ################################################################################################################################

def build_description(connection_name:'str', item:'any_') -> 'str':
    """ Describes an Odoo tool through the host, database and protocol the connection uses.
    """

    config = item['config']
    host = config['host']
    database = config['database']
    protocol = config['protocol']

    out = f'Invokes the Odoo connection `{connection_name}` ({protocol} at {host}, database {database})'
    return out

# ################################################################################################################################

def invoke(cid:'str', item:'any_', arguments:'stranydict') -> 'any_':
    """ Borrows a pooled Odoo client, takes the requested model and calls the method on it -
    the audited model wrapper underneath records every call.
    """

    model_name = arguments['model']
    method = arguments['method']

    if (call_arguments := arguments.get('arguments')) is None:
        call_arguments = {}

    # Anything outside the method table is refused before a client is even borrowed ..
    if method not in _methods:
        raise Exception(f'Unknown Odoo method `{method}`')

    # .. borrow a pooled client for the duration of the one call.
    wrapper = item.conn

    with wrapper.client() as client:
        model = client.get_model(model_name)
        func = getattr(model, method)
        out = func(**call_arguments)

    return out

# ################################################################################################################################
# ################################################################################################################################

definition = GroupDefinition(
    group = 'odoo',
    config_key = 'odoo_connections',
    tool_prefix = 'odoo',
    get_config_dict = get_config_dict,
    input_schema = input_schema,
    build_description = build_description,
    invoke = invoke,
)

# ################################################################################################################################
# ################################################################################################################################
