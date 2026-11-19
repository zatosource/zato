# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from live_windows.layout import Folders, Hub, Shares

# Local
from _smb_windows_flows import assert_appeared_once, assert_consumed_once, assert_no_leftovers, file_key, label_name, \
     label_site, share_path, shipment_name, wait_appeared, wait_consumed, wait_produced

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from live_windows.progress import Monitor
    from zato.common.typing_ import anydict, strlist, strstrdict
    from _smb_windows_suite import SMBWindowsSuite

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How many shipment notices the test writes, half of them for each site
    Shipment_Count = 6

    # The pattern of the label trigger files that the label printing of each site reads
    Label_Pattern = 'LB*.csv'

    # The extension a trigger file gets once the label printing could not process it
    Failed_Extension = '.failed'

# ################################################################################################################################
# ################################################################################################################################

def test_labels_per_site(smb_suite:'SMBWindowsSuite', version:'str', run:'str', monitor:'Monitor') -> 'None':
    """ Each shipment notice results in a label trigger file at the site that ships it. The label printing of each site
    fails on one trigger file, which the hub then moves to the failed directory of that site.
    """
    handle = smb_suite.guest(version)

    numbers = smb_suite.sequences.next_numbers(ModuleCtx.Shipment_Count)

    # The first job of each site is the one its label printing fails on ..
    fail_names:'anydict' = {}

    for number in numbers:
        site = label_site(number)
        if site not in fail_names:
            fail_names[site] = [label_name(number)]

    # .. each site's printing reads its own folder, and the shipping and labels shares are observed ..
    _ = handle.observe(run, Shares.Shipping)
    _ = handle.observe(run, Shares.Labels)

    for site in Folders.Label_Sites:
        _ = handle.consume(run, Shares.Labels, site, ModuleCtx.Label_Pattern, fail_names=fail_names[site])

    # .. and the notices are written ..
    names:'strlist' = []

    for number in numbers:
        name = shipment_name(number)
        names.append(name)

    _ = handle.produce(run, Shares.Shipping, Folders.Shipping_Outbox, names)

    sources = wait_produced(monitor, version, run, ModuleCtx.Shipment_Count)

    # .. each notice turns into a trigger file at its site, with the content of the notice ..
    expected:'strstrdict' = {}
    processed:'strlist' = []
    failed:'strlist' = []

    for number in numbers:
        site = label_site(number)
        notice = shipment_name(number)
        label = label_name(number)

        key = file_key(Shares.Labels, site, label)
        expected[key] = sources[notice]

        path = share_path(f'{Folders.Shipping_Outbox}/{Hub.Processed}', notice)
        processed.append(path)

        if label in fail_names[site]:
            failed_label = label.replace('.csv', ModuleCtx.Failed_Extension)
            path = share_path(f'{site}/{Folders.Label_Failed}', failed_label)
            failed.append(path)

    wait_consumed(monitor, version, run, expected, 'label trigger files printed')
    wait_appeared(monitor, version, run, processed, 'shipment notices moved to processed')

    # .. and the trigger files that failed are moved out of the way.
    wait_appeared(monitor, version, run, failed, 'failed trigger files moved to the failed directories')

    monitor.settle()

    assert_consumed_once(monitor, version, run, expected, 'label trigger files')
    assert_appeared_once(monitor, version, run, processed, 'processed shipment notices')
    assert_appeared_once(monitor, version, run, failed, 'failed trigger files')
    assert_no_leftovers(monitor, version, run, 'label trigger files')

    marked = monitor.names(version, 'marked-failed', run)
    assert len(marked) == len(Folders.Label_Sites), f'Expected one failed trigger file per site, got {marked}'

# ################################################################################################################################
# ################################################################################################################################
