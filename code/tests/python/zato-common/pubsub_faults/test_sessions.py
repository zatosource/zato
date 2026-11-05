# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# Zato
from faults import get_label, Severity_Levels, Total_Loss
from run import FaultRun
from sessions import Graded_Session_Kinds, SessionFault, Single_Session_Kinds

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from conftest import FaultDatabase

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('level', Severity_Levels)
@pytest.mark.parametrize('kind', Graded_Session_Kinds)
def test_backends_ended(fault_database:'FaultDatabase', kind:'str', level:'int') -> 'None':
    """ Item 15.11 - in each round, a share of the backends of pub/sub is ended or has its statement cancelled.
    """
    fault = SessionFault(fault_database.database, kind)

    label = get_label(fault.name, level)

    run = FaultRun(label)
    run.run(fault, level)
    run.check()

# ################################################################################################################################

@pytest.mark.parametrize('kind', Single_Session_Kinds)
def test_session(fault_database:'FaultDatabase', kind:'str') -> 'None':
    """ Items 15.10 and 15.11 - a session of the test locks each pub/sub table in turn, keeps a transaction open,
    stays idle in a transaction, forces a checkpoint every few seconds or holds every free connection slot.
    """
    fault = SessionFault(fault_database.database, kind)

    run = FaultRun(fault.name)
    run.run(fault, Total_Loss)
    run.check()

# ################################################################################################################################
# ################################################################################################################################
