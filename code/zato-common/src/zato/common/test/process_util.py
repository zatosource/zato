# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import signal
import subprocess

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, intdict, intlist

# ################################################################################################################################
# ################################################################################################################################

# How long to wait for a process group to exit cleanly before it goes down hard
_Kill_Timeout = 5

# ################################################################################################################################
# ################################################################################################################################

def kill_process_tree(process:'any_') -> 'None':
    """ Kills a subprocess along with every descendant it spawned. The process must have been
    started with start_new_session=True, which makes it the leader of its own process group -
    killing the group is what reaches launcher wrappers, shells, servers and gunicorn workers
    alike, including the ones whose direct parent has already exited.
    """
    if not process:
        return

    # Give the whole group a chance to exit cleanly first ..
    try:
        os.killpg(process.pid, signal.SIGTERM)

    # .. the group has no members anymore, so there is nothing to kill.
    except ProcessLookupError:
        return

    # .. wait for the group's leader to finish ..
    try:
        _ = process.wait(timeout=_Kill_Timeout)
    except subprocess.TimeoutExpired:
        pass

    # .. and take down anything in the group that is still alive.
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass

# ################################################################################################################################
# ################################################################################################################################

def _get_parent_pids() -> 'intdict':
    """ Returns the parent of each process of the system, by process ID.
    """
    out:'intdict' = {}

    for name in os.listdir('/proc'):

        if not name.isdigit():
            continue

        try:
            with open(f'/proc/{name}/stat') as stat_file:
                stat = stat_file.read()
        except FileNotFoundError:
            continue

        # The process name is in parentheses and may contain spaces, the parent follows the state after it.
        _, _, remainder = stat.rpartition(')')
        fields = remainder.split()

        pid = int(name)
        parent_pid = int(fields[1])

        out[pid] = parent_pid

    return out

# ################################################################################################################################

def get_process_tree_pids(root_pid:'int') -> 'intlist':
    """ Returns a process and every process that descends from it.
    """
    parents = _get_parent_pids()

    out:'intlist' = [root_pid]

    for pid in parents:
        ancestor = parents[pid]

        while ancestor in parents:
            if ancestor == root_pid:
                out.append(pid)
                break
            ancestor = parents[ancestor]

    return out

# ################################################################################################################################

def _has_exited(pid:'int') -> 'bool':
    """ Returns whether a process has exited, which a process that only waits to be reaped by its parent has as well.
    """
    try:
        with open(f'/proc/{pid}/stat') as stat_file:
            stat = stat_file.read()
    except FileNotFoundError:
        return True

    # The state follows the process name, which is in parentheses and may contain spaces.
    _, _, remainder = stat.rpartition(')')
    fields = remainder.split()
    state = fields[0]

    out = state == _Zombie_State
    return out

# ################################################################################################################################

def kill_process_tree_at_once(process:'any_') -> 'None':
    """ Kills a subprocess and every process that descends from it with SIGKILL, without a chance to exit cleanly,
    as a host that lost its power stops them, and waits until each of them has exited and closed its files.
    """
    pids = get_process_tree_pids(process.pid)

    for pid in pids:
        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass

    _ = process.wait(timeout=_Kill_Timeout)

    deadline = time.monotonic() + _Kill_Timeout

    for pid in pids:
        while not _has_exited(pid):
            if time.monotonic() > deadline:
                raise Exception(f'Process {pid} did not exit within {_Kill_Timeout}s of SIGKILL')
            time.sleep(_Exit_Poll_Seconds)

# ################################################################################################################################
# ################################################################################################################################
