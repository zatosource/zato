# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# Zato
from faults import Duty_Cycles, get_label, High_Severity_Levels, Total_Loss
from process import get_process_env
from process_faults import ClockFault, Clock_Kinds, FileDescriptorFault, Filesystem_Kinds, FilesystemFault, \
    ScopeCPUFault, ScopeMemoryFault, ServerFreezeFault, TasksFault
from run import FaultRun

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from faults import Fault
    from process import ProcessEnvironment
    from process_faults import Scope
    from pubsub_rest.server import PubSubServer

    dutycycle = tuple[int, float]
    pathpair  = tuple[str, str]
    pathlist  = list[pathpair]

# ################################################################################################################################
# ################################################################################################################################

# The levels of a shortage of memory, which leaves a tenth of it - its total loss, an OOM kill of the server,
# is what the crash suite covers.
_memory_levels = [90]

# ################################################################################################################################
# ################################################################################################################################

def _run(
    environment:'ProcessEnvironment',
    server:'PubSubServer',
    fault:'Fault',
    level:'int',
    label:'str',
    probes_expiration:'bool'=False,
    ) -> 'None':
    """ Runs the traffic of the server in its scope through the phases of one fault, with the cleanup process
    in the same scope and with the same libraries preloaded.
    """
    cleanup_env = get_process_env(environment)

    run = FaultRun(server, label, probes_expiration=probes_expiration, cleanup_env=cleanup_env)
    run.run(fault, level)
    run.check()

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('level', High_Severity_Levels)
@pytest.mark.parametrize('kind', Filesystem_Kinds)
def test_filesystem(
    process_environment:'ProcessEnvironment',
    server_scope:'Scope',
    server:'PubSubServer',
    kind:'str',
    level:'int',
    ) -> 'None':
    """ Item 15.4 - the writes and the fsync calls of the server, its cleanup process and PostgreSQL
    are delayed, or a percentage of them fails with EIO or ENOSPC.
    """
    targets:'pathlist' = [(process_environment.server_control, process_environment.server_prefix)]

    if process_environment.database:
        targets.append((process_environment.database_control, process_environment.database_prefix))

    fault = FilesystemFault(kind, targets)
    label = get_label(fault.name, level)

    _run(process_environment, server, fault, level, label)

# ################################################################################################################################

@pytest.mark.parametrize('level', High_Severity_Levels)
def test_server_cpu(
    process_environment:'ProcessEnvironment',
    server_scope:'Scope',
    server:'PubSubServer',
    level:'int',
    ) -> 'None':
    """ Item 15.7 - the server loses a share of the CPU time that it used in the baseline, and is frozen at a total loss.
    """
    fault = ScopeCPUFault(server_scope)
    label = get_label(fault.name, level)

    _run(process_environment, server, fault, level, label)

# ################################################################################################################################

@pytest.mark.parametrize('duty_cycle', Duty_Cycles)
def test_server_freeze(
    process_environment:'ProcessEnvironment',
    server_scope:'Scope',
    server:'PubSubServer',
    duty_cycle:'dutycycle',
    ) -> 'None':
    """ Item 15.7 - the server is frozen and resumed in a duty cycle.
    """
    period_seconds, frozen_seconds = duty_cycle

    fault = ServerFreezeFault(server.get_pids, period_seconds, frozen_seconds)
    _run(process_environment, server, fault, Total_Loss, fault.name)

# ################################################################################################################################

@pytest.mark.parametrize('level', _memory_levels)
def test_server_memory(
    process_environment:'ProcessEnvironment',
    server_scope:'Scope',
    server:'PubSubServer',
    level:'int',
    ) -> 'None':
    """ Item 15.8 - memory.high takes away a share of the memory that the server used in the baseline.
    """
    fault = ScopeMemoryFault(server_scope)
    label = get_label(fault.name, level)

    _run(process_environment, server, fault, level, label)

# ################################################################################################################################

def test_server_tasks(process_environment:'ProcessEnvironment', server_scope:'Scope', server:'PubSubServer') -> 'None':
    """ Item 15.10 - the server can start no thread and no process.
    """
    fault = TasksFault(server_scope)
    _run(process_environment, server, fault, Total_Loss, fault.name)

# ################################################################################################################################

def test_server_file_descriptors(
    process_environment:'ProcessEnvironment',
    server_scope:'Scope',
    server:'PubSubServer',
    ) -> 'None':
    """ Item 15.10 - the server and its cleanup process can open almost no file and no connection.
    """
    fault = FileDescriptorFault(server_scope)
    _run(process_environment, server, fault, Total_Loss, fault.name)

# ################################################################################################################################

@pytest.mark.parametrize('kind', Clock_Kinds)
def test_clock(process_environment:'ProcessEnvironment', server_scope:'Scope', server:'PubSubServer', kind:'str') -> 'None':
    """ Item 15.9 - the clock of the server moves ahead, behind, back and forth, or slows down,
    and the messages published in the meantime expire neither early nor late.
    """
    fault = ClockFault(kind, process_environment.timestamp_file)
    _run(process_environment, server, fault, Total_Loss, fault.name, probes_expiration=True)

# ################################################################################################################################
# ################################################################################################################################
