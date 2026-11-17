# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# Zato
from faults import DiskFault, get_label, High_Severity_Levels
from run import FaultRun

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pubsub_rest.server import PubSubServer
    from conftest import FaultDatabase

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('level', High_Severity_Levels)
def test_sync_standby_disk(standby_database:'FaultDatabase', server:'PubSubServer', level:'int') -> 'None':
    """ Item 15.11 - the disk of a synchronous standby is throttled as in item 15.3, so that every commit
    on the primary waits for the standby.
    """
    fault = DiskFault(standby_database.container, standby_database.device)
    fault.name = 'sync-standby-disk'

    label = get_label(fault.name, level)

    run = FaultRun(server, label)
    run.run(fault, level)
    run.check()

# ################################################################################################################################
# ################################################################################################################################
