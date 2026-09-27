# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import os
import shutil
from typing import NamedTuple

# Live Fabric
from live_fabric import azure
from live_fabric.common import ModuleCtx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, strlist

# ################################################################################################################################
# ################################################################################################################################

_state_path = os.path.join(ModuleCtx.State_Dir, ModuleCtx.State_File)

# The capacity state the tests need
_state_active = 'Active'

# ################################################################################################################################
# ################################################################################################################################

class FabricEnvironment(NamedTuple):
    """ The environment the setup recorded.
    """
    tenant_id: str
    client_id: str
    client_secret: str
    capacity_id: str
    workspace_id: str
    lakehouse_id: str
    state: 'anydict'

# ################################################################################################################################
# ################################################################################################################################

def exists() -> 'bool':
    """ Whether a setup has run on this machine.
    """
    out = os.path.exists(_state_path)
    return out

# ################################################################################################################################

def load() -> 'anydict':
    """ Everything recorded so far, or nothing if no setup has run yet.
    """
    if not exists():
        return {}

    with open(_state_path) as state_file:
        out = json.load(state_file)

    return out

# ################################################################################################################################

def save(state:'anydict') -> 'None':
    """ Records the state, creating the directory on the first save.
    """
    os.makedirs(ModuleCtx.State_Dir, exist_ok=True)

    text = json.dumps(state, indent=2, sort_keys=True)

    with open(_state_path, 'w') as state_file:
        _ = state_file.write(text)

# ################################################################################################################################

def remove() -> 'None':
    """ Removes the state directory with everything in it.
    """
    shutil.rmtree(ModuleCtx.State_Dir, ignore_errors=True)

# ################################################################################################################################

def path_of(file_name:'str') -> 'str':
    """ Where a file of the state directory is.
    """
    out = os.path.join(ModuleCtx.State_Dir, file_name)
    return out

# ################################################################################################################################
# ################################################################################################################################

def missing_requirements() -> 'strlist':
    """ What this machine lacks for the live tests to run.
    """
    out:'strlist' = []

    if not shutil.which('az'):
        out.append('az is not installed')
        return out

    if not azure.is_logged_in():
        out.append('az is not logged in')
        return out

    if not exists():
        out.append(f'State file {_state_path} is missing')
        return out

    capacity_state = azure.capacity_state()

    if capacity_state != _state_active:
        out.append(f'Capacity {ModuleCtx.Capacity_Name} is {capacity_state}, not {_state_active}')

    return out

# ################################################################################################################################

def describe() -> 'FabricEnvironment':
    """ Reads the environment the setup recorded.
    """
    state = load()

    out = FabricEnvironment(
        tenant_id=state['tenant_id'],
        client_id=state['client_id'],
        client_secret=state['client_secret'],
        capacity_id=state['capacity_id'],
        workspace_id=state['workspace_id'],
        lakehouse_id=state['lakehouse_id'],
        state=state,
    )

    return out

# ################################################################################################################################
# ################################################################################################################################
