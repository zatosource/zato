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
    from zato.common.typing_ import stranydict, strintdict, strlist, strstrdict
    from live_hl7.system import LiveSystem

# ################################################################################################################################
# ################################################################################################################################

handle_list = list[Handle]

# ################################################################################################################################
# ################################################################################################################################

# Every compose project of ours starts with this
Project_Prefix = 'zato-hl7'

# A process variable with this prefix adds what follows it, under that name, to the compose environment of the
# system a command starts - how a suite hands its own certificates or paths to a system
Extra_Environment_Prefix = 'Zato_HL7_Live_Env_'

# Set to this, the variable makes a start remove what a system keeps between runs first, so it comes up as new
Fresh_Env = 'Zato_HL7_Live_Fresh'
Fresh_Wanted = '1'

# ################################################################################################################################
# ################################################################################################################################

def _project_name(system:'LiveSystem') -> 'str':
    """ Each system has one fixed project.
    """
    out = f'{Project_Prefix}-{system.name}'
    return out

# ################################################################################################################################

def _now() -> 'str':
    now = datetime.now(timezone.utc)

    out = now.isoformat(timespec='seconds')
    return out

# ################################################################################################################################

def _build_handle(system:'LiveSystem', ports:'strintdict', extra_environment:'strstrdict') -> 'Handle':
    """ Everything a system needs to start, before anything runs. What a suite passes in the extra
    environment overrides what the system would set on its own.
    """
    password = password_for(system.password_rules)
    project_name = _project_name(system)
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
    out.environment   = extra_environment
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
        'environment':  handle.environment,
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

    exited:'strlist' = []

    for service in handle.stack.exited_services():
        if service not in system.one_off_services:
            exited.append(service)

    if exited:
        logs = handle.stack.logs(exited[0])
        raise ContainerExited(f'Container of {system.name} exited -> {exited[0]}\n{logs}')

    if error:
        raise error

    return False

# ################################################################################################################################

def _reset_kept_volumes(system:'LiveSystem', handle:'Handle') -> 'None':
    """ Removes what the system keeps between runs when the password it was installed with is not this one,
    or when a fresh start was asked for, and records the password either way.
    """
    if not system.kept_volumes:
        return

    digest = sha256(handle.password.encode('utf8')).hexdigest()

    if _wants_fresh():
        needs_removal = True
    else:
        needs_removal = read_kept_digest(system.name) != digest

    if needs_removal:
        for volume_name in system.kept_volumes:
            remove_volume(volume_name)

    write_kept_digest(system.name, digest)

# ################################################################################################################################

def _wants_fresh() -> 'bool':
    out = os.environ.get(Fresh_Env) == Fresh_Wanted
    return out

# ################################################################################################################################

def extra_environment_from_process() -> 'strstrdict':
    """ What the process environment adds to a system's compose environment, one variable per key.
    """
    out:'strstrdict' = {}

    for name, value in os.environ.items():
        if name.startswith(Extra_Environment_Prefix):
            key = name[len(Extra_Environment_Prefix):]
            out[key] = value

    return out

# ################################################################################################################################

def start(system_name:'str', *, extra_environment:'strstrdict | None'=None) -> 'Handle':
    """ Starts one system and returns when it is ready and set up.
    """
    if extra_environment is None:
        extra_environment = {}

    system = get_system(system_name)
    plan = system.port_plan()

    # The system sits on its fixed block of ports ..
    ports = plan.standalone()
    handle = _build_handle(system, ports, extra_environment)

    # .. anything a previous run of the same project left behind goes away first ..
    handle.stack.stop()

    # .. the system renders and fetches what its compose file mounts ..
    system.prepare(handle)

    # .. what the system keeps between runs has its password installed in it, so a different password starts it over,
    # as does whoever asked for a fresh start ..
    _reset_kept_volumes(system, handle)

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

    # .. and the system records itself for whoever comes looking.
    write_state(system.name, _state_data(handle))

    return handle

# ################################################################################################################################

def attach(system_name:'str') -> 'Handle':
    """ A handle to a system already running, from its state file - for a test that does not start its own.
    """
    system = get_system(system_name)
    state = read_state(system_name)

    ports = state['ports']
    extra_environment = state['environment']
    password = password_for(system.password_rules)
    environment = system.environment(ports, password)
    environment.update(extra_environment)
    compose_path = system.compose_path()

    out = Handle()
    out.system        = system.name
    out.project_name  = state['project_name']
    out.ports         = ports
    out.images        = state['images']
    out.password      = password
    out.started_at    = state['started_at']
    out.environment   = extra_environment
    out.stack         = ComposeStack(state['project_name'], compose_path, environment)

    return out

# ################################################################################################################################

def stop(system_name:'str') -> 'None':
    """ Stops a system, from its state file.
    """
    handle = attach(system_name)
    handle.stack.stop()

    remove_state(system_name)
    print(f'{system_name} stopped', flush=True)

# ################################################################################################################################

def logs(system_name:'str', service:'str'='') -> 'str':
    """ The logs of a running system.
    """
    handle = attach(system_name)

    out = handle.stack.logs(service)
    return out

# ################################################################################################################################

def describe(system_name:'str') -> 'str':
    """ What a system is and where it listens.
    """
    system = get_system(system_name)
    plan = system.port_plan()
    ports = plan.standalone()

    out = system.describe(ports)
    return out

# ################################################################################################################################

def start_group(group_name:'str') -> 'handle_list':
    """ Starts every system of a scenario group, one after another.
    """
    out:'handle_list' = []

    for system_name in get_group(group_name):
        handle = start(system_name)
        out.append(handle)

    return out

# ################################################################################################################################

def stop_group(group_name:'str') -> 'None':
    """ Stops every system of a scenario group that is running.
    """
    for system_name in get_group(group_name):
        if has_state(system_name):
            stop(system_name)

# ################################################################################################################################
# ################################################################################################################################
