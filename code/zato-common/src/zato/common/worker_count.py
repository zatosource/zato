# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The number of worker processes of a server. The [main] workers key of server.conf holds auto or a positive integer,
# and the Zato_Server_Workers environment variable overrides it. A server.conf without the key resolves to auto.
# auto is the smaller of the number of CPUs that the process may run on and the CPU quota of its cgroup v2,
# rounded up, so a server in a container with a quota of 1.5 CPUs runs two workers.

# stdlib
import os
from math import ceil

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import intlist, intnone, strnone

    intlist = intlist
    intnone = intnone
    strnone = strnone

# ################################################################################################################################
# ################################################################################################################################

class ServerWorkers:

    # The key of the [main] section of server.conf
    Config_Key = 'workers'

    # The environment variable that overrides the key
    Env_Key = 'Zato_Server_Workers'

    # The value that resolves the count from the CPUs available to the process
    Auto = 'auto'

    # The value of a server.conf without the key
    Default = Auto

    # The file of cgroup v2 that holds the CPU quota and its period, in microseconds
    CPU_Max_Path = '/sys/fs/cgroup/cpu.max'

    # The quota of a cgroup without a CPU limit
    No_Quota = 'max'

# ################################################################################################################################
# ################################################################################################################################

class WorkerCountError(Exception):
    """ Raised at startup for a worker count that is neither auto nor a positive integer.
    """

# ################################################################################################################################
# ################################################################################################################################

def get_affinity_count() -> 'int':
    """ Returns the number of CPUs that the process may run on.
    """
    cpus = os.sched_getaffinity(0)

    out = len(cpus)
    return out

# ################################################################################################################################

def get_affinity() -> 'intlist':
    """ Returns the CPUs that the process may run on, in ascending order.
    """
    cpus = os.sched_getaffinity(0)

    out = sorted(cpus)
    return out

# ################################################################################################################################

def get_worker_cpus(worker_count:'int', cpus:'intlist', cpu_limit:'intnone') -> 'intlist':
    """ Returns the CPU to which the worker of each slot pins itself, by the position of the slot,
    or an empty list when no worker is pinned.
    """
    out:'intlist' = []

    # Each worker receives a CPU of its own only when there are as many workers as CPUs ..
    if worker_count != len(cpus):
        return out

    # .. and not under a quota smaller than those CPUs, with which the scheduler shares them among the processes,
    # whereas a pinned worker could not use a CPU that another worker leaves idle.
    if cpu_limit is not None:
        if cpu_limit < len(cpus):
            return out

    out = sorted(cpus)
    return out

# ################################################################################################################################

def get_cgroup_cpu_limit(cpu_max_path:'str') -> 'intnone':
    """ Returns the CPU quota of the cgroup of the process, rounded up to whole CPUs, or None without a quota.
    """
    # A host without cgroup v2, or a process outside of any cgroup with a CPU controller, has no such file
    if not os.path.exists(cpu_max_path):
        return None

    with open(cpu_max_path) as cpu_max:
        quota, period = cpu_max.read().split()

    if quota == ServerWorkers.No_Quota:
        return None

    cpus = int(quota) / int(period)

    out = ceil(cpus)
    return out

# ################################################################################################################################

def get_auto_worker_count(affinity_count:'int', cpu_max_path:'str') -> 'int':
    """ Returns the worker count that auto resolves to.
    """
    out = affinity_count
    cpu_limit = get_cgroup_cpu_limit(cpu_max_path)

    if cpu_limit is not None:
        out = min(out, cpu_limit)

    return out

# ################################################################################################################################

def resolve_worker_count(config_value:'strnone', env_value:'strnone', affinity_count:'int', cpu_max_path:'str') -> 'int':
    """ Returns the worker count of a server from its server.conf and its environment.
    """
    # The environment variable overrides server.conf ..
    if env_value:
        value = env_value

    # .. a server.conf written before the key existed resolves to the default ..
    elif config_value is None:
        value = ServerWorkers.Default

    # .. and any other has the key.
    else:
        value = config_value

    value = value.strip()

    if value == ServerWorkers.Auto:
        out = get_auto_worker_count(affinity_count, cpu_max_path)
        return out

    error = f'Invalid worker count `{value}`, expected `{ServerWorkers.Auto}` or a positive integer'

    # Only ASCII digits form an integer, since str.isdigit accepts other digits too, e.g. superscripts ..
    if not (value.isascii() and value.isdigit()):
        raise WorkerCountError(error)

    out = int(value)

    # .. and a server runs at least one worker.
    if out == 0:
        raise WorkerCountError(error)

    return out

# ################################################################################################################################
# ################################################################################################################################
