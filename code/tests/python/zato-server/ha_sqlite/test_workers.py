# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The processes of the Zato server on the active node - a worker terminated with SIGKILL is respawned by the arbiter
# while the node keeps its role, and an arbiter terminated with SIGKILL takes every worker with it, after which
# the supervisor of the node starts the server again. A takeover with N workers takes no longer than a bound
# of the takeover with one worker.

# stdlib
import logging
import os
import signal
import time
from threading import Event, Thread

# Zato
from ha_checks import check_workload
from ha_env import ready_pair
from nodes import ModuleCtx as NodesCtx, Timers
from topology import docker
from workload import Workload
from zato.common.test.conftest_base_multi_cpu import WorkerControl
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from ha_env import HAEnvironment, HASession
    from nodes import Node
    from zato.common.typing_ import any_, anydict, intlist, strlist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.ha_sqlite.workers')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How often the roles of both nodes are read while a fault is in effect, in seconds
    Role_Poll_Interval = 0.25

    # How long the workers of a terminated arbiter may take to terminate, in seconds
    Worker_Exit_Timeout = 10

    # How often the processes of the node are read while the test waits for them to terminate, in seconds
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

    # The worker count of the server whose takeover is the reference
    Reference_Worker_Count = 1

    # How many times the takeover of the reference server, plus a margin in seconds, a takeover with N workers may take
    Takeover_Factor = 2.0
    Takeover_Margin = 15.0

# ################################################################################################################################
# ################################################################################################################################

class ContainerWorkerControl(WorkerControl):
    """ Reads the slots of the server of a node and sends signals to its processes inside the container of the node.
    """

    def __init__(self, node:'Node', invoke_password:'str') -> 'None':
        super().__init__(node.server_url, invoke_password)
        self.container_name = node.container_name

# ################################################################################################################################

    def execute(self, script:'str') -> 'str':
        """ Runs a shell script inside the container of the node and returns its output.
        """
        result = docker('exec', self.container_name, 'sh', '-c', script)

        out = result.stdout
        return out

# ################################################################################################################################

    def send_signal(self, slot:'int', signal_number:'int') -> 'anydict':
        row = self.get_slot(slot)
        _ = self.execute(f'kill -{signal_number} {row["pid"]}')
        return row

# ################################################################################################################################

    def get_arbiter_pid(self) -> 'int':
        """ Returns the PID of the arbiter, the parent of each worker.
        """
        worker_pid = self.get_slots()[0]['pid']
        output = self.execute(f'sed -n "s/^PPid:[[:space:]]*//p" /proc/{worker_pid}/status')

        out = int(output.strip())
        return out

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

def test_worker_kill_on_active_node(ha_session:'HASession', ha_pair:'HAEnvironment') -> 'None':
    """ SIGKILL of the worker of each slot on the active node results in a respawn by the arbiter,
    with no takeover and no change of the role of either node.
    """
    env = ha_pair

    active = _get_active(env)
    standby = env.get_other(active)

    control = ContainerWorkerControl(active, ha_session.invoke_password)
    slots = control.wait_for_all_ready()

    generation = active.read_generation_file()

    watch = RoleWatch(active, standby)
    watch.start()

    try:
        for row in slots:
            slot = row['slot']

            killed = control.kill(slot)
            logger.info('Killed slot %s on %s -> %s', slot, active.node_name, killed)

            respawned = control.wait_for_respawn(slot, killed['generation'])
            logger.info('Respawned slot %s on %s -> %s', slot, active.node_name, respawned)

            assert respawned['pid'] != killed['pid'], f'Slot {slot} kept PID {killed["pid"]}'

    finally:
        watch.stop()

    assert watch.deviations == [], f'Roles changed while workers were respawned -> {watch.deviations}'
    assert active.read_generation_file() == generation, f'{active.node_name} took over again'

    _ = env.wait_for_pair(ModuleCtx.Server_Timeout)

# ################################################################################################################################

def test_arbiter_kill_on_active_node(ha_session:'HASession', ha_pair:'HAEnvironment') -> 'None':
    """ SIGKILL of the arbiter on the active node terminates every worker, and the supervisor of the node
    then starts the server again, whose pidfile, listening port and barrier socket are free by then,
    so the server starts every worker.
    """
    env = ha_pair

    active = _get_active(env)

    control = ContainerWorkerControl(active, ha_session.invoke_password)
    slots = control.wait_for_all_ready()

    arbiter_pid = control.get_arbiter_pid()

    worker_pids:'intlist' = []
    start_times:'dict[int, str]' = {}

    for row in slots:
        pid = row['pid']
        worker_pids.append(pid)
        start_times[pid] = control.get_start_time(pid)

    _ = control.execute(f'kill -{signal.SIGKILL} {arbiter_pid}')
    logger.info('Killed the arbiter %s on %s, workers -> %s', arbiter_pid, active.node_name, worker_pids)

    # Each worker of the arbiter terminates, and a process that reuses its PID afterwards has a start time of its own ..
    deadline = time.monotonic() + ModuleCtx.Worker_Exit_Timeout
    remaining = list(worker_pids)

    while remaining:
        assert time.monotonic() < deadline, f'Workers {remaining} outlived the arbiter {arbiter_pid}'

        still_running:'intlist' = []

        for pid in remaining:
            if control.get_start_time(pid) == start_times[pid]:
                still_running.append(pid)

        remaining = still_running
        time.sleep(ModuleCtx.Poll_Interval)

    # .. the node keeps running and its supervisor starts the server again ..
    assert active.is_running(), f'{active.node_name} stopped instead of its server'
    _ = active.wait_until_server_up(ModuleCtx.Server_Timeout)

    # .. which starts the worker of every slot under a new arbiter.
    restarted = control.wait_for_all_ready()

    assert len(restarted) == len(slots), f'Slots after the restart -> {restarted}, before -> {slots}'
    assert control.get_arbiter_pid() != arbiter_pid, f'Arbiter {arbiter_pid} still running'

    for row in restarted:
        assert row['pid'] not in worker_pids, f'Slot {row["slot"]} kept PID {row["pid"]}'

    _ = env.wait_for_pair(ModuleCtx.Server_Timeout)

# ################################################################################################################################

def test_node_stop_under_load(ha_pair:'HAEnvironment') -> 'None':
    """ A graceful stop of the active node under REST and pub/sub traffic drains every worker before STOP_GRACE,
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

    # The node stops its server first, which takes STOP_GRACE or longer only if a worker did not drain in time
    active.stop()
    stop_duration = time.monotonic() - started

    logger.info('Stop of %s with %s workers took %.3fs', active.node_name, os.environ[NodesCtx.Worker_Count_Env], stop_duration)

    assert stop_duration < ModuleCtx.Stop_Grace, f'Stop of {active.node_name} took {stop_duration:.3f}s'

    _ = standby.wait_for_role(list(NodesCtx.Active_Roles), ModuleCtx.Takeover_Timeout)
    _ = standby.wait_until_server_up(ModuleCtx.Server_Timeout)

    active.resume()
    workload.fault_windows.append((started_at, time.time()))

    _ = env.wait_for_pair(ModuleCtx.Server_Timeout)
    check_workload(env, workload)

# ################################################################################################################################

def _measure_takeover(session:'HASession', test_name:'str', worker_count:'int', monkeypatch:'any_') -> 'float':
    """ Returns how long, in seconds, a pair whose servers run the given number of workers takes from the kill
    of the active node until the worker of every slot of the new active node is ready.
    """
    monkeypatch.setenv(NodesCtx.Worker_Count_Env, str(worker_count))

    with ready_pair(session, f'{test_name}-{worker_count}', Timers(), []) as env:

        active = _get_active(env)
        standby = env.get_other(active)

        started = time.monotonic()
        active.kill()

        _ = standby.wait_for_role(list(NodesCtx.Active_Roles), ModuleCtx.Takeover_Timeout)
        _ = standby.wait_until_server_up(ModuleCtx.Server_Timeout)

        control = ContainerWorkerControl(standby, session.invoke_password)
        slots = control.wait_for_all_ready()

        out = time.monotonic() - started

        assert len(slots) == worker_count, f'Slots of {standby.node_name} -> {slots}, expected {worker_count}'

        active.resume()

    logger.info('Takeover with %s workers took %.3fs', worker_count, out)

    return out

# ################################################################################################################################

def test_takeover_duration(ha_session:'HASession', request:'any_', monkeypatch:'any_') -> 'None':
    """ The time from the kill of the active node until every slot of the new active node is ready, with N workers,
    stays within a bound of the time with one worker.
    """
    worker_count = int(os.environ[NodesCtx.Worker_Count_Env])

    reference = _measure_takeover(ha_session, request.node.name, ModuleCtx.Reference_Worker_Count, monkeypatch)
    measured = _measure_takeover(ha_session, request.node.name, worker_count, monkeypatch)

    bound = reference * ModuleCtx.Takeover_Factor + ModuleCtx.Takeover_Margin

    message = f'Takeover with {worker_count} workers took {measured:.3f}s, '
    message += f'with {ModuleCtx.Reference_Worker_Count} {reference:.3f}s, bound {bound:.3f}s'

    assert measured <= bound, message

# ################################################################################################################################
# ################################################################################################################################
