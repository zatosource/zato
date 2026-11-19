# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timezone

# pytest
import pytest

# Zato
from live_windows.layout import Folders, Hub, Shares
from live_windows.settings import Partners

# Local
from _smb_windows_flows import archive_path, assert_appeared_once, assert_consumed_once, assert_no_leftovers, \
     document_name, file_key, share_path, wait_appeared, wait_consumed, wait_produced

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from live_windows.progress import Monitor
    from zato.common.typing_ import strlist, strstrdict
    from _smb_windows_suite import SMBWindowsSuite

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How many documents each test distributes
    Document_Count = 5

    # The pattern of the documents in the partner drop
    Document_Pattern = 'DOC*.xml'

    # The partner drop has no folders of its own
    Drop_Folder = ''

# ################################################################################################################################
# ################################################################################################################################

def _distribute(smb_suite:'SMBWindowsSuite', version:'str', partner_version:'str', run:'str', monitor:'Monitor') -> 'None':
    """ Writes documents into the outbox of one guest, then waits until each is in the dated archive of that guest,
    in the processed directory of the outbox, and in the drop of the partner, which may be on another guest.
    """
    handle = smb_suite.guest(version)
    partner = smb_suite.guest(partner_version)

    # The archive and the outbox are observed on the guest, and the drop is read by the partner ..
    _ = handle.observe(run, Shares.Archive)
    _ = handle.observe(run, Shares.Documents)
    _ = partner.consume(run, Shares.Partner_Drop, ModuleCtx.Drop_Folder, ModuleCtx.Document_Pattern)

    # .. each document carries the time it was issued at ..
    now = datetime.now(timezone.utc)
    numbers = smb_suite.sequences.next_numbers(ModuleCtx.Document_Count)

    names:'strlist' = []
    archived:'strlist' = []
    processed:'strlist' = []

    for number in numbers:
        name = document_name(number, now)
        names.append(name)

        path = archive_path(name, now)
        archived.append(path)

        path = share_path(f'{Folders.Documents_Outbox}/{Hub.Processed}', name)
        processed.append(path)

    _ = handle.produce(run, Shares.Documents, Folders.Documents_Outbox, names)

    sources = wait_produced(monitor, version, run, ModuleCtx.Document_Count)

    expected:'strstrdict' = {}

    for name, digest in sources.items():
        key = file_key(Shares.Partner_Drop, ModuleCtx.Drop_Folder, name)
        expected[key] = digest

    # .. each one is archived, moved out of the outbox, and handed to the partner, exactly once.
    wait_appeared(monitor, version, run, archived, 'documents archived')
    wait_appeared(monitor, version, run, processed, 'documents moved to processed')
    wait_consumed(monitor, partner_version, run, expected, 'documents in the partner drop')

    monitor.settle()

    assert_appeared_once(monitor, version, run, archived, 'archive')
    assert_appeared_once(monitor, version, run, processed, 'processed documents')
    assert_consumed_once(monitor, partner_version, run, expected, 'partner drop')
    assert_no_leftovers(monitor, version, run, 'documents')

# ################################################################################################################################
# ################################################################################################################################

def test_archive_and_partner_drop(smb_suite:'SMBWindowsSuite', version:'str', run:'str', monitor:'Monitor') -> 'None':
    """ Documents are archived by date and handed to the partner drop on the same guest.
    """
    _distribute(smb_suite, version, version, run, monitor)

# ################################################################################################################################

@pytest.mark.partner_guest
def test_partner_on_other_guest(smb_suite:'SMBWindowsSuite', version:'str', run:'str', monitor:'Monitor') -> 'None':
    """ Documents are archived on one guest and handed to the partner drop on the guest of its partner version.
    """
    partner_version = Partners[version]
    smb_suite.import_guest(version, partner_version=partner_version)

    try:
        _distribute(smb_suite, version, partner_version, run, monitor)
    finally:
        smb_suite.import_guest(version)

# ################################################################################################################################
# ################################################################################################################################
