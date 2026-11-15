# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import subprocess
from time import monotonic, sleep

# local
from local_docker import run_command

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import callable_, strintdict

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The prefix of the process names of the workers, which the arbiter sets through prctl
    Worker_Name_Prefix = 'zato-worker-'

    # Prints the PID and the process name of every process of the container, one per line
    List_Command = 'for path in /proc/[0-9]*/comm; do pid=${path#/proc/}; echo "${pid%/comm} $(cat $path 2>/dev/null)"; done'

    # How long the workers of a container have to appear or to be replaced, in seconds
    Process_Deadline = 120.0
    Poll_Interval = 1.0

# ################################################################################################################################
# ################################################################################################################################

def get_workers(container_name:'str') -> 'strintdict':
    """ Returns the PID of each worker of the container by the name of its process.
    """
    result = subprocess.run(['docker', 'exec', container_name, 'sh', '-c', ModuleCtx.List_Command],
        capture_output=True, text=True, check=False)

    out:'strintdict' = {}

    for line in result.stdout.splitlines():
        fields = line.split()

        # A process that ended while the list was read has no name
        if len(fields) != 2:
            continue

        pid, name = fields

        if name.startswith(ModuleCtx.Worker_Name_Prefix):
            out[name] = int(pid)

    return out

# ################################################################################################################################

def wait_for_workers(container_name:'str', is_done:'callable_', description:'str') -> 'strintdict':
    """ Waits until the workers of the container satisfy the condition and returns them.
    """
    deadline = monotonic() + ModuleCtx.Process_Deadline

    while True:
        workers = get_workers(container_name)

        if is_done(workers):
            return workers

        if monotonic() > deadline:
            raise Exception(f'{description} not reached after {ModuleCtx.Process_Deadline}s, workers -> {workers}')

        sleep(ModuleCtx.Poll_Interval)

# ################################################################################################################################

def inspect(container_name:'str', field:'str') -> 'str':
    """ Returns one field of the state of the container, such as {{.State.ExitCode}}.
    """
    result = run_command(['docker', 'inspect', '-f', field, container_name])

    out = result.stdout.strip()
    return out

# ################################################################################################################################
# ################################################################################################################################
