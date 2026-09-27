# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
from logging import getLogger

# Live Fabric
from live_fabric import state as state_
from live_fabric.common import ModuleCtx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, strlist

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# The state keys written to fabric.ini
_ini_keys = ('workspace_id', 'lakehouse_id', 'reminder_notebook_id', 'nightly_pipeline_id', 'occupancy_dataset_id')

# ################################################################################################################################
# ################################################################################################################################

def quoted(value:'str') -> 'str':
    """ A string as a quoted YAML scalar.
    """
    out = json.dumps(value)
    return out

# ################################################################################################################################

def fabric_connection(state:'anydict') -> 'strlist':
    """ The Fabric connection.
    """
    tenant_id = state['tenant_id']
    client_id = state['client_id']
    client_secret = state['client_secret']

    out = [
        'microsoft_fabric:',
        f'  - name: {quoted(ModuleCtx.Connection_Name)}',
        f'    tenant_id: {quoted(tenant_id)}',
        f'    client_id: {quoted(client_id)}',
        f'    client_secret: {quoted(client_secret)}',
        '',
    ]
    return out

# ################################################################################################################################

def bearer_token(name:'str', state:'anydict', scope:'str', prefix:'str'='') -> 'strlist':
    """ One Bearer token definition signing in as the app registration recorded under the prefix.
    """
    token_url = ModuleCtx.Token_URL_Template.format(tenant_id=state['tenant_id'])
    client_id = state[f'{prefix}client_id']
    client_secret = state[f'{prefix}client_secret']

    out = [
        f'  - name: {quoted(name)}',
        '    type: bearer_token',
        f'    username: {quoted(client_id)}',
        f'    password: {quoted(client_secret)}',
        f'    auth_endpoint: {quoted(token_url)}',
        f'    scopes: {quoted(scope)}',
        '',
    ]
    return out

# ################################################################################################################################

def events_objects(state:'anydict', alerts_service:'str'=ModuleCtx.Alerts_Service_Name) -> 'strlist':
    """ The Zato objects of the events pages.
    """
    namespace = state['events_namespace']
    alerts_namespace = state['alerts_namespace']
    address = f'{namespace}:{ModuleCtx.Kafka_Port}'
    alerts_address = f'{alerts_namespace}:{ModuleCtx.Kafka_Port}'
    events_scope = ModuleCtx.Events_Scope_Template.format(namespace=namespace)
    events_topic = state['events_topic']
    rest_host = f'https://{namespace}'
    rest_path = f'/{events_topic}/messages'
    connection_string = state['events_connection_string']
    alerts_topic = state['alerts_topic']
    query_uri = state['query_uri']

    # A leading $ names an environment variable in enmasse and is written as $$.
    consumer_group = state['alerts_consumer_group']
    if consumer_group.startswith('$'):
        consumer_group = f'${consumer_group}'

    out = ['security:']
    out.extend(bearer_token(ModuleCtx.Events_Token_Name, state, events_scope))
    out.extend(bearer_token(ModuleCtx.Events_REST_Token_Name, state, ModuleCtx.Events_REST_Scope, ModuleCtx.Events_REST_Prefix))
    out.extend(bearer_token(ModuleCtx.Eventhouse_Token_Name, state, ModuleCtx.Kusto_Scope, ModuleCtx.Eventhouse_Prefix))
    out.extend([
        f'  - name: {quoted(ModuleCtx.Events_Key_Name)}',
        '    type: basic_auth',
        f'    username: {quoted(ModuleCtx.Plain_Username)}',
        f'    password: {quoted(connection_string)}',
        '    realm: zato',
        '',
        'outgoing_kafka:',
        f'  - name: {quoted(ModuleCtx.Events_Outgoing_Name)}',
        f'    address: {quoted(address)}',
        f'    topic: {quoted(events_topic)}',
        f'    security: {quoted(ModuleCtx.Events_Token_Name)}',
        '    sasl_mechanism: OAUTHBEARER',
        '    ssl: true',
        '',
        'channel_kafka:',
        f'  - name: {quoted(ModuleCtx.Alerts_Channel_Name)}',
        f'    address: {quoted(alerts_address)}',
        f'    topic: {quoted(alerts_topic)}',
        f'    group_id: {quoted(consumer_group)}',
        f'    service: {alerts_service}',
        f'    security: {quoted(ModuleCtx.Events_Token_Name)}',
        '    sasl_mechanism: OAUTHBEARER',
        '    ssl: true',
        '',
        'outgoing_rest:',
        f'  - name: {quoted(ModuleCtx.Events_REST_Name)}',
        f'    host: {quoted(rest_host)}',
        f'    url_path: {quoted(rest_path)}',
        '    data_format: json',
        f'    security: {quoted(ModuleCtx.Events_REST_Token_Name)}',
        f'  - name: {quoted(ModuleCtx.Eventhouse_REST_Name)}',
        f'    host: {quoted(query_uri)}',
        '    url_path: /v1/rest/query',
        '    data_format: json',
        f'    security: {quoted(ModuleCtx.Eventhouse_Token_Name)}',
        '',
    ])

    return out

# ################################################################################################################################

def enmasse_yaml(state:'anydict') -> 'str':
    """ The enmasse file for what exists so far.
    """
    lines = fabric_connection(state)

    if 'eventstream_id' in state:
        lines.extend(events_objects(state))

    out = '\n'.join(lines)
    return out

# ################################################################################################################################

def fabric_ini(state:'anydict') -> 'str':
    """ The fabric.ini file.
    """
    lines = [
        '[connection]',
        f'name={ModuleCtx.Connection_Name}',
        '',
        '[operations]',
    ]

    for key in _ini_keys:
        if key in state:
            value = state[key]
            lines.append(f'{key}={value}')

    lines.append('')

    out = '\n'.join(lines)
    return out

# ################################################################################################################################
# ################################################################################################################################

def write_all(state:'anydict') -> 'None':
    """ Saves the state and renders the files the user imports and copies.
    """
    state_.save(state)

    enmasse_path = state_.path_of(ModuleCtx.Enmasse_File)
    ini_path = state_.path_of(ModuleCtx.INI_File)

    with open(enmasse_path, 'w') as enmasse_file:
        _ = enmasse_file.write(enmasse_yaml(state))

    with open(ini_path, 'w') as ini_file:
        _ = ini_file.write(fabric_ini(state))

# ################################################################################################################################
# ################################################################################################################################
