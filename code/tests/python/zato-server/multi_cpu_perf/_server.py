# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The server of the scaling measurement, which is created once and started again with each worker count,
# and the CPUs on which the server and the load generator run.

# stdlib
import logging
import os
import shutil
import signal
import subprocess
from dataclasses import dataclass
from time import monotonic, sleep

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.test.conftest_base_multi_cpu import ModuleCtx as MultiCPUCtx, MultiCPUTestConfig
from zato.common.test.conftest_base_pubsub import find_free_port, patch_server_conf, run_quickstart_and_enmasse, \
    SessionState, wait_for_server

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import intlist, list_, strlist

    intlistlist = list_[intlist]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.multi_cpu_perf.server')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The highest worker count of the measurement
    Max_Workers = 8

    # The files of the kernel that describe the cores and the frequencies of the CPUs
    Core_CPUs_Path = '/sys/devices/system/cpu/cpu{}/topology/core_cpus_list'
    Max_Frequency_Path = '/sys/devices/system/cpu/cpu{}/cpufreq/cpuinfo_max_freq'

    # The directory whose entries are the PIDs of the processes of the host, and the state of a zombie in their stat files
    Proc_Directory = '/proc'
    State_Zombie = 'Z'

    Quickstart_Prefix = 'zato_multi_cpu_perf_qs_'
    Server_Log_Copy_Name = 'server-logs-multi-cpu-perf.txt'

    Services_Path = os.path.join(os.path.dirname(__file__), '_services.py')

    # How long a server may take to drain and exit after SIGTERM, and how often its processes are checked, in seconds
    Stop_Timeout = 60
    Stop_Poll_Interval = 0.2

    # The file in the logs directory of the server to which the output of the server goes
    Output_File_Name = 'server-output.txt'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class CPULayout:

    # The CPU of each worker, one thread of each of the fastest physical cores, in the order in which workers are added
    server_cpus: 'intlist'

    # The CPUs of the load generator, on cores of which the server uses no thread
    load_cpus: 'intlist'

# ################################################################################################################################
# ################################################################################################################################

def _read_int(path:'str') -> 'int':
    with open(path) as file:
        out = int(file.read())
    return out

# ################################################################################################################################

def _is_group_running(process_group:'int') -> 'bool':
    """ Whether a process of the group still runs, other than as a zombie that its parent has not collected.
    """
    for name in os.listdir(ModuleCtx.Proc_Directory):
        if not name.isdigit():
            continue

        # A process may exit between the listing and the read
        try:
            with open(os.path.join(ModuleCtx.Proc_Directory, name, 'stat')) as stat_file:
                stat = stat_file.read()
        except FileNotFoundError:
            continue

        # The fields after the name, which may contain spaces, begin with the state, the parent PID and the process group
        fields = stat[stat.rindex(')') + 2:].split()
        state = fields[0]
        group = int(fields[2])

        if group == process_group and state != ModuleCtx.State_Zombie:
            return True

    return False

# ################################################################################################################################

def _parse_cpu_list(text:'str') -> 'intlist':
    """ Returns the CPUs of a list in the format of the kernel, such as 0-1 or 0,16.
    """
    out:'intlist' = []

    for part in text.strip().split(','):
        if '-' in part:
            first, last = part.split('-')
            out.extend(range(int(first), int(last) + 1))
        else:
            out.append(int(part))

    return out

# ################################################################################################################################

def _core_frequency_key(core:'intlist') -> 'tuple[int, int]':
    """ Orders the cores from the fastest one, and the cores of one frequency by their first CPU.
    """
    frequency = _read_int(ModuleCtx.Max_Frequency_Path.format(core[0]))
    out = (-frequency, core[0])
    return out

# ################################################################################################################################

def get_cpu_layout() -> 'CPULayout':
    """ Assigns one thread of each of the fastest physical cores to the workers, leaving the other threads of those cores
    idle, and every CPU of the remaining cores to the load generator.
    """
    available = sorted(os.sched_getaffinity(0))

    cores:'intlistlist' = []
    seen:'strlist' = []

    for cpu in available:
        with open(ModuleCtx.Core_CPUs_Path.format(cpu)) as core_file:
            core_text = core_file.read().strip()

        if core_text not in seen:
            seen.append(core_text)
            cores.append(_parse_cpu_list(core_text))

    cores.sort(key=_core_frequency_key)

    server_cores = cores[:ModuleCtx.Max_Workers]
    server_cores.sort()

    out = CPULayout()
    out.server_cpus = []
    out.load_cpus = []

    for core in server_cores:
        out.server_cpus.append(core[0])

    for core in cores[ModuleCtx.Max_Workers:]:
        out.load_cpus.extend(core)

    out.load_cpus.sort()

    if len(out.server_cpus) < ModuleCtx.Max_Workers:
        raise Exception(f'The measurement requires {ModuleCtx.Max_Workers} physical cores, found {len(out.server_cpus)}')

    if not out.load_cpus:
        raise Exception('No core remains for the load generator')

    return out

# ################################################################################################################################
# ################################################################################################################################

class PerfServer:
    """ A quickstart environment whose server is started with a given number of workers on given CPUs.
    """

    def __init__(self) -> 'None':
        self.state = SessionState(logger.name, ModuleCtx.Server_Log_Copy_Name)
        self.zato_bin = os.path.join(os.environ['ZATO_TEST_BASE_DIR'], 'code', 'bin', 'zato')
        self.invoke_password = 'test.invoke.' + CryptoManager.generate_hex_string()
        self.server_directory = ''
        self.port = 0

# ################################################################################################################################

    def create(self) -> 'None':
        """ Creates the environment, with the databases of pub/sub and of the audit log in the directory of the server
        and the service of the measurement in its pickup directory.
        """
        self.server_directory = run_quickstart_and_enmasse(
            state=self.state,
            logger=logger,
            zato_bin=self.zato_bin,
            invoke_password=self.invoke_password,
            rendered_yaml='',
            quickstart_prefix=ModuleCtx.Quickstart_Prefix,
        )

        os.environ['Zato_PubSub_Generation_File'] = os.path.join(self.server_directory, 'pubsub-generation')
        os.environ['Zato_PubSub_DB_Path'] = os.path.join(self.server_directory, 'pubsub.db')
        os.environ['Zato_Audit_Log_DB_Type'] = 'sqlite'
        os.environ['Zato_Audit_Log_DB_Name'] = os.path.join(self.server_directory, 'audit.db')

        pickup_directory = os.path.join(self.server_directory, 'pickup', 'incoming', 'services')

        for source_path in (ModuleCtx.Services_Path, MultiCPUCtx.Worker_Slot_Service_Path):
            _ = shutil.copy2(source_path, pickup_directory)

# ################################################################################################################################

    def start(self, worker_count:'int', cpus:'intlist') -> 'None':
        """ Starts the server with a number of workers, whose processes run on the given CPUs alone.
        """
        self.port = find_free_port()

        environment = os.environ.copy()
        environment['Zato_Config_Bind_Port'] = str(self.port)
        environment['Zato_Broker_HTTP_Port'] = str(find_free_port())
        environment[MultiCPUCtx.Worker_Count_Env] = str(worker_count)
        _ = environment.pop('COVERAGE_PROCESS_START', None)

        patch_server_conf(self.server_directory, self.port, True)

        # The output of the server goes to a file, which no process of the measurement reads while the load runs
        output_path = os.path.join(self.server_directory, 'logs', ModuleCtx.Output_File_Name)
        output_file = open(output_path, 'ab')

        # The server inherits the affinity of the thread that starts it, and the thread receives its own again afterwards,
        # and it runs in a session of its own, whose process group a stop signals as a whole
        affinity = os.sched_getaffinity(0)
        os.sched_setaffinity(0, cpus)

        try:
            self.state.server_process = subprocess.Popen(
                [self.zato_bin, 'start', self.server_directory, '--fg'],
                env=environment,
                stdout=output_file,
                stderr=subprocess.STDOUT,
                start_new_session=True,
            )
        finally:
            os.sched_setaffinity(0, affinity)
            output_file.close()

        wait_for_server(logger, '127.0.0.1', self.port)

        MultiCPUTestConfig.host = '127.0.0.1'
        MultiCPUTestConfig.port = self.port
        MultiCPUTestConfig.server_directory = self.server_directory
        MultiCPUTestConfig.zato_bin = self.zato_bin
        MultiCPUTestConfig.base_url = f'http://127.0.0.1:{self.port}'
        MultiCPUTestConfig.invoke_password = self.invoke_password
        MultiCPUTestConfig.worker_count = worker_count

        logger.info('Server started with %s workers on CPUs %s', worker_count, cpus)

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Sends SIGTERM to every process of the server, as killpg of the server does, and waits until none remains.
        """
        server_process = self.state.server_process

        if not server_process:
            return

        process_group = server_process.pid
        os.killpg(process_group, signal.SIGTERM)

        deadline = monotonic() + ModuleCtx.Stop_Timeout

        while _is_group_running(process_group):
            if monotonic() > deadline:
                os.killpg(process_group, signal.SIGKILL)
                raise Exception(f'Server of process group {process_group} still running after {ModuleCtx.Stop_Timeout}s')
            sleep(ModuleCtx.Stop_Poll_Interval)

        _ = server_process.wait()
        self.state.server_process = None

# ################################################################################################################################

    def cleanup(self) -> 'None':
        self.stop()

        if self.state.quickstart_directory:
            shutil.rmtree(self.state.quickstart_directory)
            self.state.quickstart_directory = None

# ################################################################################################################################
# ################################################################################################################################
