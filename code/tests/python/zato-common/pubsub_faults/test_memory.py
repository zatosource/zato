# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# Zato
from faults import get_label, MemoryFault, Severity_Levels
from run import FaultRun

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from conftest import FaultDatabase

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('level', Severity_Levels)
def test_memory(fault_database:'FaultDatabase', level:'int') -> 'None':
    """ Item 15.8 - PostgreSQL is held below the memory that it used in the baseline, which causes reclaim stalls,
    and at a total loss the OOM killer ends one backend, after which every backend ends and crash recovery runs.
    """
    fault = MemoryFault(fault_database.container)

    label = get_label(fault.name, level)

    run = FaultRun(label)
    run.run(fault, level)
    run.check()

# ################################################################################################################################
# ################################################################################################################################
