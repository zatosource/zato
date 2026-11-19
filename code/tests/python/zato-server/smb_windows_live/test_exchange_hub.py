# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from live_windows.layout import Hub, Shares

# Local
from _smb_windows_flows import assert_nothing_under, hub_outbox, hub_rejected_path, start_hub, verify_hub, wait_appeared, \
     wait_produced

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from live_windows.progress import Monitor
    from _smb_windows_suite import SMBWindowsSuite

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How many files a burst consists of, and the pause between two of them, in milliseconds
    Burst_Count       = 50
    Burst_Interval_Ms = 20

    # How many files the catalog sends to the branches at once
    Fan_Out_Count = 3

    # What the server logs for a file without content - the error the routing service raises and the name of the service
    Empty_File_Errors = 'has no content', 'file-exchange.route'

# ################################################################################################################################
# ################################################################################################################################

def test_single_file(smb_suite:'SMBWindowsSuite', version:'str', run:'str', monitor:'Monitor') -> 'None':
    """ One file in the outbox of the plant reaches the inbox of the logistics application and is moved to processed.
    """
    handle = smb_suite.guest(version)
    start_hub(handle, run, [Hub.Plant])

    names = smb_suite.sequences.next_names(Hub.Plant, 1)
    outbox = hub_outbox(Hub.Plant)
    _ = handle.produce(run, Shares.Exchange, outbox, names)

    sources = wait_produced(monitor, version, run, 1)
    verify_hub(monitor, version, run, sources, 'single file')

# ################################################################################################################################

def test_burst(smb_suite:'SMBWindowsSuite', version:'str', run:'str', monitor:'Monitor') -> 'None':
    """ A burst of files written in quick succession is routed in full, each file exactly once.
    """
    handle = smb_suite.guest(version)
    start_hub(handle, run, [Hub.Plant])

    names = smb_suite.sequences.next_names(Hub.Plant, ModuleCtx.Burst_Count)
    outbox = hub_outbox(Hub.Plant)
    _ = handle.produce(run, Shares.Exchange, outbox, names, interval_ms=ModuleCtx.Burst_Interval_Ms)

    sources = wait_produced(monitor, version, run, ModuleCtx.Burst_Count)
    verify_hub(monitor, version, run, sources, 'burst')

# ################################################################################################################################

def test_fan_out(smb_suite:'SMBWindowsSuite', version:'str', run:'str', monitor:'Monitor') -> 'None':
    """ Each file of the catalog reaches the inbox of every branch.
    """
    handle = smb_suite.guest(version)
    start_hub(handle, run, [Hub.Catalog])

    names = smb_suite.sequences.next_names(Hub.Catalog, ModuleCtx.Fan_Out_Count)
    outbox = hub_outbox(Hub.Catalog)
    _ = handle.produce(run, Shares.Exchange, outbox, names)

    sources = wait_produced(monitor, version, run, ModuleCtx.Fan_Out_Count)
    verify_hub(monitor, version, run, sources, 'fan-out')

# ################################################################################################################################

def test_empty_file_rejected(smb_suite:'SMBWindowsSuite', version:'str', run:'str', monitor:'Monitor') -> 'None':
    """ A file without content is moved to the quarantine directory of its outbox and reaches no inbox.
    """
    monitor.expect_server_errors(*ModuleCtx.Empty_File_Errors)

    handle = smb_suite.guest(version)
    start_hub(handle, run, [Hub.Plant])

    names = smb_suite.sequences.next_names(Hub.Plant, 1)
    name = names[0]
    outbox = hub_outbox(Hub.Plant)
    _ = handle.produce(run, Shares.Exchange, outbox, names, size=0)

    _ = wait_produced(monitor, version, run, 1)

    rejected = hub_rejected_path(Hub.Plant, name)
    wait_appeared(monitor, version, run, [rejected], 'empty file quarantined')

    monitor.settle()

    consumed = monitor.names(version, 'consumed', run)
    assert not consumed, f'An empty file must reach no inbox, got {consumed}'

    processed_prefix = f'{outbox}/{Hub.Processed}'.replace('/', '\\')
    assert_nothing_under(monitor, version, run, processed_prefix, 'empty file')

# ################################################################################################################################
# ################################################################################################################################
