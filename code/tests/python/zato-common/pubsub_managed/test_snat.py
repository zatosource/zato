# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# Zato
from faults import get_label, Severity_Levels
from managed_faults import SNATFault
from run import FaultRun
from zato.common.test.pubsub_profile import Managed_Profiles

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from conftest import ManagedDatabase

# ################################################################################################################################
# ################################################################################################################################

# The processes of a fault run that connect to the database - the server of the test and its cleanup process.
_run_process_count = 2

# The SYN packets of one connection that the kernel sends before it gives up, the first one
# and the retransmissions of net.ipv4.tcp_syn_retries.
_syn_packets_per_connection = 7

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('level', Severity_Levels)
def test_snat_exhaustion(managed_database:'ManagedDatabase', level:'int') -> 'None':
    """ A share of the new connections is refused or delayed while the existing connections continue,
    and the pools open at most the connections that they hold, rather than opening them in a loop.
    """
    database = managed_database.database
    profile = Managed_Profiles[database.profile_name]

    fault = SNATFault(database.container_name)
    label = get_label(fault.name, level)

    run = FaultRun(label)
    run.run(fault, level)
    run.check()

    max_new_connections = _run_process_count * profile.pool_size * _syn_packets_per_connection
    assert fault.new_connections <= max_new_connections, (fault.new_connections, max_new_connections)

# ################################################################################################################################
# ################################################################################################################################
