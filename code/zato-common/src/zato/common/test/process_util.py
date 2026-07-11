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
    from zato.common.typing_ import any_

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
