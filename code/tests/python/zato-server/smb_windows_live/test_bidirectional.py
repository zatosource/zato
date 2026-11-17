# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from live_windows.layout import Folders, Hub, Shares

# Local
from _smb_windows_flows import assert_appeared_once, assert_consumed_once, assert_no_leftovers, file_key, \
     ModuleCtx as FlowsCtx, share_path, wait_appeared, wait_consumed

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from live_windows.progress import Monitor
    from zato.common.typing_ import strlist, strstrdict
    from _smb_windows_suite import SMBWindowsSuite

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How many files each side sends
    File_Count = 10

    # The prefixes of the files each side writes
    HR_Prefix  = 'EMP'
    ERP_Prefix = 'ORG'

    # Both sides write at the same time, each with this pause between two files, in milliseconds
    Interval_Ms = 100

# ################################################################################################################################
# ################################################################################################################################

def test_both_directions(smb_suite:'SMBWindowsSuite', version:'str', run:'str', monitor:'Monitor') -> 'None':
    """ The HR and ERP applications send files to each other at the same time, and each file reaches the other side once.
    """
    handle = smb_suite.guest(version)

    hr_numbers = smb_suite.sequences.next_numbers(ModuleCtx.File_Count)
    erp_numbers = smb_suite.sequences.next_numbers(ModuleCtx.File_Count)

    hr_names:'strlist' = []
    for number in hr_numbers:
        hr_names.append(f'{ModuleCtx.HR_Prefix}{number}.csv')

    erp_names:'strlist' = []
    for number in erp_numbers:
        erp_names.append(f'{ModuleCtx.ERP_Prefix}{number}.csv')

    # Each side reads its inbound folder, and the share is observed ..
    _ = handle.observe(run, Shares.People)
    _ = handle.consume(run, Shares.People, Folders.ERP_Inbound, f'{ModuleCtx.HR_Prefix}*.csv')
    _ = handle.consume(run, Shares.People, Folders.HR_Inbound, f'{ModuleCtx.ERP_Prefix}*.csv')

    # .. and both sides write at the same time ..
    _ = handle.produce(run, Shares.People, Folders.HR_Outbound, hr_names, interval_ms=ModuleCtx.Interval_Ms)
    _ = handle.produce(run, Shares.People, Folders.ERP_Outbound, erp_names, interval_ms=ModuleCtx.Interval_Ms)

    total = ModuleCtx.File_Count * 2

    def _all_produced() -> 'bool':
        events = monitor.events(version, 'produced', run)

        out = len(events) >= total
        return out

    monitor.wait_until(_all_produced, f'win{version} produced {total} files')

    # .. each file is relayed to the inbound folder of the other side and moved to processed on its own side.
    expected:'strstrdict' = {}
    processed:'strlist' = []

    for event in monitor.events(version, 'produced', run):

        name = event['name']

        if name.startswith(ModuleCtx.HR_Prefix):
            source_folder = Folders.HR_Outbound
            target_folder = Folders.ERP_Inbound
        else:
            source_folder = Folders.ERP_Outbound
            target_folder = Folders.HR_Inbound

        key = file_key(Shares.People, target_folder, name)
        expected[key] = event['sha256']

        path = share_path(f'{source_folder}/{Hub.Processed}', name)
        processed.append(path)

    wait_consumed(monitor, version, run, expected, 'files relayed in both directions')
    wait_appeared(monitor, version, run, processed, 'relayed files moved to processed')

    monitor.pause(FlowsCtx.Settle_Seconds)

    assert_consumed_once(monitor, version, run, expected, 'relayed files')
    assert_appeared_once(monitor, version, run, processed, 'processed relayed files')
    assert_no_leftovers(monitor, version, run, 'relayed files')

# ################################################################################################################################
# ################################################################################################################################
