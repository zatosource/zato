# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from live_windows.layout import Hub, Shares
from live_windows.session import Mode

# Local
from _smb_windows_flows import hub_outbox, start_hub, verify_hub, wait_produced

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from live_windows.progress import Monitor
    from _smb_windows_suite import SMBWindowsSuite

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How many files each write mode produces
    File_Count = 3

    # A slow writer appends its file in this many chunks over this many milliseconds, each chunk sooner
    # than the stability delay of the schedules, so that the file is never stable before it is complete
    Slow_Chunk_Count = 6
    Slow_Ms          = 3000
    Slow_File_Size   = 65536

    # A locking writer keeps its file open, with no sharing, for this many milliseconds
    Lock_Ms = 3000

# ################################################################################################################################
# ################################################################################################################################

def test_temp_then_rename(smb_suite:'SMBWindowsSuite', version:'str', run:'str', monitor:'Monitor') -> 'None':
    """ Files written under a temporary name and then renamed are routed under their final names only.
    """
    handle = smb_suite.guest(version)
    start_hub(handle, run, [Hub.Plant])

    names = smb_suite.sequences.next_names(Hub.Plant, ModuleCtx.File_Count)
    outbox = hub_outbox(Hub.Plant)
    _ = handle.produce(run, Shares.Exchange, outbox, names, mode=Mode.Temp_Then_Rename)

    sources = wait_produced(monitor, version, run, ModuleCtx.File_Count)
    verify_hub(monitor, version, run, sources, 'temporary name, then renamed')

# ################################################################################################################################

def test_slow_writer(smb_suite:'SMBWindowsSuite', version:'str', run:'str', monitor:'Monitor') -> 'None':
    """ A file that grows for a few seconds is picked up only once it is complete.
    """
    handle = smb_suite.guest(version)
    start_hub(handle, run, [Hub.Plant])

    names = smb_suite.sequences.next_names(Hub.Plant, 1)
    outbox = hub_outbox(Hub.Plant)

    _ = handle.produce(
        run,
        Shares.Exchange,
        outbox,
        names,
        mode=Mode.Slow,
        size=ModuleCtx.Slow_File_Size,
        chunk_count=ModuleCtx.Slow_Chunk_Count,
        slow_ms=ModuleCtx.Slow_Ms,
    )

    # The digest of a slow file is reported once its last chunk is written, so the content compared is the complete one
    sources = wait_produced(monitor, version, run, 1)
    verify_hub(monitor, version, run, sources, 'slow writer')

# ################################################################################################################################

def test_locked_file(smb_suite:'SMBWindowsSuite', version:'str', run:'str', monitor:'Monitor') -> 'None':
    """ A file that its writer keeps open with no sharing is picked up once the writer releases it.
    """
    handle = smb_suite.guest(version)
    start_hub(handle, run, [Hub.Plant])

    names = smb_suite.sequences.next_names(Hub.Plant, 1)
    outbox = hub_outbox(Hub.Plant)
    _ = handle.produce(run, Shares.Exchange, outbox, names, mode=Mode.Locked, lock_ms=ModuleCtx.Lock_Ms)

    sources = wait_produced(monitor, version, run, 1)

    def _is_released() -> 'bool':
        out = monitor.has_event(version, 'released', run)
        return out

    monitor.wait_until(_is_released, f'win{version} released the locked file')

    # Nothing may have reached the inbox while the file was locked
    consumed = monitor.names(version, 'consumed', run)
    assert not consumed, f'A locked file must not be routed before it is released, got {consumed}'

    verify_hub(monitor, version, run, sources, 'locked file')

# ################################################################################################################################
# ################################################################################################################################
