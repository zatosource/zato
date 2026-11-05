# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# Zato
from faults import Duty_Cycles, get_label, Severity_Levels, Total_Loss
from process import new_scope, run_process_fault
from process_faults import ClockFault, Clock_Kinds, FileDescriptorFault, Filesystem_Kinds, FilesystemFault, \
    ScopeCPUFault, ScopeMemoryFault, ServerFreezeFault, TasksFault

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from process import ProcessEnvironment
    from zato.common.typing_ import intlist

    dutycycle = tuple[int, float]
    pathpair  = tuple[str, str]
    pathlist  = list[pathpair]

# ################################################################################################################################
# ################################################################################################################################

# The levels of a shortage of memory - its total loss, an OOM kill of the server, is what the crash suite covers.
_memory_levels:'intlist' = []

for _level in Severity_Levels:
    if _level != Total_Loss:
        _memory_levels.append(_level)

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('level', Severity_Levels)
@pytest.mark.parametrize('kind', Filesystem_Kinds)
def test_filesystem(process_environment:'ProcessEnvironment', kind:'str', level:'int') -> 'None':
    """ Item 15.4 - the writes and the fsync calls of the server, its cleanup process and PostgreSQL
    are delayed, or a percentage of them fails with EIO or ENOSPC.
    """
    targets:'pathlist' = [(process_environment.server_control, process_environment.server_prefix)]

    if process_environment.database:
        targets.append((process_environment.database_control, process_environment.database_prefix))

    scope = new_scope()
    fault = FilesystemFault(kind, targets)
    label = get_label(fault.name, level)

    run_process_fault(process_environment, scope, fault, level, label)

# ################################################################################################################################

@pytest.mark.parametrize('level', Severity_Levels)
def test_server_cpu(process_environment:'ProcessEnvironment', level:'int') -> 'None':
    """ Item 15.7 - the server loses a share of the CPU time that it used in the baseline, and is frozen at a total loss.
    """
    scope = new_scope()
    fault = ScopeCPUFault(scope)
    label = get_label(fault.name, level)

    run_process_fault(process_environment, scope, fault, level, label)

# ################################################################################################################################

@pytest.mark.parametrize('duty_cycle', Duty_Cycles)
def test_server_freeze(process_environment:'ProcessEnvironment', duty_cycle:'dutycycle') -> 'None':
    """ Item 15.7 - the server is frozen and resumed in a duty cycle.
    """
    period_seconds, frozen_seconds = duty_cycle

    scope = new_scope()
    fault = ServerFreezeFault(scope, period_seconds, frozen_seconds)
    run_process_fault(process_environment, scope, fault, Total_Loss, fault.name)

# ################################################################################################################################

@pytest.mark.parametrize('level', _memory_levels)
def test_server_memory(process_environment:'ProcessEnvironment', level:'int') -> 'None':
    """ Item 15.8 - memory.high takes away a share of the memory that the server used in the baseline.
    """
    scope = new_scope()
    fault = ScopeMemoryFault(scope)
    label = get_label(fault.name, level)

    run_process_fault(process_environment, scope, fault, level, label)

# ################################################################################################################################

def test_server_tasks(process_environment:'ProcessEnvironment') -> 'None':
    """ Item 15.10 - the server can start no thread and no process.
    """
    scope = new_scope()
    fault = TasksFault(scope)
    run_process_fault(process_environment, scope, fault, Total_Loss, fault.name)

# ################################################################################################################################

def test_server_file_descriptors(process_environment:'ProcessEnvironment') -> 'None':
    """ Item 15.10 - the server and its cleanup process can open almost no file and no connection.
    """
    scope = new_scope()
    fault = FileDescriptorFault(scope)
    run_process_fault(process_environment, scope, fault, Total_Loss, fault.name)

# ################################################################################################################################

@pytest.mark.parametrize('kind', Clock_Kinds)
def test_clock(process_environment:'ProcessEnvironment', kind:'str') -> 'None':
    """ Item 15.9 - the clock of the server moves ahead, behind, back and forth, or slows down,
    and the messages published in the meantime expire neither early nor late.
    """
    scope = new_scope()
    fault = ClockFault(kind, process_environment.timestamp_file)

    run_process_fault(process_environment, scope, fault, Total_Loss, fault.name, probes_expiration=True)

# ################################################################################################################################
# ################################################################################################################################
