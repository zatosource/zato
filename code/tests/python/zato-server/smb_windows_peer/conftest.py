# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys
import tempfile
from uuid import uuid4

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'smb_windows_live')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'zato-common', 'lib')))

# pytest
import pytest

# Zato
from live_environment.parts import skip_or_fail
from live_windows.containers import stop_guests
from live_windows.peer_server import PeerServer
from live_windows.session import missing_guest_requirements, open_guests
from live_windows.settings import Suite, Versions

# Local
from _smb_windows_peer_suite import ModuleCtx, PeerSuite

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from live_windows.progress import Monitor
    from zato.common.typing_ import any_, iterator_, strlist

# ################################################################################################################################
# ################################################################################################################################

# The guests every test that takes a version runs against, one after the other
_versions = list(Versions.All)

_version_ids:'strlist' = []
for _version in _versions:
    _version_ids.append(f'win{_version}')

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def smb_suite() -> 'iterator_':
    """ The guests and the peer in place of a Zato server, with the definitions of each guest, for the whole session.
    """
    skip_or_fail(missing_guest_requirements(_versions), Suite.Required_Variable)

    handles, started_versions = open_guests(_versions)

    descriptor, log_path = tempfile.mkstemp(prefix=ModuleCtx.Log_Prefix, suffix='.log')
    os.close(descriptor)
    print(f'[SMB peer] Log in {log_path}', flush=True)

    peer = PeerServer(ModuleCtx.Services_File, log_path)
    suite = PeerSuite(peer, handles, started_versions)

    try:
        suite.import_all()
        yield suite

    finally:
        suite.close()

        # No guest is left running once the session ends
        guest_versions = list(handles)
        stop_guests(guest_versions)

# ################################################################################################################################

@pytest.fixture(params=_versions, ids=_version_ids)
def version(request:'any_') -> 'str':
    """ The guest a test runs against.
    """
    out = request.param
    return out

# ################################################################################################################################

@pytest.fixture
def run(request:'any_') -> 'str':
    """ The name of the run that every agent task of a test belongs to.
    """
    suffix = uuid4().hex[:8]

    out = f'{request.node.originalname}-{suffix}'
    return out

# ################################################################################################################################

@pytest.fixture
def monitor(smb_suite:'PeerSuite', run:'str', request:'any_') -> 'iterator_':
    """ Watches the guests and the peer while a test runs, and stops the agent tasks of the test once it ends.
    """
    out:'Monitor' = smb_suite.new_monitor(request.node.name)
    out.start()

    try:
        yield out

    finally:

        # The monitor is stopped even if a guest fails to stop the tasks of the test
        try:
            for version, handle in smb_suite.handles.items():
                watch = out.watches[version]
                if not watch.may_stop:
                    handle.stop_run(run)
        finally:
            out.stop()

# ################################################################################################################################
# ################################################################################################################################
