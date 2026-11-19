# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import signal
import subprocess
import time

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, intdict, intlist, intset, strlist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# How long to wait for a process group to exit cleanly before it goes down hard
_Kill_Timeout = 5

# How often a killed process is checked for having exited, in seconds
_Exit_Poll_Seconds = 0.05

# The state in /proc of a process that exited and was not reaped yet
_Zombie_State = 'Z'

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

    # The entry disappears when the process is reaped, which can happen between the open and the read.
    except (FileNotFoundError, ProcessLookupError):
        return True

    # The state follows the process name, which is in parentheses and may contain spaces.
    _, _, remainder = stat.rpartition(')')
    fields = remainder.split()
    state = fields[0]

    out = state == _Zombie_State
    return out

# ################################################################################################################################

def _refers_to_prefixes(pid:'int', prefixes:'strlist') -> 'bool':
    """ Returns whether the working directory or an argument of the command line of a process contains one of the prefixes.
    """
    try:
        working_directory = os.readlink(f'/proc/{pid}/cwd')

        with open(f'/proc/{pid}/cmdline', 'rb') as cmdline_file:
            cmdline = cmdline_file.read()

    # The process exited in the meantime, or it belongs to another user, in which case it was not started by this user's tests.
    except (FileNotFoundError, ProcessLookupError, PermissionError):
        return False

    # The arguments of the command line are separated with null bytes
    text = cmdline.decode('utf8', errors='replace')
    values = text.split('\0')
    values.append(working_directory)

    for value in values:
        for prefix in prefixes:
            if prefix in value:
                return True

    return False

# ################################################################################################################################

def _send_signal(pid:'int', signal_number:'int') -> 'None':
    try:
        os.kill(pid, signal_number)

    # The process exited already
    except ProcessLookupError:
        pass

# ################################################################################################################################

def kill_processes_in_directories(prefixes:'strlist') -> 'None':
    """ Kills every process whose working directory or command line refers to a path under one of the prefixes,
    together with every process that descends from it, e.g. a server and a listener that an interrupted run left behind.
    """
    pids:'intset' = set()
    current_pid = os.getpid()

    for name in os.listdir('/proc'):

        if not name.isdigit():
            continue

        pid = int(name)

        # The process that runs the tests never kills itself
        if pid == current_pid:
            continue

        if _refers_to_prefixes(pid, prefixes):
            tree_pids = get_process_tree_pids(pid)
            pids.update(tree_pids)

    if not pids:
        return

    logger.info('Killing processes left behind in %s -> %s', prefixes, sorted(pids))

    # Each process is given a chance to exit cleanly first ..
    for pid in pids:
        _send_signal(pid, signal.SIGTERM)

    deadline = time.monotonic() + _Kill_Timeout

    for pid in pids:
        while not _has_exited(pid):
            if time.monotonic() > deadline:
                break
            time.sleep(_Exit_Poll_Seconds)

    # .. and each one that is still running is killed.
    for pid in pids:
        if not _has_exited(pid):
            _send_signal(pid, signal.SIGKILL)

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
