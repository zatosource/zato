# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# Zato
from live_windows.docker_ import remove_container
from live_windows.enmasse import exchange_connection_name, partner_connection_name
from live_windows.layout import Hub, Shares
from live_windows.settings import Partners, Versions

# Local
from _smb_windows_flows import hub_outbox, start_hub, verify_hub, wait_produced, Fault_Stale_Temp_Ms

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from live_windows.progress import Monitor
    from _smb_windows_suite import SMBWindowsSuite

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How many files a flow consists of, and the pause between two of them, in milliseconds
    File_Count  = 20
    Interval_Ms = 200

    # How many files are written before the server restarts
    Before_Restart = 5

    # The guest that goes away in a switchover and the one that takes over from it
    Primary = Versions.Server_2025
    Standby = Partners[Primary]

# ################################################################################################################################
# ################################################################################################################################

def test_server_restart(smb_suite:'SMBWindowsSuite', version:'str', run:'str', monitor:'Monitor') -> 'None':
    """ The Zato server restarts in the middle of a flow, and the flow completes once the server is back.
    """
    handle = smb_suite.guest(version)
    conn_name = exchange_connection_name(handle.info)

    monitor.expect_server_errors(conn_name)

    start_hub(handle, run, [Hub.Plant], stale_temp_ms=Fault_Stale_Temp_Ms)

    names = smb_suite.sequences.next_names(Hub.Plant, ModuleCtx.File_Count)
    outbox = hub_outbox(Hub.Plant)
    _ = handle.produce(run, Shares.Exchange, outbox, names, interval_ms=ModuleCtx.Interval_Ms)

    _ = wait_produced(monitor, version, run, ModuleCtx.Before_Restart)

    smb_suite.restart_server()

    sources = wait_produced(monitor, version, run, ModuleCtx.File_Count)
    verify_hub(monitor, version, run, sources, 'flow across a server restart')

# ################################################################################################################################

@pytest.mark.guests(ModuleCtx.Primary, ModuleCtx.Standby)
def test_switchover(smb_suite:'SMBWindowsSuite', run:'str', monitor:'Monitor') -> 'None':
    """ The primary file server goes away, its connections are pointed to the standby one, and the flows continue there,
    with each file routed exactly once even though the connections of both guests now poll the same outboxes.
    This test removes the primary guest, which is why it runs last.
    """
    primary = smb_suite.guest(ModuleCtx.Primary)
    standby = smb_suite.guest(ModuleCtx.Standby)

    start_hub(standby, run, [Hub.Plant])

    # The primary goes away ..
    exchange_name = exchange_connection_name(primary.info)
    partner_name = partner_connection_name(primary.info)

    monitor.allow_stop(ModuleCtx.Primary)
    monitor.expect_server_errors(exchange_name, partner_name)

    remove_container(primary.info.name)

    # .. its connections are pointed to the standby ..
    smb_suite.import_guest(ModuleCtx.Primary, target_version=ModuleCtx.Standby, partner_version=ModuleCtx.Standby)

    try:

        # .. the files written on the standby are routed exactly once ..
        names = smb_suite.sequences.next_names(Hub.Plant, ModuleCtx.File_Count)
        outbox = hub_outbox(Hub.Plant)
        _ = standby.produce(run, Shares.Exchange, outbox, names, interval_ms=ModuleCtx.Interval_Ms)

        sources = wait_produced(monitor, ModuleCtx.Standby, run, ModuleCtx.File_Count)
        verify_hub(monitor, ModuleCtx.Standby, run, sources, 'flow on the standby after a switchover')

    # .. and the connections of the primary are pointed back to it, which closes their connections to the standby.
    finally:
        smb_suite.import_guest(ModuleCtx.Primary)

# ################################################################################################################################
# ################################################################################################################################
