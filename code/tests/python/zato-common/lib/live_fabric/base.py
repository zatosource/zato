# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from time import monotonic, sleep

# Zato
from zato.common.typing_ import cast_

# Live Fabric
from live_fabric import azure, items, state as state_
from live_fabric.common import ModuleCtx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict
    from zato.server.connection.cloud.microsoft_fabric.client import MicrosoftFabricClient

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# What the SQL endpoint reports once it can be queried
_sql_endpoint_ready = 'Success'

# The role the signed-in user gets in the workspace
_admin_role = 'Admin'

# ################################################################################################################################
# ################################################################################################################################

_access_message = f'''
Fabric rejected the calls of app registration {ModuleCtx.App_Name}.

In the Fabric admin portal, under Tenant settings -> Developer settings, enable
"Service principals can call Fabric public APIs", then re-run the target.
'''

_workspace_message = f'''
Fabric did not let app registration {ModuleCtx.App_Name} create workspace {ModuleCtx.Workspace_Name}.

In the Fabric admin portal, under Tenant settings -> Developer settings, enable
"Service principals can create workspaces, connections, and deployment pipelines", then re-run the target.
'''

# ################################################################################################################################
# ################################################################################################################################

def ensure_app(state:'anydict', name:'str', prefix:'str') -> 'None':
    """ An app registration, its service principal and its client secret, recorded under the prefix.
    """
    if not (app := azure.find_app(name)):
        app = azure.create_app(name)

    state[f'{prefix}client_id'] = app['appId']
    state[f'{prefix}app_object_id'] = app['id']
    state[f'{prefix}principal_id'] = azure.ensure_service_principal(app['appId'])

    if f'{prefix}client_secret' not in state:
        state[f'{prefix}client_secret'] = azure.reset_credential(app['appId'])

# ################################################################################################################################

def ensure_identity(state:'anydict') -> 'None':
    """ The app registration the Fabric connection signs in as.
    """
    state['tenant_id'] = azure.tenant_id()
    ensure_app(state, ModuleCtx.App_Name, '')

# ################################################################################################################################

def ensure_workspace_role(client:'MicrosoftFabricClient', workspace_id:'str', principal_id:'str', role:'str') -> 'None':
    """ Gives a service principal a role in the workspace.
    """
    if items.role_assignment_exists(client, workspace_id, principal_id):
        return

    logger.info(f'Adding a service principal to the workspace as {role} ..')
    data = {'principal': {'id': principal_id, 'type': 'ServicePrincipal'}, 'role': role}

    def is_assigned() -> 'bool':
        try:
            _ = client.post(f'/workspaces/{workspace_id}/roleAssignments', data=data)
        except Exception:
            return False
        return True

    items.wait_until('Workspace role of the service principal', is_assigned)

# ################################################################################################################################

def verify_access(client:'MicrosoftFabricClient') -> 'None':
    """ Waits until the principal can call the Fabric API.
    """
    deadline = monotonic() + ModuleCtx.Access_Timeout

    while True:

        try:
            _ = client.list_workspaces()
        except Exception as e:
            error = str(e)
        else:
            return

        now = monotonic()
        if now >= deadline:
            logger.warning(_access_message)
            raise Exception(f'App registration {ModuleCtx.App_Name} cannot use the Fabric API: {error}')

        logger.info('Waiting for Fabric to accept the app registration ..')
        sleep(ModuleCtx.Access_Poll_Interval)

# ################################################################################################################################

def ensure_workspace(client:'MicrosoftFabricClient', state:'anydict') -> 'None':
    """ The workspace on the capacity, with the signed-in user as its administrator.
    """
    # The workspace itself ..
    if not (workspace := items.find_workspace(client, ModuleCtx.Workspace_Name)):
        logger.info(f'Creating workspace {ModuleCtx.Workspace_Name} ..')
        data = {'displayName': ModuleCtx.Workspace_Name, 'capacityId': state['capacity_id']}

        try:
            workspace = client.post('/workspaces', data=data)
        except Exception as e:
            logger.warning(_workspace_message)
            raise Exception(f'App registration {ModuleCtx.App_Name} cannot create workspaces: {e}')

        workspace = cast_('anydict', workspace)
    else:
        logger.info(f'Workspace {ModuleCtx.Workspace_Name} exists')

    workspace_id = workspace['id']
    state['workspace_id'] = workspace_id

    # .. and the signed-in user is its administrator.
    user_id = azure.signed_in_user_id()

    if not items.role_assignment_exists(client, workspace_id, user_id):
        logger.info('Adding the signed-in user as a workspace administrator ..')
        data = {'principal': {'id': user_id, 'type': 'User'}, 'role': _admin_role}
        _ = client.post(f'/workspaces/{workspace_id}/roleAssignments', data=data)

# ################################################################################################################################

def ensure_lakehouse(client:'MicrosoftFabricClient', state:'anydict') -> 'None':
    """ The lakehouse, with its SQL endpoint ready for queries.
    """
    workspace_id = state['workspace_id']

    lakehouse = items.find_or_create_item(client, workspace_id, ModuleCtx.Lakehouse_Name, 'Lakehouse')
    lakehouse_id = lakehouse['id']
    state['lakehouse_id'] = lakehouse_id

    def is_sql_endpoint_ready() -> 'bool':
        current = client.get(f'/workspaces/{workspace_id}/lakehouses/{lakehouse_id}')
        current = cast_('anydict', current)
        properties = current['properties']

        # The key is present but empty until provisioning starts.
        endpoint = properties['sqlEndpointProperties']
        if not endpoint:
            return False

        if endpoint['provisioningStatus'] != _sql_endpoint_ready:
            return False

        state['sql_endpoint_id'] = endpoint['id']
        state['sql_endpoint_connection_string'] = endpoint['connectionString']
        return True

    logger.info(f'Waiting for the SQL endpoint of lakehouse {ModuleCtx.Lakehouse_Name} ..')
    items.wait_until(f'SQL endpoint of lakehouse {ModuleCtx.Lakehouse_Name}', is_sql_endpoint_ready)

# ################################################################################################################################
# ################################################################################################################################

def setup(state:'anydict') -> 'MicrosoftFabricClient':
    """ The capacity, the app registration, the workspace and the lakehouse. Returns the client.
    """
    # The capacity and the identity ..
    azure.resume_capacity()
    ensure_identity(state)

    # .. saved before anything else runs ..
    state_.save(state)

    # .. the identity as a capacity administrator ..
    azure.ensure_capacity_admin(state['principal_id'])

    # .. a client that can use the API ..
    client = items.new_client(state)
    verify_access(client)

    state['capacity_id'] = items.find_capacity_id(client, ModuleCtx.Capacity_Name)

    # .. and the workspace with its lakehouse.
    ensure_workspace(client, state)
    ensure_lakehouse(client, state)

    return client

# ################################################################################################################################
# ################################################################################################################################
