# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import subprocess
from logging import getLogger
from time import monotonic, sleep

# Live Fabric
from live_fabric.common import ModuleCtx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydictnone, strlist

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# The capacity states az reports
_state_active = 'Active'
_state_paused = 'Paused'

# What az says when the capacity was deleted outside the builder
_not_found = 'ResourceNotFound'

# ################################################################################################################################
# ################################################################################################################################

def _run(*command_parts:'str', timeout:'int'=ModuleCtx.Az_Timeout) -> 'subprocess.CompletedProcess[str]':
    """ Runs one az command and returns the completed process, whatever its exit code.
    """
    command = ['az', *command_parts, '--output', 'json']
    out = subprocess.run(command, capture_output=True, text=True, timeout=timeout)

    return out

# ################################################################################################################################

def _run_az(*command_parts:'str', timeout:'int'=ModuleCtx.Az_Timeout) -> 'any_':
    """ Runs one az command and returns what it printed, parsed from JSON.
    """
    # Run the command ..
    result = _run(*command_parts, timeout=timeout)

    # .. a non-zero exit code is an error ..
    if result.returncode != 0:
        group = command_parts[0]
        command_name = command_parts[1]
        error = result.stderr.strip()
        raise Exception(f'az {group} {command_name} failed: {error}')

    # .. empty output has no JSON in it ..
    if not result.stdout.strip():
        return None

    # .. and anything else is parsed.
    out = json.loads(result.stdout)
    return out

# ################################################################################################################################

def is_logged_in() -> 'bool':
    """ Whether az has an account to work with.
    """
    result = _run('account', 'show')

    out = result.returncode == 0
    return out

# ################################################################################################################################

def tenant_id() -> 'str':
    """ The tenant of the signed-in account.
    """
    account = _run_az('account', 'show')

    out = account['tenantId']
    return out

# ################################################################################################################################

def signed_in_user_id() -> 'str':
    """ The object ID of the signed-in user.
    """
    user = _run_az('ad', 'signed-in-user', 'show')

    out = user['id']
    return out

# ################################################################################################################################
# ################################################################################################################################

def capacity_show() -> 'any_':
    """ The capacity as az sees it, or None if it does not exist.
    """
    try:
        out = _run_az(
            'fabric', 'capacity', 'show',
            '--resource-group', ModuleCtx.Resource_Group,
            '--capacity-name', ModuleCtx.Capacity_Name,
        )
    except Exception as e:
        if _not_found in str(e):
            logger.info(f'Capacity {ModuleCtx.Capacity_Name} does not exist')
            return None
        raise

    return out

# ################################################################################################################################

def capacity_state() -> 'str':
    """ Active, Paused, one of the states in between, or an empty string if the capacity does not exist.
    """
    capacity = capacity_show()

    if not capacity:
        return ''

    out = capacity['state']
    return out

# ################################################################################################################################

def resume_capacity() -> 'None':
    """ Makes sure the capacity is running - the call returns once it is.
    """
    state = capacity_state()

    if not state:
        raise Exception(f'Capacity {ModuleCtx.Capacity_Name} does not exist in resource group {ModuleCtx.Resource_Group}')

    if state == _state_active:
        logger.info(f'Capacity {ModuleCtx.Capacity_Name} is active')
        return

    logger.info(f'Resuming capacity {ModuleCtx.Capacity_Name} ..')

    _ = _run_az(
        'fabric', 'capacity', 'resume',
        '--resource-group', ModuleCtx.Resource_Group,
        '--capacity-name', ModuleCtx.Capacity_Name,
        timeout=ModuleCtx.Az_Long_Timeout,
    )

    logger.info(f'Capacity {ModuleCtx.Capacity_Name} is active')

# ################################################################################################################################

def suspend_capacity() -> 'None':
    """ Makes sure the capacity is paused - the call returns once it is.
    """
    state = capacity_state()

    if not state:
        return

    if state == _state_paused:
        logger.info(f'Capacity {ModuleCtx.Capacity_Name} is paused')
        return

    logger.info(f'Suspending capacity {ModuleCtx.Capacity_Name} ..')

    _ = _run_az(
        'fabric', 'capacity', 'suspend',
        '--resource-group', ModuleCtx.Resource_Group,
        '--capacity-name', ModuleCtx.Capacity_Name,
        timeout=ModuleCtx.Az_Long_Timeout,
    )

    logger.info(f'Capacity {ModuleCtx.Capacity_Name} is paused')

# ################################################################################################################################

def principal_exists(object_id:'str') -> 'bool':
    """ Whether the object ID is a service principal or a user that still exists.
    """
    for group in ('sp', 'user'):
        result = _run('ad', group, 'show', '--id', object_id)
        if result.returncode == 0:
            out = True
            break
    else:
        out = False

    return out

# ################################################################################################################################

def existing_capacity_admins() -> 'strlist':
    """ The capacity's administrators, without the ones that were deleted since they were added.
    """
    capacity = capacity_show()

    if not capacity:
        return []

    administration = capacity['administration']
    members:'strlist' = administration['members']

    out:'strlist' = []
    for member in members:
        if principal_exists(member):
            out.append(member)
        else:
            logger.info(f'Dropping deleted principal {member} from the administrators of capacity {ModuleCtx.Capacity_Name}')

    return out

# ################################################################################################################################

def update_capacity_admins(members:'strlist') -> 'None':
    """ Replaces the capacity's administrators.
    """
    administration_text = json.dumps({'members': members})
    deadline = monotonic() + ModuleCtx.Access_Timeout

    while True:

        # Try to replace the list ..
        result = _run(
            'fabric', 'capacity', 'update',
            '--resource-group', ModuleCtx.Resource_Group,
            '--capacity-name', ModuleCtx.Capacity_Name,
            '--administration', administration_text,
            timeout=ModuleCtx.Az_Long_Timeout,
        )

        # .. stop once az accepts it ..
        if result.returncode == 0:
            return

        error = result.stderr.strip()

        # .. give up after the timeout ..
        now = monotonic()
        if now >= deadline:
            raise Exception(f'az fabric capacity update failed: {error}')

        # .. and wait before the next attempt.
        logger.info('Waiting for the service principal to become visible ..')
        sleep(ModuleCtx.Access_Poll_Interval)

# ################################################################################################################################

def ensure_capacity_admin(object_id:'str') -> 'None':
    """ Adds a principal to the capacity's administrators.
    """
    members = existing_capacity_admins()

    if object_id in members:
        return

    logger.info(f'Adding the app registration to the administrators of capacity {ModuleCtx.Capacity_Name} ..')

    members.append(object_id)
    update_capacity_admins(members)

# ################################################################################################################################

def remove_capacity_admin(object_id:'str') -> 'None':
    """ Removes a principal from the capacity's administrators.
    """
    members = existing_capacity_admins()

    if object_id not in members:
        return

    logger.info(f'Removing the app registration from the administrators of capacity {ModuleCtx.Capacity_Name} ..')

    members.remove(object_id)
    update_capacity_admins(members)

# ################################################################################################################################
# ################################################################################################################################

def find_app(name:'str') -> 'anydictnone':
    """ The app registration of that name, if it exists.
    """
    apps = _run_az('ad', 'app', 'list', '--display-name', name)

    for app in apps:
        if app['displayName'] == name:
            out = app
            break
    else:
        out = None

    return out

# ################################################################################################################################

def create_app(name:'str') -> 'any_':
    """ Registers the application.
    """
    logger.info(f'Creating app registration {name} ..')

    out = _run_az('ad', 'app', 'create', '--display-name', name)
    return out

# ################################################################################################################################

def ensure_service_principal(app_id:'str') -> 'str':
    """ Returns the object ID of the app's service principal, creating the principal if there is none.
    """
    # Look the principal up ..
    result = _run('ad', 'sp', 'show', '--id', app_id)

    # .. use the one that exists ..
    if result.returncode == 0:
        principal = json.loads(result.stdout)

    # .. or create a new one.
    else:
        logger.info('Creating the service principal ..')
        principal = _run_az('ad', 'sp', 'create', '--id', app_id)

    out = principal['id']
    return out

# ################################################################################################################################

def reset_credential(app_id:'str') -> 'str':
    """ Gives the app registration a new client secret and returns it.
    """
    logger.info('Creating a client secret ..')

    credential = _run_az('ad', 'app', 'credential', 'reset', '--id', app_id)

    out = credential['password']
    return out

# ################################################################################################################################

def app_exists(app_id:'str') -> 'bool':
    """ Whether the app registration still exists.
    """
    result = _run('ad', 'app', 'show', '--id', app_id)

    out = result.returncode == 0
    return out

# ################################################################################################################################

def delete_app(name:'str', app_id:'str') -> 'None':
    """ Deletes the app registration and, with it, its service principal.
    """
    logger.info(f'Deleting app registration {name} ..')
    _ = _run_az('ad', 'app', 'delete', '--id', app_id)

# ################################################################################################################################
# ################################################################################################################################
