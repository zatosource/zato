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
from dataclasses import dataclass

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.test.conftest_base_multi_cpu import ModuleCtx as MultiCPUCtx, MultiCPUTestConfig
from zato.common.test.conftest_base_pubsub import find_free_port, run_quickstart_and_enmasse, SessionState, \
    start_server_process

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

    Quickstart_Prefix = 'zato_multi_cpu_perf_qs_'
    Server_Log_Copy_Name = 'server-logs-multi-cpu-perf.txt'

    Services_Path = os.path.join(os.path.dirname(__file__), '_services.py')

    # How long a server may take to drain and exit after SIGTERM, in seconds
    Stop_Timeout = 60

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

        # The server inherits the affinity of the thread that starts it, and the thread receives its own again afterwards
        affinity = os.sched_getaffinity(0)
        os.sched_setaffinity(0, cpus)

        try:
            _ = start_server_process(
                state=self.state,
                logger=logger,
                zato_bin=self.zato_bin,
                server_directory=self.server_directory,
                server_port=self.port,
                broker_port=find_free_port(),
                extra_server_env={MultiCPUCtx.Worker_Count_Env: str(worker_count)},
                patch_server_conf_bind=True,
            )
        finally:
            os.sched_setaffinity(0, affinity)

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
        """ Stops the server through SIGTERM, which drains and stops each of its processes, and waits until it exits.
        """
        server_process = self.state.server_process

        if server_process:
            server_process.terminate()
            _ = server_process.wait(ModuleCtx.Stop_Timeout)
            self.state.server_process = None

# ################################################################################################################################

    def cleanup(self) -> 'None':
        self.stop()

        if self.state.quickstart_directory:
            shutil.rmtree(self.state.quickstart_directory)
            self.state.quickstart_directory = None

# ################################################################################################################################
# ################################################################################################################################
