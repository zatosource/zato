# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.soap.message import XMLMessage
from zato.server.connection.http_soap.invocation import soap_message_to_dict
from zato.server.connection.mcp.connection_tools.common import GroupDefinition

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict
    from zato.server.base.config_manager import ConfigManager

    ConfigManager = ConfigManager

# ################################################################################################################################
# ################################################################################################################################

# What every SOAP tool advertises as its input
input_schema:'stranydict' = {
    'type': 'object',
    'properties': {
        'operation': {
            'type': 'string',
            'description': 'SOAP operation to invoke',
        },
        'message': {
            'type': 'object',
            'description': 'The message that becomes the operation element in the SOAP body',
        },
    },
}

# ################################################################################################################################
# ################################################################################################################################

def get_config_dict(config_manager:'ConfigManager') -> 'any_':
    """ SOAP connection names resolve in the outgoing SOAP config dict.
    """

    out = config_manager.config_store.out_soap
    return out

# ################################################################################################################################

def build_description(connection_name:'str', item:'any_') -> 'str':
    """ Describes a SOAP tool through the host, URL path and SOAP action the connection points to.
    """

    config = item['config']
    host = config['host']
    url_path = config['url_path']
    soap_action = config['soap_action']

    out = f'Invokes the outgoing SOAP connection `{connection_name}` ({host}{url_path}, action: {soap_action})'
    return out

# ################################################################################################################################

def invoke(cid:'str', item:'any_', arguments:'stranydict') -> 'any_':
    """ Invokes a SOAP connection - the wrapper's own declarative profile merging
    and SOAP header evaluation run unchanged underneath.
    """

    wrapper = item.conn

    message = arguments.get('message')

    if (operation := arguments.get('operation')) is None:
        operation = ''

    response = wrapper.invoke(cid, operation, message)

    # The parsed response body is a dot-accessed message - it travels back as a plain dict.
    if isinstance(response, XMLMessage):
        response = soap_message_to_dict(response)

    out = response
    return out

# ################################################################################################################################
# ################################################################################################################################

definition = GroupDefinition(
    group = 'soap',
    config_key = 'soap_connections',
    tool_prefix = 'soap',
    get_config_dict = get_config_dict,
    input_schema = input_schema,
    build_description = build_description,
    invoke = invoke,
)

# ################################################################################################################################
# ################################################################################################################################
