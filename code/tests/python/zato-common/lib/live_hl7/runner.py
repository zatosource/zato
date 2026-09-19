# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from datetime import datetime, timezone
from hashlib import sha256
from functools import partial

# Live containers
from live_containers.ready import ContainerExited, wait_until

# Live HL7
from live_hl7.compose import ComposeStack, ensure_volume, remove_volume
from live_hl7.credentials import password_for
from live_hl7.registry import get_group, get_system
from live_hl7.state import has_state, read_kept_digest, read_state, remove_state, write_kept_digest, write_state
from live_hl7.system import Handle

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict, strintdict, strstrdict
    from live_hl7.system import LiveSystem

# ################################################################################################################################
# ################################################################################################################################

handle_list = list[Handle]

# ################################################################################################################################
# ################################################################################################################################

# Every compose project of ours starts with this
Project_Prefix = 'zato-hl7'

# ################################################################################################################################
# ################################################################################################################################

def _project_name(system:'LiveSystem', is_standalone:'bool') -> 'str':
    """ Standalone systems have one fixed project each, a test's systems carry its process id
    so they never collide with a standalone one.
    """
    if is_standalone:
        out = f'{Project_Prefix}-{system.name}'
    else:
        out = f'{Project_Prefix}-{system.name}-{os.getpid()}'

    return out

# ################################################################################################################################

def _now() -> 'str':
    now = datetime.now(timezone.utc)

    out = now.isoformat(timespec='seconds')
    return out

# ################################################################################################################################

def _build_handle(
    system:'LiveSystem',
    ports:'strintdict',
    is_standalone:'bool',
    extra_environment:'strstrdict',
    ) -> 'Handle':
    """ Everything a system needs to start, before anything runs. What a suite passes in the extra
    environment overrides what the system would set on its own.
    """
    password = password_for(system.password_rules)
    project_name = _project_name(system, is_standalone)
    environment = system.environment(ports, password)
    environment.update(extra_environment)
    compose_path = system.compose_path()

    out = Handle()
    out.system        = system.name
    out.project_name  = project_name
    out.ports         = ports
    out.images        = dict(system.images)
    out.password      = password
    out.started_at    = _now()
    out.is_standalone = is_standalone
    out.stack         = ComposeStack(project_name, compose_path, environment)

    return out

# ################################################################################################################################

def _state_data(handle:'Handle') -> 'stranydict':
    out:'stranydict' = {
        'system':       handle.system,
        'project_name': handle.project_name,
        'ports':        handle.ports,
        'images':       handle.images,
        'started_at':   handle.started_at,
    }

    return out

# ################################################################################################################################

def _is_ready_or_gone(system:'LiveSystem', handle:'Handle') -> 'bool':
    """ The system's own readiness check, unless a container of its has exited, which ends the wait with
    that container's output - there is nothing left to wait for and the output says why.
    """
    # A check that raises is a check that says no, which the wait knows how to report - but only after
    # the containers have been looked at, since a container that is gone is the better explanation.
    try:
        is_ready = system.is_ready(handle)
        error = None
    except Exception as e:
        is_ready = False
        error = e

    if is_ready:
        return True

    exited = handle.stack.exited_services()

    if exited:
        logs = handle.stack.logs(exited[0])
        raise ContainerExited(f'Container of {system.name} exited -> {exited[0]}\n{logs}')

    if error:
        raise error

    return False

# ################################################################################################################################

def _reset_kept_volumes_on_new_password(system:'LiveSystem', handle:'Handle') -> 'None':
    if not system.kept_volumes:
        return

    digest = sha256(handle.password.encode('utf8')).hexdigest()

    if read_kept_digest(system.name) == digest:
        return

    for volume_name in system.kept_volumes:
        remove_volume(volume_name)

    write_kept_digest(system.name, digest)

# ################################################################################################################################

def start(system_name:'str', *, is_standalone:'bool', extra_environment:'strstrdict | None'=None) -> 'Handle':
    """ Starts one system and returns when it is ready and set up.
    """
    if extra_environment is None:
        extra_environment = {}

    system = get_system(system_name)
    plan = system.port_plan()

    # Standalone systems sit on their fixed block, a test takes whatever is free ..
    if is_standalone:
        ports = plan.standalone()
    else:
        ports = plan.for_test()

    handle = _build_handle(system, ports, is_standalone, extra_environment)

    # .. anything a previous run of the same project left behind goes away first ..
    handle.stack.stop()

    # .. the system renders and fetches what its compose file mounts ..
    system.prepare(handle)

    # .. what the system keeps between runs has its password installed in it, so a different password starts it over ..
    _reset_kept_volumes_on_new_password(system, handle)

    # .. and what it keeps is there before its containers look for it ..
    for volume_name in system.kept_volumes:
        ensure_volume(volume_name)

    # .. the containers come up ..
    print(f'Starting {system.name} as {handle.project_name}', flush=True)
    handle.stack.start()

    # .. whatever the system needs done before it can come up runs now ..
    system.after_start(handle)

    # .. we wait until the system answers, or until one of its containers gives up ..
    check = partial(_is_ready_or_gone, system, handle)
    wait_until(check, system.name)

    # .. its first-start setup runs ..
    system.after_ready(handle)
    print(f'{system.name} is ready', flush=True)

    # .. and a standalone system records itself for whoever comes looking.
    if is_standalone:
        write_state(system.name, _state_data(handle))

    return handle

# ################################################################################################################################

def stop_handle(handle:'Handle') -> 'None':
    """ Stops a system started in this process.
    """
    handle.stack.stop()

    if handle.is_standalone:
        remove_state(handle.system)

# ################################################################################################################################

def attach(system_name:'str') -> 'Handle':
    """ A handle to a system already running standalone, from its state file - for a test that does not start
    its own.
    """
    system = get_system(system_name)
    state = read_state(system_name)

    ports = state['ports']
    password = password_for(system.password_rules)
    environment = system.environment(ports, password)
    compose_path = system.compose_path()

    out = Handle()
    out.system        = system.name
    out.project_name  = state['project_name']
    out.ports         = ports
    out.images        = state['images']
    out.password      = password
    out.started_at    = state['started_at']
    out.is_standalone = True
    out.stack         = ComposeStack(state['project_name'], compose_path, environment)

    return out

# ################################################################################################################################

def stop(system_name:'str') -> 'None':
    """ Stops a standalone system, from its state file.
    """
    handle = attach(system_name)
    handle.stack.stop()

    remove_state(system_name)
    print(f'{system_name} stopped', flush=True)

# ################################################################################################################################

def logs(system_name:'str', service:'str'='') -> 'str':
    """ The logs of a standalone system.
    """
    handle = attach(system_name)

    out = handle.stack.logs(service)
    return out

# ################################################################################################################################

def describe(system_name:'str') -> 'str':
    """ What a system is and where it would listen standalone.
    """
    system = get_system(system_name)
    plan = system.port_plan()
    ports = plan.standalone()

    out = system.describe(ports)
    return out

# ################################################################################################################################

def start_group(group_name:'str', *, is_standalone:'bool') -> 'handle_list':
    """ Starts every system of a scenario group, one after another.
    """
    out:'handle_list' = []

    for system_name in get_group(group_name):
        handle = start(system_name, is_standalone=is_standalone)
        out.append(handle)

    return out

# ################################################################################################################################

def stop_group(group_name:'str') -> 'None':
    """ Stops every standalone system of a scenario group that is running.
    """
    for system_name in get_group(group_name):
        if has_state(system_name):
            stop(system_name)

# ################################################################################################################################
# ################################################################################################################################
