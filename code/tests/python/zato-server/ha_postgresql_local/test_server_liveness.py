# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The answers of /zato/ping of a server whose processes are frozen, and the exit of a server whose configuration cannot
# be read. An active-standby node pings its server after the first answer, and counts the exits of its server, so these
# are the outcomes on which the node decides that the server failed.

# stdlib
import logging
import os
import signal
import stat
import time

# pytest
import pytest

# Zato
from local_server import bind_local_server, create_local_server, get_server_pids, is_answering, spawn_local_server, \
     start_local_server, stop_local_server
from zato.common.test.ha_limits import HALimits
from zato.common.test.reservation import reserve_port

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from local_server import LocalServer
    from zato.common.test.pubsub_database import PubSubDatabase
    from zato.common.typing_ import any_, intlist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The scopes of a freeze - the process group of the command, the worker alone and the arbiter alone
    Scope_Group   = 'group'
    Scope_Worker  = 'worker'
    Scope_Arbiter = 'arbiter'

    # The names that the server gives to its worker and to its arbiter
    Process_Name_Worker  = 'zato-worker'
    Process_Name_Arbiter = 'zato-arbiter'

    # How many pings each variant sends after the freeze, each with the timeout of the node
    Ping_Count = 3

    # The path of the configuration of the server, relative to its directory
    Server_Conf_Path = os.path.join('config', 'repo', 'server.conf')

    # The purpose under which the port of a server that never listens is reserved
    Port_Purpose = 'ha-postgresql-local-bad-start'

    # How often the exit of a server is checked, and how long the test waits for the exit before it gives up
    Exit_Poll_Interval = 0.05
    Exit_Timeout = 60.0

# The name of the process that each scope of a single process freezes
_process_names = {
    ModuleCtx.Scope_Worker:  ModuleCtx.Process_Name_Worker,
    ModuleCtx.Scope_Arbiter: ModuleCtx.Process_Name_Arbiter,
}

# ################################################################################################################################
# ################################################################################################################################

def _freeze(server:'LocalServer', scope:'str') -> 'None':
    """ Sends SIGSTOP to the processes of the server that the scope selects.
    """
    process:'any_' = server.process

    # The whole group is frozen at once ..
    if scope == ModuleCtx.Scope_Group:
        os.killpg(process.pid, signal.SIGSTOP)

    # .. while a single process is found by the name that the server gave it.
    else:
        process_name = _process_names[scope]
        pids:'intlist' = get_server_pids(server, process_name)
        assert pids, f'No process {process_name} in the server'

        for pid in pids:
            os.kill(pid, signal.SIGSTOP)

# ################################################################################################################################

def _count_answers(server:'LocalServer') -> 'int':
    """ Sends Ping_Count pings, each with the timeout of the node, and returns how many were answered with 200.
    """
    out = 0

    for _ in range(ModuleCtx.Ping_Count):

        started_at = time.monotonic()
        answered = is_answering(server.ping_url, HALimits.Server_Ping_Timeout)
        elapsed = time.monotonic() - started_at

        logger.info('Ping answered -> %s after %.3fs', answered, elapsed)

        if answered:
            out += 1

        time.sleep(HALimits.Server_Ping_Interval)

    return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('scope', [ModuleCtx.Scope_Group, ModuleCtx.Scope_Worker, ModuleCtx.Scope_Arbiter])
def test_ping_under_freeze(pubsub_database:'PubSubDatabase', scope:'str') -> 'None':
    """ A frozen process group or a frozen worker leaves every ping of the node unanswered,
    while a frozen arbiter alone leaves the worker answering every ping.
    """
    server = create_local_server(pubsub_database)

    try:

        # The server answers before the freeze ..
        _ = start_local_server(server)
        assert is_answering(server.ping_url, HALimits.Server_Ping_Timeout)

        # .. its processes of the scope are frozen ..
        _freeze(server, scope)

        # .. and the pings of the node are answered only if the worker still runs.
        answer_count = _count_answers(server)

        if scope == ModuleCtx.Scope_Arbiter:
            assert answer_count == ModuleCtx.Ping_Count, answer_count
        else:
            assert answer_count == 0, answer_count

    finally:
        stop_local_server(server)

# ################################################################################################################################

def test_unreadable_config_exits(pubsub_database:'PubSubDatabase') -> 'None':
    """ A server whose configuration cannot be read exits with a non-zero code within Server_Bad_Start,
    so that its node counts an exit rather than a start that never answers.
    """
    server = create_local_server(pubsub_database)
    port = reserve_port(ModuleCtx.Port_Purpose)
    server_conf_path = os.path.join(server.server_dir, ModuleCtx.Server_Conf_Path)

    try:

        # The configuration of the server, with its port, cannot be read ..
        bind_local_server(server, port.port)
        os.chmod(server_conf_path, 0)

        # .. the server is started by the command of the node ..
        spawn_local_server(server, port.port)

        process:'any_' = server.process
        deadline = server.spawned_at + ModuleCtx.Exit_Timeout

        while process.poll() is None:
            if time.monotonic() > deadline:
                break
            time.sleep(ModuleCtx.Exit_Poll_Interval)

        exited_after = time.monotonic() - server.spawned_at
        logger.info('Server with an unreadable configuration -> exit code %s after %.3fs', process.returncode, exited_after)

        # .. and it exits by itself, with an error, within the limit.
        assert process.returncode is not None, f'Server still runs after {exited_after:.3f}s'
        assert process.returncode != 0, process.returncode
        assert exited_after < HALimits.Server_Bad_Start, exited_after

    finally:
        os.chmod(server_conf_path, stat.S_IRUSR | stat.S_IWUSR)
        stop_local_server(server)
        port.release()

# ################################################################################################################################
# ################################################################################################################################
