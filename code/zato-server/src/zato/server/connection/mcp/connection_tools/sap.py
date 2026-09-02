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

# How many seconds to wait for a pooled OData client, covering the window
# while the connection queue is still being built.
_block_timeout = 30

# The operations a SAP tool accepts - each one maps onto one ODataClient method
_operations = ['read', 'get', 'create', 'update', 'delete', 'call_function', 'call_action', 'count']

# What every SAP tool advertises as its input
input_schema:'stranydict' = {
    'type': 'object',
    'properties': {
        'operation': {
            'type': 'string',
            'enum': _operations,
            'description': 'The OData operation to run',
        },
        'entity_set': {
            'type': 'string',
            'description': 'The entity set, or the function or action name for call_function and call_action',
        },
        'arguments': {
            'type': 'object',
            'description': 'Arguments of the operation, e.g. key, data, params or query options',
        },
    },
    'required': ['operation', 'entity_set'],
}

# ################################################################################################################################
# ################################################################################################################################

def get_config_dict(config_manager:'ConfigManager') -> 'any_':
    """ SAP connection names resolve in the config manager's SAP dict.
    """

    out = config_manager.outconn_sap
    return out

# ################################################################################################################################

def build_description(connection_name:'str', item:'any_') -> 'str':
    """ Describes a SAP tool through the address the connection points to.
    """

    address = item['address']

    out = f'Invokes the SAP connection `{connection_name}` ({address}) through OData'
    return out

# ################################################################################################################################

def _run_read(client:'any_', entity_set:'str', arguments:'stranydict') -> 'any_':
    out = client.read(entity_set, **arguments)
    return out

def _run_get(client:'any_', entity_set:'str', arguments:'stranydict') -> 'any_':
    key = arguments.pop('key')
    out = client.get(entity_set, key, **arguments)
    return out

def _run_create(client:'any_', entity_set:'str', arguments:'stranydict') -> 'any_':
    data = arguments['data']
    out = client.create(entity_set, data)
    return out

def _run_update(client:'any_', entity_set:'str', arguments:'stranydict') -> 'any_':
    key = arguments.pop('key')
    data = arguments.pop('data')
    out = client.update(entity_set, key, data, **arguments)
    return out

def _run_delete(client:'any_', entity_set:'str', arguments:'stranydict') -> 'any_':
    key = arguments.pop('key')
    out = client.delete(entity_set, key, **arguments)
    return out

def _run_call_function(client:'any_', entity_set:'str', arguments:'stranydict') -> 'any_':
    out = client.call_function(entity_set, params=arguments)
    return out

def _run_call_action(client:'any_', entity_set:'str', arguments:'stranydict') -> 'any_':
    out = client.call_action(entity_set, data=arguments)
    return out

def _run_count(client:'any_', entity_set:'str', arguments:'stranydict') -> 'any_':
    out = client.count(entity_set, **arguments)
    return out

# Which function runs each operation
_operation_runners = {
    'read': _run_read,
    'get': _run_get,
    'create': _run_create,
    'update': _run_update,
    'delete': _run_delete,
    'call_function': _run_call_function,
    'call_action': _run_call_action,
    'count': _run_count,
}

# ################################################################################################################################

def invoke(cid:'str', item:'any_', arguments:'stranydict') -> 'any_':
    """ Borrows a pooled OData client and runs the requested operation on it,
    refusing anything outside the operation table.
    """

    operation = arguments['operation']
    entity_set = arguments['entity_set']

    if (call_arguments := arguments.get('arguments')) is None:
        call_arguments = {}

    # Anything outside the operation table is refused before a client is even borrowed ..
    if runner := _operation_runners.get(operation):

        # .. borrow a pooled client for the duration of the one call.
        wrapper = item.conn

        with wrapper.client(should_block=True, block_timeout=_block_timeout) as client:
            out = runner(client, entity_set, call_arguments)

        return out

    else:
        raise Exception(f'Unknown SAP operation `{operation}`')

# ################################################################################################################################
# ################################################################################################################################

definition = GroupDefinition(
    group = 'sap',
    config_key = 'sap_connections',
    tool_prefix = 'sap',
    get_config_dict = get_config_dict,
    input_schema = input_schema,
    build_description = build_description,
    invoke = invoke,
)

# ################################################################################################################################
# ################################################################################################################################
