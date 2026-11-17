# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timedelta, timezone

# Zato
from live_windows.layout import Folders, Shares

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from live_windows.progress import Monitor
    from zato.common.typing_ import strlist
    from _smb_windows_suite import SMBWindowsSuite

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How many extracts the job is to write before it is deactivated
    Extract_Count = 2

    # The pattern of the extracts in the landing zone
    Extract_Pattern = 'extract-*.csv'

    # The format of the date in the name of each extract
    Extract_Date_Format = '%Y%m%d'

# ################################################################################################################################
# ################################################################################################################################

def test_daily_extract(smb_suite:'SMBWindowsSuite', version:'str', run:'str', monitor:'Monitor') -> 'None':
    """ Once its job is active, the server writes the extracts of the previous day into the encrypted landing zone.
    """
    handle = smb_suite.guest(version)

    _ = handle.observe(run, Shares.Landing)
    _ = handle.consume(run, Shares.Landing, Folders.Landing_Daily, ModuleCtx.Extract_Pattern)

    smb_suite.import_guest(version, is_landing_active=True)

    try:
        def _has_extracts() -> 'bool':
            names = monitor.names(version, 'consumed', run)

            out = len(names) >= ModuleCtx.Extract_Count
            return out

        monitor.wait_until(_has_extracts, f'win{version} received {ModuleCtx.Extract_Count} extracts')

    finally:
        smb_suite.import_guest(version)

    # Each extract is of the previous day, and each one arrived exactly once
    now = datetime.now(timezone.utc)
    previous_day = now - timedelta(days=1)
    extract_date = previous_day.strftime(ModuleCtx.Extract_Date_Format)
    expected_prefix = f'extract-{extract_date}-'

    names = monitor.names(version, 'consumed', run)
    seen:'strlist' = []

    for name in names:
        assert name.startswith(expected_prefix), f'Expected an extract of {extract_date}, got {name}'
        assert name not in seen, f'Extract {name} arrived more than once'
        seen.append(name)

# ################################################################################################################################
# ################################################################################################################################
