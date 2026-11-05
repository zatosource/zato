# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# Zato
from faults import DiskFault, get_label, Severity_Levels
from run import FaultRun

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from conftest import FaultDatabase

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('level', Severity_Levels)
def test_disk(fault_database:'FaultDatabase', level:'int') -> 'None':
    """ Item 15.3 - the disk of PostgreSQL loses a share of the bandwidth and of the operations per second
    that it used in the baseline, which slows down checkpoints, WAL writes and commits.
    """
    fault = DiskFault(fault_database.container, fault_database.device)

    label = get_label(fault.name, level)

    run = FaultRun(label)
    run.run(fault, level)
    run.check()

# ################################################################################################################################
# ################################################################################################################################
