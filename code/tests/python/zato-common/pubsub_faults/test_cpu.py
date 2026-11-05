# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# Zato
from faults import CPUFault, Duty_Cycles, Freeze_Autovacuum_Launcher, Freeze_Cleanup, Freeze_Client_Backend, \
    Freeze_WAL_Writer, FreezeFault, get_label, Severity_Levels, Total_Loss
from run import FaultRun

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from conftest import FaultDatabase

    dutycycle = tuple[int, float]

# ################################################################################################################################
# ################################################################################################################################

# The processes that are frozen one at a time.
_freeze_targets = [Freeze_WAL_Writer, Freeze_Autovacuum_Launcher, Freeze_Client_Backend, Freeze_Cleanup]

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('level', Severity_Levels)
def test_cpu(fault_database:'FaultDatabase', level:'int') -> 'None':
    """ Item 15.7 - PostgreSQL loses a share of the CPU time that it used in the baseline, and all of its processes
    are frozen at a total loss.
    """
    fault = CPUFault(fault_database.container)

    label = get_label(fault.name, level)

    run = FaultRun(label)
    run.run(fault, level)
    run.check()

# ################################################################################################################################

@pytest.mark.parametrize('duty_cycle', Duty_Cycles)
@pytest.mark.parametrize('target', _freeze_targets)
def test_freeze(fault_database:'FaultDatabase', target:'str', duty_cycle:'dutycycle') -> 'None':
    """ Item 15.7 - one process is frozen and resumed in a duty cycle - the WAL writer, the autovacuum launcher,
    one backend of pub/sub or the cleanup process.
    """
    period_seconds, frozen_seconds = duty_cycle

    run = FaultRun('')

    fault = FreezeFault(
        fault_database.database,
        fault_database.container,
        target,
        period_seconds,
        frozen_seconds,
        run.get_cleanup_pid,
    )

    run.label = fault.name
    run.run(fault, Total_Loss)
    run.check()

# ################################################################################################################################
# ################################################################################################################################
