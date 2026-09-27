# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import OK
from logging import getLogger

# Zato
from zato.common.typing_ import cast_

# Live Fabric
from live_fabric import base, items
from live_fabric.common import ModuleCtx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anydictnone, anylist, strlist
    from zato.server.connection.cloud.microsoft_fabric.client import MicrosoftFabricClient

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# The app registrations of the REST and eventhouse tokens, with their state key prefixes
_token_apps = (
    (ModuleCtx.Events_REST_App_Name, ModuleCtx.Events_REST_Prefix),
    (ModuleCtx.Eventhouse_App_Name, ModuleCtx.Eventhouse_Prefix),
)

# The workspace role that lets a principal send events and query the eventhouse
_contributor_role = 'Contributor'

# The names of the nodes inside the eventstream
_default_stream = 'occupancy_events_stream'
_derived_stream = 'stock_alerts_stream'
_filter_operator = 'stock_filter'
_eventhouse_destination = 'operations_events'

# The columns of the Events table, in Kusto and in the eventstream's own terms
_event_columns = (
    ('event_type',    'string',   'Nvarchar(max)'),
    ('location',      'string',   'Nvarchar(max)'),
    ('occurred_at',   'datetime', 'DateTime'),
    ('admission_id',  'string',   'Nvarchar(max)'),
    ('item_id',       'string',   'Nvarchar(max)'),
    ('quantity',      'long',     'BigInt'),
    ('reorder_level', 'long',     'BigInt'),
)

# ################################################################################################################################
# ################################################################################################################################

def kusto_command(client:'MicrosoftFabricClient', query_uri:'str', database:'str', command:'str') -> 'None':
    """ Runs one management command against the eventhouse.
    """
    token, _ = client._acquire_token_for_scope(ModuleCtx.Kusto_Scope)

    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }
    data = {'db': database, 'csl': command}
    url = f'{query_uri}/v1/rest/mgmt'

    response = client.session.post(url, json=data, headers=headers)

    if response.status_code != OK:
        raise Exception(f'Kusto command failed: {response.status_code} -> {repr(response.text)}')

# ################################################################################################################################

def create_table_command() -> 'str':
    """ The command that creates the Events table, or leaves it as it is when it exists.
    """
    column_texts:'strlist' = []

    for name, kusto_type, _ in _event_columns:
        column_texts.append(f'{name}:{kusto_type}')

    columns = ', '.join(column_texts)

    out = f'.create-merge table {ModuleCtx.Events_Table} ({columns})'
    return out

# ################################################################################################################################

def ensure_eventhouse(client:'MicrosoftFabricClient', state:'anydict') -> 'None':
    """ The eventhouse, its KQL database and the Events table.
    """
    workspace_id = state['workspace_id']

    eventhouse = items.find_or_create_item(client, workspace_id, ModuleCtx.Eventhouse_Name, 'Eventhouse')
    eventhouse_id = eventhouse['id']
    state['eventhouse_id'] = eventhouse_id

    def is_eventhouse_ready() -> 'bool':
        current = client.get(f'/workspaces/{workspace_id}/eventhouses/{eventhouse_id}')
        current = cast_('anydict', current)
        properties = current['properties']

        if 'queryServiceUri' not in properties:
            return False

        if not properties['databasesItemIds']:
            return False

        state['query_uri'] = properties['queryServiceUri']
        database_ids = properties['databasesItemIds']
        state['kql_database_id'] = database_ids[0]
        return True

    logger.info(f'Waiting for eventhouse {ModuleCtx.Eventhouse_Name} ..')
    items.wait_until(f'Eventhouse {ModuleCtx.Eventhouse_Name}', is_eventhouse_ready)

    kql_database_id = state['kql_database_id']
    database = client.get(f'/workspaces/{workspace_id}/kqlDatabases/{kql_database_id}')
    database = cast_('anydict', database)
    database_name = database['displayName']
    state['kql_database_name'] = database_name

    logger.info(f'Creating table {ModuleCtx.Events_Table} ..')
    command = create_table_command()
    kusto_command(client, state['query_uri'], database_name, command)

# ################################################################################################################################
# ################################################################################################################################

def input_schema(node:'str') -> 'anydict':
    """ The schema the filter reads its input stream through.
    """
    columns:'anylist' = []

    for name, _, stream_type in _event_columns:
        columns.append({'name': name, 'type': stream_type})

    out = {'name': node, 'schema': {'columns': columns}}
    return out

# ################################################################################################################################

def eventstream_definition(state:'anydict') -> 'anydict':
    """ The eventstream definition.
    """
    json_serialization = {'type': 'Json', 'properties': {'encoding': 'UTF8'}}

    topology = {
        'sources': [
            {'name': ModuleCtx.Eventstream_Source, 'type': 'CustomEndpoint', 'properties': {}},
        ],
        'streams': [
            {
                'name': _default_stream,
                'type': 'DefaultStream',
                'properties': {},
                'inputNodes': [{'name': ModuleCtx.Eventstream_Source}],
            },
            {
                'name': _derived_stream,
                'type': 'DerivedStream',
                'properties': {'inputSerialization': json_serialization},
                'inputNodes': [{'name': _filter_operator}],
            },
        ],
        'operators': [
            {
                'name': _filter_operator,
                'type': 'Filter',
                'inputNodes': [{'name': _default_stream}],
                'inputSchemas': [input_schema(_default_stream)],
                'properties': {
                    'conditions': [
                        {
                            'column': {'node': _default_stream, 'columnName': 'event_type', 'columnPathSegments': []},
                            'operatorType': 'Equals',
                            'value': {'dataType': 'Nvarchar(max)', 'value': ModuleCtx.Alert_Event_Type},
                        },
                    ],
                },
            },
        ],
        'destinations': [
            {
                'name': _eventhouse_destination,
                'type': 'Eventhouse',
                'inputNodes': [{'name': _default_stream}],
                'properties': {
                    'dataIngestionMode': 'ProcessedIngestion',
                    'workspaceId': state['workspace_id'],
                    'itemId': state['kql_database_id'],
                    'databaseName': state['kql_database_name'],
                    'tableName': ModuleCtx.Events_Table,
                    'inputSerialization': json_serialization,
                },
            },
            {
                'name': ModuleCtx.Eventstream_Alerts,
                'type': 'CustomEndpoint',
                'inputNodes': [{'name': _derived_stream}],
                'properties': {},
            },
        ],
        'compatibilityLevel': '1.0',
    }

    properties = {'retentionTimeInDays': 1, 'eventThroughputLevel': 'Low'}

    parts = [
        items.json_part('eventstream.json', topology),
        items.json_part('eventstreamProperties.json', properties),
    ]

    out = items.new_definition(parts)
    return out

# ################################################################################################################################

def find_node(nodes:'anylist', name:'str') -> 'anydict':
    """ The node of that name in the eventstream's topology.
    """
    for node in nodes:
        if node['name'] == name:
            out = node
            break
    else:
        raise Exception(f'Eventstream node {name} not found')

    return out

# ################################################################################################################################

def read_connection(client:'MicrosoftFabricClient', path:'str') -> 'anydictnone':
    """ The connection details of a custom endpoint, or nothing while they are still being prepared.
    """
    try:
        connection = client.get(path)
    except Exception as e:
        if 'AuthorizationRuleNotFound' in str(e):
            return None
        raise

    connection = cast_('anydict', connection)

    if 'accessKeys' not in connection:
        return None

    return connection

# ################################################################################################################################

def ensure_eventstream(client:'MicrosoftFabricClient', state:'anydict') -> 'None':
    """ The eventstream and the keys of its custom endpoints.
    """
    workspace_id = state['workspace_id']

    definition = eventstream_definition(state)
    eventstream = items.find_or_create_item(client, workspace_id, ModuleCtx.Eventstream_Name, 'Eventstream', definition)
    eventstream_id = eventstream['id']
    state['eventstream_id'] = eventstream_id

    base_path = f'/workspaces/{workspace_id}/eventstreams/{eventstream_id}'

    topology = client.get(f'{base_path}/topology')
    topology = cast_('anydict', topology)

    source = find_node(topology['sources'], ModuleCtx.Eventstream_Source)
    destination = find_node(topology['destinations'], ModuleCtx.Eventstream_Alerts)
    source_id = source['id']
    destination_id = destination['id']

    source_path = f'{base_path}/sources/{source_id}/connection'
    destination_path = f'{base_path}/destinations/{destination_id}/connection'

    def are_keys_ready() -> 'bool':
        source_connection = read_connection(client, source_path)
        destination_connection = read_connection(client, destination_path)

        if not source_connection:
            return False

        if not destination_connection:
            return False

        source_keys = source_connection['accessKeys']
        destination_keys = destination_connection['accessKeys']

        state['events_namespace'] = source_connection['fullyQualifiedNamespace']
        state['events_topic'] = source_connection['eventHubName']
        state['events_connection_string'] = source_keys['primaryConnectionString']

        state['alerts_namespace'] = destination_connection['fullyQualifiedNamespace']
        state['alerts_topic'] = destination_connection['eventHubName']
        state['alerts_consumer_group'] = destination_connection['consumerGroupName']
        state['alerts_connection_string'] = destination_keys['primaryConnectionString']
        return True

    logger.info(f'Waiting for the keys of eventstream {ModuleCtx.Eventstream_Name} ..')
    items.wait_until(f'Keys of eventstream {ModuleCtx.Eventstream_Name}', are_keys_ready)

# ################################################################################################################################
# ################################################################################################################################

def ensure_token_identities(client:'MicrosoftFabricClient', state:'anydict') -> 'None':
    """ The app registrations behind the REST and eventhouse tokens, each a contributor of the workspace.
    """
    workspace_id = state['workspace_id']

    for name, prefix in _token_apps:
        base.ensure_app(state, name, prefix)
        base.ensure_workspace_role(client, workspace_id, state[f'{prefix}principal_id'], _contributor_role)

# ################################################################################################################################
# ################################################################################################################################

def build(client:'MicrosoftFabricClient', state:'anydict') -> 'None':
    """ The eventhouse, the eventstream and the app registrations of the tokens.
    """
    ensure_eventhouse(client, state)
    ensure_eventstream(client, state)
    ensure_token_identities(client, state)

# ################################################################################################################################
# ################################################################################################################################
