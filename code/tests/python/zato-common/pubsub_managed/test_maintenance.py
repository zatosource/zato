# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# Zato
from faults import DiskFault, Total_Loss
from managed_faults import Maintenance_Parameter, Maintenance_Reboot, Maintenance_Upgrade, MaintenanceFault
from run import FaultRun
from zato.common.test.pubsub_database import connect, ModuleCtx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pubsub_rest.server import PubSubServer
    from zato.common.test.pubsub_database import PubSubDatabase
    from zato.common.typing_ import any_, callable_

# ################################################################################################################################
# ################################################################################################################################

# The latency that a storage scaling operation adds, as the share of the disk taken away.
_scaling_level = 50

# ################################################################################################################################
# ################################################################################################################################

def _show(database:'PubSubDatabase', name:'str') -> 'str':
    connection = connect(database, is_admin=True)

    try:
        cursor = connection.cursor()
        cursor.execute(f'show {name}')
        row:'any_' = cursor.fetchone()
        out = row[0]
    finally:
        connection.close()

    return out

# ################################################################################################################################

def _run_maintenance(request:'pytest.FixtureRequest', database:'PubSubDatabase', kind:'str') -> 'None':
    """ Runs one maintenance of the database of a test, whose server starts once the database runs.
    """
    server:'PubSubServer' = request.getfixturevalue('server')
    fault = MaintenanceFault(database, kind)

    run = FaultRun(server, fault.name)
    run.run(fault, Total_Loss)
    run.check()

# ################################################################################################################################
# ################################################################################################################################

def test_reboot(start_managed:'callable_', request:'pytest.FixtureRequest') -> 'None':
    """ The database restarts in the maintenance window or for compute scaling.
    """
    managed = start_managed('maintenance-reboot')
    _run_maintenance(request, managed.database, Maintenance_Reboot)

# ################################################################################################################################

@pytest.mark.skip(reason='PostgreSQL 19 has one minor release, 19.0, so no minor version upgrade can be run until 19.1 exists')
def test_minor_upgrade(start_managed:'callable_', request:'pytest.FixtureRequest') -> 'None':
    """ The database restarts on the next minor version of PostgreSQL.
    """
    managed = start_managed('maintenance-upgrade', image=ModuleCtx.Previous_Minor_Image)
    database = managed.database

    version_before = int(_show(database, 'server_version_num'))
    _run_maintenance(request, database, Maintenance_Upgrade)
    version_after = int(_show(database, 'server_version_num'))

    assert version_after > version_before, (version_before, version_after)

# ################################################################################################################################

def test_static_parameter(start_managed:'callable_', request:'pytest.FixtureRequest') -> 'None':
    """ A parameter that takes effect only after a restart is changed and the database restarts.
    """
    managed = start_managed('maintenance-parameter')
    database = managed.database

    _run_maintenance(request, database, Maintenance_Parameter)

    assert _show(database, 'max_locks_per_transaction') == '128'

# ################################################################################################################################

def test_storage_scaling(start_managed:'callable_', request:'pytest.FixtureRequest') -> 'None':
    """ A storage scaling operation raises the latency of the disk while the database keeps running.
    """
    managed = start_managed('maintenance-scaling')
    fault = DiskFault(managed.container, managed.device)
    server:'PubSubServer' = request.getfixturevalue('server')

    run = FaultRun(server, 'storage-scaling')
    run.run(fault, _scaling_level)
    run.check()

# ################################################################################################################################
# ################################################################################################################################
