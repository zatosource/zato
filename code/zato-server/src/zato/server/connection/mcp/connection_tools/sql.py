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

# What every SQL tool advertises as its input
input_schema:'stranydict' = {
    'type': 'object',
    'properties': {
        'query': {
            'type': 'string',
            'description': 'The SQL statement to run',
        },
        'params': {
            'type': 'object',
            'description': 'Named parameters the statement refers to',
        },
    },
    'required': ['query'],
}

# ################################################################################################################################
# ################################################################################################################################

def get_config_dict(config_manager:'ConfigManager') -> 'any_':
    """ SQL connection names resolve in the server's SQL connection pool store.
    """

    out = config_manager.sql_pool_store.wrappers
    return out

# ################################################################################################################################

def build_description(connection_name:'str', item:'any_') -> 'str':
    """ Describes an SQL tool through the engine, host and database the pool connects to.
    """

    config = item.config
    engine = config['engine']
    host = config['host']
    db_name = config['db_name']

    out = f'Runs SQL through the outgoing connection `{connection_name}` ({engine} at {host}, database {db_name})'
    return out

# ################################################################################################################################

def invoke(cid:'str', item:'any_', arguments:'stranydict') -> 'any_':
    """ Runs the statement from the tool call through the pool's session wrapper,
    which is what also puts the call on the audit record for outgoing pools.
    """

    query = arguments['query']
    params = arguments.get('params')

    out = item.execute(query, params)
    return out

# ################################################################################################################################
# ################################################################################################################################

definition = GroupDefinition(
    group = 'sql',
    config_key = 'sql_connections',
    tool_prefix = 'sql',
    get_config_dict = get_config_dict,
    input_schema = input_schema,
    build_description = build_description,
    invoke = invoke,
)

# ################################################################################################################################
# ################################################################################################################################
