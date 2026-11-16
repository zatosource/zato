# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The processes of the Zato server on the active node - a worker terminated with SIGKILL is respawned by the arbiter
# while the node keeps its role, and an arbiter terminated with SIGKILL takes the worker and the config process with it,
# after which the supervisor of the node starts the server again.

# stdlib
import logging
import signal
import time
from threading import Event, Thread

# Zato
from ha_checks import check_workload
from nodes import ModuleCtx as NodesCtx
from topology import docker
from workload import Workload
from zato.common.typing_ import cast_
from zato.server.arbiter_config import ModuleCtx as ArbiterCtx
from zato.server.arbiter_config_process import ConfigProcessCtx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from ha_env import HAEnvironment
    from nodes import Node
    from zato.common.typing_ import any_, intlist, strlist

    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.ha_sqlite.workers')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How often the roles of both nodes are read while a fault is in effect, in seconds
    Role_Poll_Interval = 0.25

    # How long the processes of a terminated arbiter may take to terminate, in seconds
    Process_Exit_Timeout = 10

    # How long the arbiter may take to respawn a terminated worker, in seconds
    Respawn_Timeout = 60

    # How often the processes of the node are read while the test waits for them, in seconds
    Poll_Interval = 0.25

    # How long the supervisor of the node may take to start the server again, in seconds
    Server_Timeout = 120

    # The field of /proc/<pid>/stat, counted after the name of the process, that holds the start time of the process
    Start_Time_Field = 19

    # What the shell of the container prints for a process that is no longer running
    No_Process = '-'

    # How long the standby may take to take over, in seconds
    Takeover_Timeout = 60

    # How long the traffic runs before the active node is stopped, in seconds
    Traffic_Seconds = 10

    # STOP_GRACE of the supervisor of the node, after which it sends SIGKILL to the process group of the server, in seconds
    Stop_Grace = 10

# ################################################################################################################################
# ################################################################################################################################

class ContainerProcesses:
    """ Finds the processes of the server of a node by the names of their roles and sends signals to them
    inside the container of the node.
    """

    def __init__(self, node:'Node') -> 'None':
        self.container_name = node.container_name

# ################################################################################################################################

    def execute(self, script:'str') -> 'str':
        """ Runs a shell script inside the container of the node and returns its output.
        """
        result = docker('exec', self.container_name, 'sh', '-c', script)

        out = result.stdout
        return out

# ################################################################################################################################

    def find_pids(self, process_name:'str') -> 'intlist':
        """ Returns the PIDs of the processes that list under a name.
        """
        script = 'for entry in /proc/[0-9]*; do '
        script += f'if [ "$(cat $entry/comm 2>/dev/null)" = "{process_name}" ]; then basename $entry; fi; '
        script += 'done'

        output = self.execute(script)
        out:'intlist' = []

        for line in output.split():
            out.append(int(line))

        return out

# ################################################################################################################################

    def wait_for_pid(self, process_name:'str', excluded:'intlist', timeout:'float') -> 'int':
        """ Waits until one process lists under a name, other than those excluded, and returns its PID.
        """
        deadline = time.monotonic() + timeout

        while True:
            pids = self.find_pids(process_name)

            if len(pids) == 1:
                if pids[0] not in excluded:
                    return pids[0]

            assert time.monotonic() < deadline, f'No {process_name} other than {excluded} -> {pids}'
            time.sleep(ModuleCtx.Poll_Interval)

# ################################################################################################################################

    def kill(self, pid:'int') -> 'None':
        _ = self.execute(f'kill -{signal.SIGKILL} {pid}')

# ################################################################################################################################

    def get_start_time(self, pid:'int') -> 'str':
        """ Returns the start time of a process, which tells it apart from a later process with the same PID,
        or No_Process if no process has the PID.
        """
        output = self.execute(f'cat /proc/{pid}/stat 2>/dev/null || echo "{ModuleCtx.No_Process}"')
        output = output.strip()

        if output == ModuleCtx.No_Process:
            return output

        # The name of the process is in parentheses and may hold spaces, so the fields are counted after it
        _, _, fields = output.rpartition(')')
        out = fields.split()[ModuleCtx.Start_Time_Field]

        return out

# ################################################################################################################################
# ################################################################################################################################

class RoleWatch:
    """ Reads the roles of both nodes in a thread and records each moment at which the active node did not serve
    requests or the standby did.
    """

    def __init__(self, active:'Node', standby:'Node') -> 'None':
        self.active = active
        self.standby = standby
        self.deviations:'strlist' = []
        self.is_done = Event()
        self.thread = Thread(target=self.run, daemon=True)

    def start(self) -> 'None':
        self.thread.start()

    def stop(self) -> 'None':
        self.is_done.set()
        self.thread.join()

    def run(self) -> 'None':
        while not self.is_done.is_set():

            if not self.active.is_active():
                self.deviations.append(f'{time.time():.3f} {self.active.node_name} not active')

            if self.standby.is_active():
                self.deviations.append(f'{time.time():.3f} {self.standby.node_name} active')

            time.sleep(ModuleCtx.Role_Poll_Interval)

# ################################################################################################################################
# ################################################################################################################################

def _get_active(env:'HAEnvironment') -> 'Node':
    out = env.get_active()
    assert out is not None, 'No active node'

    return out

# ################################################################################################################################

def test_worker_kill_on_active_node(ha_pair:'HAEnvironment') -> 'None':
    """ SIGKILL of the worker on the active node results in a respawn by the arbiter,
    with no takeover and no change of the role of either node.
    """
    env = ha_pair

    active = _get_active(env)
    standby = env.get_other(active)

    processes = ContainerProcesses(active)
    worker_pid = processes.wait_for_pid(ArbiterCtx.Process_Name_Worker, [], ModuleCtx.Respawn_Timeout)

    generation = active.read_generation_file()

    watch = RoleWatch(active, standby)
    watch.start()

    try:
        processes.kill(worker_pid)
        logger.info('Killed the worker %s on %s', worker_pid, active.node_name)

        respawned = processes.wait_for_pid(ArbiterCtx.Process_Name_Worker, [worker_pid], ModuleCtx.Respawn_Timeout)
        logger.info('Respawned the worker on %s -> %s', active.node_name, respawned)

        _ = active.wait_until_server_up(ModuleCtx.Server_Timeout)

    finally:
        watch.stop()

    assert watch.deviations == [], f'Roles changed while the worker was respawned -> {watch.deviations}'
    assert active.read_generation_file() == generation, f'{active.node_name} took over again'

    _ = env.wait_for_pair(ModuleCtx.Server_Timeout)

# ################################################################################################################################

def test_arbiter_kill_on_active_node(ha_pair:'HAEnvironment') -> 'None':
    """ SIGKILL of the arbiter on the active node terminates the worker and the config process, and the supervisor
    of the node then starts the server again, whose pidfile, listening port and barrier socket are free by then,
    so the server starts its processes again.
    """
    env = ha_pair

    active = _get_active(env)
    processes = ContainerProcesses(active)

    arbiter_pid = processes.wait_for_pid(ArbiterCtx.Process_Name_Arbiter, [], ModuleCtx.Respawn_Timeout)
    worker_pid = processes.wait_for_pid(ArbiterCtx.Process_Name_Worker, [], ModuleCtx.Respawn_Timeout)
    config_pid = processes.wait_for_pid(ConfigProcessCtx.Process_Name, [], ModuleCtx.Respawn_Timeout)

    child_pids = [worker_pid, config_pid]
    start_times:'dict[int, str]' = {}

    for pid in child_pids:
        start_times[pid] = processes.get_start_time(pid)

    processes.kill(arbiter_pid)
    logger.info('Killed the arbiter %s on %s, children -> %s', arbiter_pid, active.node_name, child_pids)

    # Each process of the arbiter terminates, and a process that reuses its PID afterwards has a start time of its own ..
    deadline = time.monotonic() + ModuleCtx.Process_Exit_Timeout
    remaining = list(child_pids)

    while remaining:
        assert time.monotonic() < deadline, f'Processes {remaining} outlived the arbiter {arbiter_pid}'

        still_running:'intlist' = []

        for pid in remaining:
            if processes.get_start_time(pid) == start_times[pid]:
                still_running.append(pid)

        remaining = still_running
        time.sleep(ModuleCtx.Poll_Interval)

    # .. the node keeps running and its supervisor starts the server again ..
    assert active.is_running(), f'{active.node_name} stopped instead of its server'
    _ = active.wait_until_server_up(ModuleCtx.Server_Timeout)

    # .. which starts a new worker under a new arbiter.
    _ = processes.wait_for_pid(ArbiterCtx.Process_Name_Arbiter, [arbiter_pid], ModuleCtx.Respawn_Timeout)
    _ = processes.wait_for_pid(ArbiterCtx.Process_Name_Worker, child_pids, ModuleCtx.Respawn_Timeout)

    _ = env.wait_for_pair(ModuleCtx.Server_Timeout)

# ################################################################################################################################

def test_node_stop_under_load(ha_pair:'HAEnvironment') -> 'None':
    """ A graceful stop of the active node under REST and pub/sub traffic drains the worker before STOP_GRACE,
    so the node stops before its supervisor would send SIGKILL, and the standby delivers every pending message
    after its takeover.
    """
    env = ha_pair

    workload = Workload(cast_('any_', env), cast_('any_', [env.haproxy]))
    workload.start()

    time.sleep(ModuleCtx.Traffic_Seconds)

    active = _get_active(env)
    standby = env.get_other(active)

    started_at = time.time()
    started = time.monotonic()

    # The node stops its server first, which takes STOP_GRACE or longer only if the worker did not drain in time
    active.stop()
    stop_duration = time.monotonic() - started

    logger.info('Stop of %s took %.3fs', active.node_name, stop_duration)

    assert stop_duration < ModuleCtx.Stop_Grace, f'Stop of {active.node_name} took {stop_duration:.3f}s'

    _ = standby.wait_for_role(list(NodesCtx.Active_Roles), ModuleCtx.Takeover_Timeout)
    _ = standby.wait_until_server_up(ModuleCtx.Server_Timeout)

    active.resume()
    workload.fault_windows.append((started_at, time.time()))

    _ = env.wait_for_pair(ModuleCtx.Server_Timeout)
    check_workload(env, workload)

# ################################################################################################################################
# ################################################################################################################################
