# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
from logging import getLogger
from base64 import b64encode
from http.client import ACCEPTED
from time import monotonic, sleep

# Zato
from zato.common.typing_ import cast_
from zato.server.connection.cloud.microsoft_fabric.client import MicrosoftFabricClient

# Live Fabric
from live_fabric.common import ModuleCtx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anydictnone, anylist, callable_, strlist

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# The path segment each item type is created under
_item_paths = {
    'Lakehouse':     'lakehouses',
    'Notebook':      'notebooks',
    'DataPipeline':  'dataPipelines',
    'Eventhouse':    'eventhouses',
    'Eventstream':   'eventstreams',
    'SemanticModel': 'semanticModels',
    'Report':        'reports',
}

# The payload type of a definition part
_payload_type = 'InlineBase64'

# ################################################################################################################################
# ################################################################################################################################

def new_client(state:'anydict') -> 'MicrosoftFabricClient':
    """ A client signed in as the app registration.
    """
    config = {
        'name': ModuleCtx.Connection_Name,
        'tenant_id': state['tenant_id'],
        'client_id': state['client_id'],
        'client_secret': state['client_secret'],
    }

    out = MicrosoftFabricClient(config)
    return out

# ################################################################################################################################
# ################################################################################################################################

def definition_part(path:'str', text:'str') -> 'anydict':
    """ One file of an item's definition.
    """
    data = text.encode('utf-8')
    payload = b64encode(data).decode('ascii')

    out = {'path': path, 'payload': payload, 'payloadType': _payload_type}
    return out

# ################################################################################################################################

def json_part(path:'str', data:'anydict') -> 'anydict':
    """ One JSON file of an item's definition.
    """
    text = json.dumps(data, indent=2)

    out = definition_part(path, text)
    return out

# ################################################################################################################################

def new_definition(parts:'anylist', definition_format:'str'='') -> 'anydict':
    """ A definition out of its parts.
    """
    out:'anydict' = {'parts': parts}

    if definition_format:
        out['format'] = definition_format

    return out

# ################################################################################################################################
# ################################################################################################################################

def complete(client:'MicrosoftFabricClient', method:'str', path:'str', data:'anydict') -> 'anydictnone':
    """ Invokes an endpoint that may answer at once or start a long-running operation,
    and returns the result either way.
    """
    response = client.invoke_raw(method, path, data=data)

    # An operation that runs on is followed to its end and its result is read from where it points ..
    if response.status_code == ACCEPTED:
        location = response.headers['Location']
        _ = client.wait_for_operation(location)

        out = client.get(f'{location}/result')
        return out

    # .. one that completed at once carries its result in the body.
    if response.content:
        out = response.json()
        return out

# ################################################################################################################################

def find_item(client:'MicrosoftFabricClient', workspace_id:'str', name:'str', item_type:'str') -> 'anydictnone':
    """ The item of that name and type, if the workspace has one.
    """
    response = client.list_items(workspace_id, item_type)

    for item in response['value']:
        if item['displayName'] == name:
            out = item
            break
    else:
        out = None

    return out

# ################################################################################################################################

def find_or_create_item(
    client:'MicrosoftFabricClient',
    workspace_id:'str',
    name:'str',
    item_type:'str',
    definition:'anydictnone'=None,
    ) -> 'anydict':
    """ The item of that name and type, created from the definition if the workspace has none yet.
    """
    if item := find_item(client, workspace_id, name, item_type):
        logger.info(f'{item_type} {name} exists')
        return item

    logger.info(f'Creating {item_type} {name} ..')

    data:'anydict' = {'displayName': name}
    if definition:
        data['definition'] = definition

    path_segment = _item_paths[item_type]
    path = f'/workspaces/{workspace_id}/{path_segment}'

    out = complete(client, 'POST', path, data)
    out = cast_('anydict', out)

    return out

# ################################################################################################################################

def wait_until(what:'str', check:'callable_') -> 'None':
    """ Polls a check until it passes or the provisioning timeout runs out.
    """
    deadline = monotonic() + ModuleCtx.Provisioning_Timeout

    while True:

        if check():
            return

        now = monotonic()
        if now >= deadline:
            raise Exception(f'{what} was not ready within {ModuleCtx.Provisioning_Timeout}s')

        sleep(ModuleCtx.Provisioning_Poll_Interval)

# ################################################################################################################################
# ################################################################################################################################

def find_workspace(client:'MicrosoftFabricClient', name:'str') -> 'anydictnone':
    """ The workspace of that name, if the principal can see one.
    """
    response = client.list_workspaces()

    for workspace in response['value']:
        if workspace['displayName'] == name:
            out = workspace
            break
    else:
        out = None

    return out

# ################################################################################################################################

def find_capacity_id(client:'MicrosoftFabricClient', name:'str') -> 'str':
    """ The Fabric ID of the capacity of that name.
    """
    response = client.list_capacities()

    for capacity in response['value']:
        if capacity['displayName'] == name:
            out = capacity['id']
            break
    else:
        raise Exception(f'Capacity {name} is not visible to app registration {ModuleCtx.App_Name}')

    return out

# ################################################################################################################################

def role_assignment_exists(client:'MicrosoftFabricClient', workspace_id:'str', principal_id:'str') -> 'bool':
    """ Whether the principal already has a role in the workspace.
    """
    response = client.get(f'/workspaces/{workspace_id}/roleAssignments')
    response = cast_('anydict', response)

    for assignment in response['value']:
        principal = assignment['principal']
        if principal['id'] == principal_id:
            out = True
            break
    else:
        out = False

    return out

# ################################################################################################################################
# ################################################################################################################################

def find_connection(client:'MicrosoftFabricClient', name:'str') -> 'anydictnone':
    """ The Fabric connection of that name, if the principal can see one.
    """
    response = client.get('/connections')
    response = cast_('anydict', response)

    for connection in response['value']:
        if connection['displayName'] == name:
            out = connection
            break
    else:
        out = None

    return out

# ################################################################################################################################

def find_or_create_web_connection(client:'MicrosoftFabricClient', name:'str', url:'str') -> 'str':
    """ The ID of a Web connection to the address, created without credentials if there is none yet.
    """
    if connection := find_connection(client, name):
        logger.info(f'Connection {name} exists')
        out = connection['id']
        return out

    logger.info(f'Creating connection {name} ..')

    data = {
        'connectivityType': 'ShareableCloud',
        'displayName': name,
        'connectionDetails': {
            'type': 'Web',
            'creationMethod': 'Web',
            'parameters': [
                {'dataType': 'Text', 'name': 'url', 'value': url},
            ],
        },
        'privacyLevel': 'Organizational',
        'credentialDetails': {
            'singleSignOnType': 'None',
            'connectionEncryption': 'Any',
            'skipTestConnection': True,
            'credentials': {'credentialType': 'Anonymous'},
        },
    }

    response = client.post('/connections', data=data)
    response = cast_('anydict', response)

    out = response['id']
    return out

# ################################################################################################################################

def delete_connection_if_exists(client:'MicrosoftFabricClient', name:'str') -> 'None':
    """ Deletes the Fabric connection of that name, if there is one.
    """
    if connection := find_connection(client, name):
        logger.info(f'Deleting connection {name} ..')
        connection_id = connection['id']
        _ = client.delete(f'/connections/{connection_id}')

# ################################################################################################################################
# ################################################################################################################################

def table_names(client:'MicrosoftFabricClient', workspace_id:'str', lakehouse_id:'str') -> 'strlist':
    """ The names of the lakehouse's tables.
    """
    out:'strlist' = []

    tables = client.list_tables(workspace_id, lakehouse_id)
    for table in tables:
        out.append(table['name'])

    return out

# ################################################################################################################################
# ################################################################################################################################
