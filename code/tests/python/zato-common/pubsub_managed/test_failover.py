# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from faults import Total_Loss
from managed_faults import DelayedFailoverFault
from run import FaultRun

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.pubsub_replication import ReplicatedDatabase

# ################################################################################################################################
# ################################################################################################################################

def test_failover(failover_database:'ReplicatedDatabase', failover_delay:'int') -> 'None':
    """ The primary ends at once, and after the time that the service takes to fail over,
    the endpoint name resolves to the promoted standby, whose synchronous replication kept every commit.
    """
    fault = DelayedFailoverFault(failover_database, failover_delay)

    run = FaultRun(fault.name)
    run.run(fault, Total_Loss)
    run.check()

# ################################################################################################################################
# ################################################################################################################################
