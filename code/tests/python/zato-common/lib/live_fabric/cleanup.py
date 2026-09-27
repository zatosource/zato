# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# Live Fabric
from live_fabric import azure, items, state as state_
from live_fabric.common import ModuleCtx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, strlist

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# The capacity state cleanup leaves behind
_state_paused = 'Paused'

# Every app registration the chapters create
_app_names = (ModuleCtx.App_Name, ModuleCtx.Events_REST_App_Name, ModuleCtx.Eventhouse_App_Name)

# ################################################################################################################################
# ################################################################################################################################

def delete_fabric_side(state:'anydict') -> 'None':
    """ Deletes the workspace and the connection the pipelines used.
    """
    if 'client_secret' not in state:
        return

    client = items.new_client(state)

    # Delete the workspace ..
    if workspace := items.find_workspace(client, ModuleCtx.Workspace_Name):
        logger.info(f'Deleting workspace {ModuleCtx.Workspace_Name} ..')
        workspace_id = workspace['id']
        _ = client.delete(f'/workspaces/{workspace_id}')

    # .. the connection the pipelines used ..
    items.delete_connection_if_exists(client, ModuleCtx.Zato_Connection_Name)

    # .. and confirm the workspace is gone.
    if items.find_workspace(client, ModuleCtx.Workspace_Name):
        raise Exception(f'Workspace {ModuleCtx.Workspace_Name} still exists')

# ################################################################################################################################

def delete_identities(state:'anydict') -> 'None':
    """ Deletes the app registrations and their service principals.
    """
    if principal_id := state.get('principal_id'):
        azure.remove_capacity_admin(principal_id)

    for name in _app_names:

        if app := azure.find_app(name):
            azure.delete_app(name, app['appId'])

            if azure.app_exists(app['appId']):
                raise Exception(f'App registration {name} still exists')

# ################################################################################################################################

def run() -> 'strlist':
    """ Removes everything the chapter targets built and pauses the capacity.
    """
    state = state_.load()

    delete_fabric_side(state)
    delete_identities(state)

    logger.info(f'Removing {ModuleCtx.State_Dir} ..')
    state_.remove()

    azure.suspend_capacity()

    capacity_state = azure.capacity_state()
    if capacity_state != _state_paused:
        raise Exception(f'Capacity {ModuleCtx.Capacity_Name} is {capacity_state}, not {_state_paused}')

    out = [f'Workspace {ModuleCtx.Workspace_Name} is gone']

    for name in _app_names:
        out.append(f'App registration {name} is gone')

    out.append(f'{ModuleCtx.State_Dir} is gone')
    out.append(f'Capacity {ModuleCtx.Capacity_Name} is {_state_paused}')

    return out

# ################################################################################################################################
# ################################################################################################################################
