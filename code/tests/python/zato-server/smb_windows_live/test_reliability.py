# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timezone
from uuid import uuid4

# Zato
from live_windows.docker_ import pause_container, unpause_container
from live_windows.enmasse import exchange_connection_name
from live_windows.layout import Folders, Hub, Shares
from live_windows.settings import Accounts

# Local
from _smb_windows_flows import assert_appeared_once, assert_nothing_under, document_name, hub_expected, hub_outbox, \
     share_path, start_hub, verify_hub, wait_appeared, wait_consumed, wait_produced

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from live_windows.progress import Monitor
    from zato.common.typing_ import strlist
    from _smb_windows_suite import SMBWindowsSuite

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How many files a test produces while its fault is in effect, and the pause between two of them, in milliseconds
    File_Count  = 20
    Interval_Ms = 200

    # How many files are produced before a fault is applied
    Before_Fault = 5

    # How many files compete for the claims of two schedules, and the pause between two of them, in milliseconds
    Contention_Count       = 30
    Contention_Interval_Ms = 20

    # How long the SMB port is blocked and how long a guest is paused, in milliseconds and seconds,
    # each longer than the interval of the schedules, so that at least one run meets the fault
    Block_Ms      = 2000
    Pause_Seconds = 2

    # How many files are sent before and after a password change
    Rotation_Batch = 5

    # How many documents are written while their share is removed, and how long the share stays removed, in seconds
    Document_Count       = 3
    Share_Absent_Seconds = 3

    # The Windows events that the SMB server logs while it is restarted, blocked, paused or asked for a removed share
    SMB_Server_Events = 'SMBServer',

    # The Windows events of a logon with a password that was changed - the failed logon in the Security log
    # and the failed authentication that the SMB server logs
    Logon_Failure_Events = 'Security', 'SMBServer'

# ################################################################################################################################
# ################################################################################################################################

def _wait_for_event(monitor:'Monitor', version:'str', run:'str', kind:'str') -> 'None':

    def _has_event() -> 'bool':
        out = monitor.has_event(version, kind, run)
        return out

    monitor.wait_until(_has_event, f'win{version} reported {kind}')

# ################################################################################################################################

def _start_plant_flow(smb_suite:'SMBWindowsSuite', version:'str', run:'str', monitor:'Monitor') -> 'None':
    """ Starts the hub flow of the plant and waits until its first files are written, so that the fault that follows
    hits a flow in progress.
    """
    handle = smb_suite.guest(version)
    start_hub(handle, run, [Hub.Plant])

    names = smb_suite.sequences.next_names(Hub.Plant, ModuleCtx.File_Count)
    outbox = hub_outbox(Hub.Plant)
    _ = handle.produce(run, Shares.Exchange, outbox, names, interval_ms=ModuleCtx.Interval_Ms)

    _ = wait_produced(monitor, version, run, ModuleCtx.Before_Fault)

# ################################################################################################################################

def _finish_plant_flow(version:'str', run:'str', monitor:'Monitor', what:'str') -> 'None':
    sources = wait_produced(monitor, version, run, ModuleCtx.File_Count)
    verify_hub(monitor, version, run, sources, what)

# ################################################################################################################################

def _expect_outage(smb_suite:'SMBWindowsSuite', version:'str', monitor:'Monitor') -> 'None':
    """ Declares what a guest that cannot be reached makes the server and Windows report.
    """
    handle = smb_suite.guest(version)
    conn_name = exchange_connection_name(handle.info)

    monitor.expect_server_errors(conn_name)
    monitor.expect_windows_events(*ModuleCtx.SMB_Server_Events)

# ################################################################################################################################
# ################################################################################################################################

def test_claim_contention(smb_suite:'SMBWindowsSuite', version:'str', run:'str', monitor:'Monitor') -> 'None':
    """ Two schedules poll the same outbox, and each file is still routed exactly once.
    """
    smb_suite.import_guest(version, has_contending_schedule=True)

    try:
        handle = smb_suite.guest(version)
        start_hub(handle, run, [Hub.Plant])

        names = smb_suite.sequences.next_names(Hub.Plant, ModuleCtx.Contention_Count)
        outbox = hub_outbox(Hub.Plant)
        _ = handle.produce(run, Shares.Exchange, outbox, names, interval_ms=ModuleCtx.Contention_Interval_Ms)

        sources = wait_produced(monitor, version, run, ModuleCtx.Contention_Count)
        verify_hub(monitor, version, run, sources, 'contended claims')

    finally:
        smb_suite.import_guest(version)

# ################################################################################################################################

def test_smb_service_restart(smb_suite:'SMBWindowsSuite', version:'str', run:'str', monitor:'Monitor') -> 'None':
    """ The SMB server of the guest restarts in the middle of a flow, and the flow completes once it is back.
    """
    _start_plant_flow(smb_suite, version, run, monitor)
    _expect_outage(smb_suite, version, monitor)

    monitor.suspend(version)
    smb_suite.guest(version).restart_smb_service(run)

    _wait_for_event(monitor, version, run, 'fault-ended')
    monitor.resume(version)

    _finish_plant_flow(version, run, monitor, 'flow across an SMB server restart')

# ################################################################################################################################

def test_port_blocked(smb_suite:'SMBWindowsSuite', version:'str', run:'str', monitor:'Monitor') -> 'None':
    """ The SMB port of the guest is blocked for a few seconds in the middle of a flow, and the flow completes once it is open.
    """
    _start_plant_flow(smb_suite, version, run, monitor)
    _expect_outage(smb_suite, version, monitor)

    monitor.suspend(version)
    smb_suite.guest(version).block_port(run, ModuleCtx.Block_Ms)

    _wait_for_event(monitor, version, run, 'fault-ended')
    monitor.resume(version)

    _finish_plant_flow(version, run, monitor, 'flow across a blocked port')

# ################################################################################################################################

def test_guest_paused(smb_suite:'SMBWindowsSuite', version:'str', run:'str', monitor:'Monitor') -> 'None':
    """ The whole guest stops for a few seconds in the middle of a flow, and the flow completes once it runs again.
    """
    _start_plant_flow(smb_suite, version, run, monitor)
    _expect_outage(smb_suite, version, monitor)

    container = smb_suite.guest(version).info.name

    monitor.suspend(version)
    pause_container(container)

    try:
        monitor.pause(ModuleCtx.Pause_Seconds)
    finally:
        unpause_container(container)

    monitor.resume(version)

    _finish_plant_flow(version, run, monitor, 'flow across a paused guest')

# ################################################################################################################################

def test_credential_rotation(smb_suite:'SMBWindowsSuite', version:'str', run:'str', monitor:'Monitor') -> 'None':
    """ The password of the account that Zato uses changes on the guest and then in Zato, and files sent before
    and after the change are all routed.
    """
    handle = smb_suite.guest(version)
    conn_name = exchange_connection_name(handle.info)

    new_password = f'Zato.Exchange.Rotated.{uuid4().hex[:8]}'

    start_hub(handle, run, [Hub.Plant])
    outbox = hub_outbox(Hub.Plant)

    # The first batch goes through with the original password ..
    names = smb_suite.sequences.next_names(Hub.Plant, ModuleCtx.Rotation_Batch)
    _ = handle.produce(run, Shares.Exchange, outbox, names)

    first_batch = wait_produced(monitor, version, run, ModuleCtx.Rotation_Batch)
    first_expected = hub_expected(first_batch)
    wait_consumed(monitor, version, run, first_expected, 'files sent before the password change')

    # .. the password changes on the guest, which makes each new logon with the old one fail until Zato has the new one ..
    monitor.expect_server_errors(conn_name)
    monitor.expect_windows_events(*ModuleCtx.Logon_Failure_Events)

    handle.set_password(run, Accounts.Exchange_Username, new_password)

    try:
        smb_suite.import_guest(version, password=new_password)

        # .. and the second batch goes through with the new one.
        names = smb_suite.sequences.next_names(Hub.Plant, ModuleCtx.Rotation_Batch)
        _ = handle.produce(run, Shares.Exchange, outbox, names)

        total = ModuleCtx.Rotation_Batch * 2
        sources = wait_produced(monitor, version, run, total)
        verify_hub(monitor, version, run, sources, 'files sent before and after the password change')

    finally:

        # The original password returns to the guest before it returns to Zato. The sessions that Zato established
        # with the new one remain valid until the connection is edited, and every schedule logs on with the original one
        # only after the edit, so no burst of failed logons reaches the lockout threshold of the guest.
        handle.set_password(run, Accounts.Exchange_Username, Accounts.Exchange_Password)
        smb_suite.import_guest(version)

# ################################################################################################################################

def test_share_removed(smb_suite:'SMBWindowsSuite', version:'str', run:'str', monitor:'Monitor') -> 'None':
    """ The documents share is removed while documents arrive, and they are processed once the share is back.
    """
    handle = smb_suite.guest(version)
    conn_name = exchange_connection_name(handle.info)

    monitor.expect_server_errors(conn_name, Shares.Documents)
    monitor.expect_windows_events(*ModuleCtx.SMB_Server_Events)

    _ = handle.observe(run, Shares.Documents)

    handle.remove_share(run, Shares.Documents)

    try:
        now = datetime.now(timezone.utc)
        numbers = smb_suite.sequences.next_numbers(ModuleCtx.Document_Count)

        names:'strlist' = []
        processed:'strlist' = []

        for number in numbers:
            name = document_name(number, now)
            names.append(name)

            path = share_path(f'{Folders.Documents_Outbox}/{Hub.Processed}', name)
            processed.append(path)

        # The files are written on the guest itself, which does not need the share ..
        _ = handle.produce(run, Shares.Documents, Folders.Documents_Outbox, names)
        _ = wait_produced(monitor, version, run, ModuleCtx.Document_Count)

        # .. and nothing is processed while the share is absent.
        monitor.pause(ModuleCtx.Share_Absent_Seconds)

        processed_prefix = share_path(Folders.Documents_Outbox, Hub.Processed)
        assert_nothing_under(monitor, version, run, processed_prefix, 'documents while their share is absent')

    finally:
        handle.restore_share(run, Shares.Documents)

    wait_appeared(monitor, version, run, processed, 'documents processed once their share is back')

    monitor.settle()
    assert_appeared_once(monitor, version, run, processed, 'documents processed once their share is back')

# ################################################################################################################################
# ################################################################################################################################
