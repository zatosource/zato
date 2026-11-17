# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# smbprotocol
from smbprotocol.exceptions import SMBOSError, SMBResponseException

# Zato
from live_windows.layout import Hub, Shares
from live_windows.settings import Control

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from live_windows.progress import Monitor
    from _smb_windows_suite import SMBWindowsSuite

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The Windows events of a refused access to a share, which the SMB server logs
    Access_Denied_Events = 'SMBServer',

# ################################################################################################################################
# ################################################################################################################################

def test_agent_responds(smb_suite:'SMBWindowsSuite', version:'str', run:'str', monitor:'Monitor') -> 'None':
    """ The agent of the guest answers a command through the control share.
    """
    handle = smb_suite.guest(version)
    handle.sender.send('ping', run)

    def _has_pong() -> 'bool':
        out = monitor.has_event(version, 'pong', run)
        return out

    monitor.wait_until(_has_pong, f'win{version} answered the ping')

# ################################################################################################################################

def test_exchange_account_reaches_every_share(smb_suite:'SMBWindowsSuite', version:'str', monitor:'Monitor') -> 'None':
    """ The account that Zato uses logs on and lists each data share, the encrypted one included.
    """
    handle = smb_suite.guest(version)
    client = handle.info.exchange_client()

    try:
        for share in Shares.All:
            names = client.listdir(share)
            print(f'{handle.prefix} {share} -> {names}', flush=True)
            monitor.raise_if_failed()

        exchange_names = client.listdir(Shares.Exchange)
        assert Hub.Environment in exchange_names, f'Expected {Hub.Environment} in the exchange share, got {exchange_names}'

    finally:
        client.close()

# ################################################################################################################################

def test_round_trip(smb_suite:'SMBWindowsSuite', version:'str', run:'str', monitor:'Monitor') -> 'None':
    """ A file that the account of Zato writes into a data share reads back the same, the encrypted share included.
    """
    handle = smb_suite.guest(version)
    client = handle.info.exchange_client()

    name = f'round-trip-{run}.txt'
    text = f'{handle.prefix} {run}'

    try:
        for share in Shares.Exchange, Shares.Landing:
            client.write_text(share, name, text)
            read_back = client.read_text(share, name)
            assert read_back == text, f'{share}/{name} read back as `{read_back}` instead of `{text}`'
            monitor.raise_if_failed()

    finally:
        client.close()

# ################################################################################################################################

def test_control_share_refused(smb_suite:'SMBWindowsSuite', version:'str', monitor:'Monitor') -> 'None':
    """ The account of Zato has no access to the control share of the harness.
    """
    monitor.expect_windows_events(*ModuleCtx.Access_Denied_Events)

    handle = smb_suite.guest(version)
    client = handle.info.exchange_client()

    try:
        # The refusal is raised either by the tree connect or by the open of the directory
        with pytest.raises((SMBOSError, SMBResponseException)):
            _ = client.listdir(Control.Share)

        monitor.raise_if_failed()

    finally:
        client.close()

# ################################################################################################################################
# ################################################################################################################################
