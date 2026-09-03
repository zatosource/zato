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
    from zato.common.typing_ import any_, dictlist, stranydict
    from zato.server.base.config_manager import ConfigManager

    ConfigManager = ConfigManager

# ################################################################################################################################
# ################################################################################################################################

# How many items the listing operations return when the caller does not say otherwise
_default_list_limit = 20

# ################################################################################################################################
# ################################################################################################################################

# The operations a Microsoft 365 tool accepts - each one maps onto the client's account surface
_microsoft_365_operations = ['send_mail', 'list_messages', 'list_calendar_events', 'list_users']

# What every Microsoft 365 tool advertises as its input
microsoft_365_input_schema:'stranydict' = {
    'type': 'object',
    'properties': {
        'operation': {
            'type': 'string',
            'enum': _microsoft_365_operations,
            'description': 'The Microsoft 365 operation to run',
        },
        'arguments': {
            'type': 'object',
            'description': 'Arguments of the operation, e.g. user, to, subject, body or limit',
        },
    },
    'required': ['operation'],
}

# ################################################################################################################################

def microsoft_365_get_config_dict(config_manager:'ConfigManager') -> 'any_':
    """ Microsoft 365 connection names resolve in the config manager's Microsoft 365 dict.
    """

    out = config_manager.cloud_microsoft_365
    return out

# ################################################################################################################################

def microsoft_365_build_description(connection_name:'str', item:'any_') -> 'str':
    """ Describes a Microsoft 365 tool by the connection it invokes.
    """

    out = f'Invokes the Microsoft 365 connection `{connection_name}` - mail, calendar and directory operations'
    return out

# ################################################################################################################################

def _run_send_mail(client:'any_', arguments:'stranydict') -> 'any_':

    # A mailbox of a specific user - the client credentials flow always names one.
    user = arguments['user']
    mailbox = client.mailbox(resource=user)

    message = mailbox.new_message()
    message.to.add(arguments['to'])
    message.subject = arguments['subject']
    message.body = arguments['body']

    is_sent = message.send()

    out = {'is_sent': is_sent}
    return out

# ################################################################################################################################

def _run_list_messages(client:'any_', arguments:'stranydict') -> 'any_':

    user = arguments['user']
    mailbox = client.mailbox(resource=user)

    if (limit := arguments.get('limit')) is None:
        limit = _default_list_limit

    out:'dictlist' = []

    for message in mailbox.get_messages(limit=limit):
        out.append({
            'subject': message.subject,
            'sender': message.sender.address,
            'received': message.received.isoformat(),
        })

    return out

# ################################################################################################################################

def _run_list_calendar_events(client:'any_', arguments:'stranydict') -> 'any_':

    user = arguments['user']
    schedule = client.schedule(resource=user)
    calendar = schedule.get_default_calendar()

    if (limit := arguments.get('limit')) is None:
        limit = _default_list_limit

    out:'dictlist' = []

    for event in calendar.get_events(limit=limit):
        out.append({
            'subject': event.subject,
            'start': event.start.isoformat(),
            'end': event.end.isoformat(),
        })

    return out

# ################################################################################################################################

def _run_list_users(client:'any_', arguments:'stranydict') -> 'any_':

    directory = client.directory()

    if (limit := arguments.get('limit')) is None:
        limit = _default_list_limit

    out:'dictlist' = []

    for user in directory.get_users(limit=limit):
        out.append({
            'display_name': user.display_name,
            'mail': user.mail,
        })

    return out

# ################################################################################################################################

# Which function runs each Microsoft 365 operation
_microsoft_365_runners = {
    'send_mail': _run_send_mail,
    'list_messages': _run_list_messages,
    'list_calendar_events': _run_list_calendar_events,
    'list_users': _run_list_users,
}

# ################################################################################################################################

def microsoft_365_invoke(cid:'str', item:'any_', arguments:'stranydict') -> 'any_':
    """ Runs one of the curated Microsoft 365 operations through the wrapper's shared client.
    """

    operation = arguments['operation']

    if (call_arguments := arguments.get('arguments')) is None:
        call_arguments = {}

    # Anything outside the operation table is refused ..
    if runner := _microsoft_365_runners.get(operation):

        # .. all tool calls go through the shared client.
        client = item.conn.shared_client

        out = runner(client, call_arguments)
        return out

    else:
        raise Exception(f'Unknown Microsoft 365 operation `{operation}`')

# ################################################################################################################################
# ################################################################################################################################

# What every Teams tool advertises as its input
teams_input_schema:'stranydict' = {
    'type': 'object',
    'properties': {
        'to': {
            'type': 'string',
            'description': 'Either Team name/Channel name or a chat ID',
        },
        'text': {
            'type': 'string',
            'description': 'The message to send, as HTML',
        },
    },
    'required': ['to', 'text'],
}

# ################################################################################################################################

def teams_get_config_dict(config_manager:'ConfigManager') -> 'any_':
    """ Teams connection names resolve in the config manager's Teams dict.
    """

    out = config_manager.chat_microsoft_teams
    return out

# ################################################################################################################################

def teams_build_description(connection_name:'str', item:'any_') -> 'str':
    """ Describes a Teams tool by the connection it sends through.
    """

    out = f'Sends a message through the Microsoft Teams connection `{connection_name}`'
    return out

# ################################################################################################################################

def teams_invoke(cid:'str', item:'any_', arguments:'stranydict') -> 'any_':
    """ Sends one message through the wrapper's shared client.
    """

    to = arguments['to']
    text = arguments['text']

    client = item.conn.shared_client

    out = client.send(to, text)
    return out

# ################################################################################################################################
# ################################################################################################################################

# The methods a Fabric tool accepts - the client's own explicit surface
_fabric_methods = [
    'list_workspaces', 'get_workspace', 'create_workspace', 'delete_workspace',
    'list_items', 'get_item', 'create_item', 'update_item', 'delete_item',
    'run_job', 'get_job', 'cancel_job',
    'list_shortcuts', 'create_shortcut', 'delete_shortcut',
    'list_capacities',
    'list_tables', 'load_table', 'write_table', 'wait_for_operation',
    'query',
    'onelake_list', 'onelake_read', 'onelake_write', 'onelake_delete',
]

# What every Fabric tool advertises as its input
fabric_input_schema:'stranydict' = {
    'type': 'object',
    'properties': {
        'method': {
            'type': 'string',
            'enum': _fabric_methods,
            'description': 'The Fabric client method to call',
        },
        'arguments': {
            'type': 'object',
            'description': 'Keyword arguments of the method, e.g. workspace_id, item_id or file_path',
        },
    },
    'required': ['method'],
}

# ################################################################################################################################

def fabric_get_config_dict(config_manager:'ConfigManager') -> 'any_':
    """ Fabric connection names resolve in the config manager's Fabric dict.
    """

    out = config_manager.cloud_microsoft_fabric
    return out

# ################################################################################################################################

def fabric_build_description(connection_name:'str', item:'any_') -> 'str':
    """ Describes a Fabric tool by the connection it invokes.
    """

    out = f'Invokes the Microsoft Fabric connection `{connection_name}` - workspaces, items, jobs, lakehouse tables, SQL queries and OneLake'
    return out

# ################################################################################################################################

def fabric_invoke(cid:'str', item:'any_', arguments:'stranydict') -> 'any_':
    """ Calls one of the Fabric client's explicit methods through the wrapper's shared client.
    """

    method = arguments['method']

    if (call_arguments := arguments.get('arguments')) is None:
        call_arguments = {}

    # Anything outside the method table is refused ..
    if method not in _fabric_methods:
        raise Exception(f'Unknown Fabric method `{method}`')

    client = item.conn.shared_client
    func = getattr(client, method)

    out = func(**call_arguments)

    # .. OneLake reads return bytes, which travel back as text.
    if isinstance(out, bytes):
        out = out.decode('utf8')

    return out

# ################################################################################################################################
# ################################################################################################################################

# The methods a Power Automate tool accepts
_power_automate_methods = ['list_flows', 'get_flow', 'enable_flow', 'list_runs', 'resubmit_run', 'trigger']

# What every Power Automate tool advertises as its input
power_automate_input_schema:'stranydict' = {
    'type': 'object',
    'properties': {
        'method': {
            'type': 'string',
            'enum': _power_automate_methods,
            'description': 'The Power Automate client method to call',
        },
        'arguments': {
            'type': 'object',
            'description': 'Keyword arguments of the method, e.g. flow_id, run_id or payload',
        },
    },
    'required': ['method'],
}

# ################################################################################################################################

def power_automate_get_config_dict(config_manager:'ConfigManager') -> 'any_':
    """ Power Automate connection names resolve in the config manager's Power Automate dict.
    """

    out = config_manager.cloud_microsoft_power_automate
    return out

# ################################################################################################################################

def power_automate_build_description(connection_name:'str', item:'any_') -> 'str':
    """ Describes a Power Automate tool by the connection it invokes.
    """

    out = f'Invokes the Microsoft Power Automate connection `{connection_name}` - flows, runs and triggers'
    return out

# ################################################################################################################################

def power_automate_invoke(cid:'str', item:'any_', arguments:'stranydict') -> 'any_':
    """ Calls one of the Power Automate client's methods through the wrapper's shared client.
    """

    method = arguments['method']

    if (call_arguments := arguments.get('arguments')) is None:
        call_arguments = {}

    # Anything outside the method table is refused ..
    if method not in _power_automate_methods:
        raise Exception(f'Unknown Power Automate method `{method}`')

    client = item.conn.shared_client
    func = getattr(client, method)

    out = func(**call_arguments)
    return out

# ################################################################################################################################
# ################################################################################################################################

microsoft_365_spec = GroupDefinition(
    group = 'microsoft_365',
    config_key = 'microsoft_365_connections',
    tool_prefix = 'microsoft365',
    get_config_dict = microsoft_365_get_config_dict,
    input_schema = microsoft_365_input_schema,
    build_description = microsoft_365_build_description,
    invoke = microsoft_365_invoke,
)

teams_spec = GroupDefinition(
    group = 'microsoft_teams',
    config_key = 'microsoft_teams_connections',
    tool_prefix = 'teams',
    get_config_dict = teams_get_config_dict,
    input_schema = teams_input_schema,
    build_description = teams_build_description,
    invoke = teams_invoke,
)

fabric_spec = GroupDefinition(
    group = 'microsoft_fabric',
    config_key = 'microsoft_fabric_connections',
    tool_prefix = 'fabric',
    get_config_dict = fabric_get_config_dict,
    input_schema = fabric_input_schema,
    build_description = fabric_build_description,
    invoke = fabric_invoke,
)

power_automate_spec = GroupDefinition(
    group = 'microsoft_power_automate',
    config_key = 'microsoft_power_automate_connections',
    tool_prefix = 'powerautomate',
    get_config_dict = power_automate_get_config_dict,
    input_schema = power_automate_input_schema,
    build_description = power_automate_build_description,
    invoke = power_automate_invoke,
)

# ################################################################################################################################
# ################################################################################################################################
