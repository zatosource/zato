# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys
import tempfile
from threading import Thread
from uuid import uuid4

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'zato-common', 'lib')))

# pytest
import pytest

# Zato
from live_environment.parts import Parts, skip_or_fail, tear_down
from live_environment.quickstart import ZatoEnvironment
from live_environment.scheduler import find_binary, SchedulerProcess
from live_windows.containers import stop_guests
from live_windows.session import missing_guest_requirements, open_guests
from live_windows.settings import Suite, Versions

# Local
from _smb_windows_suite import ModuleCtx, SMBWindowsSuite

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from live_windows.progress import Monitor
    from live_windows.session import handledict
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

def _requirements() -> 'strlist':
    out = missing_guest_requirements(_versions)

    try:
        _ = find_binary()
    except Exception as e:
        out.append(str(e))

    return out

# ################################################################################################################################
# ################################################################################################################################

class _GuestStart:
    """ Boots the guests in a thread of its own, so that they come up while the server does.
    """
    def __init__(self) -> 'None':
        self.handles:'handledict' = {}
        self.started_versions:'strlist' = []
        self.error:'Exception | None' = None
        self.thread = Thread(target=self._run, daemon=True, name='smb-windows-guests')

    def _run(self) -> 'None':
        try:
            self.handles, self.started_versions = open_guests(_versions)
        except Exception as e:
            self.error = e

    def start(self) -> 'None':
        self.thread.start()

    def wait(self) -> 'None':
        self.thread.join()

        if self.error is not None:
            raise self.error

    def stop(self) -> 'None':
        """ Closes the connections to the guests, and removes the guests this session booted.
        Guests that were already running are left running for the sessions that follow.
        """
        self.thread.join()

        for handle in self.handles.values():
            handle.close()

        if self.started_versions:
            stop_guests(self.started_versions)

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def smb_suite() -> 'iterator_':
    """ The guests, one Zato server with a private scheduler, the services and the definitions of each guest,
    for the whole session.
    """
    skip_or_fail(_requirements(), Suite.Required_Variable)

    parts = Parts()

    try:
        # The guests boot while the server comes up ..
        guest_start = _GuestStart()
        parts.add('guests', guest_start.stop)
        guest_start.start()

        # .. the server runs against a scheduler of its own ..
        scheduler = SchedulerProcess()

        directory = tempfile.mkdtemp(prefix=ModuleCtx.Directory_Prefix)
        zato = ZatoEnvironment(directory, password_prefix=ModuleCtx.Password_Prefix)
        parts.add('zato environment', zato.stop)

        zato.create()
        zato.start(scheduler.server_environment())

        # .. which starts once the server is up, because the server sends it its jobs ..
        scheduler.start()
        parts.add('scheduler', scheduler.cleanup)

        # .. the services the schedules invoke ..
        source = ModuleCtx.Services_File.read_text()
        zato.deploy(ModuleCtx.Services_File.name, source)

        # .. and the connections to each guest, once the guests run.
        guest_start.wait()

        suite = SMBWindowsSuite(zato, scheduler, guest_start.handles, guest_start.started_versions)
        suite.import_all()

        yield suite

    finally:
        tear_down(parts)

# ################################################################################################################################
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
def monitor(smb_suite:'SMBWindowsSuite', run:'str', request:'any_') -> 'iterator_':
    """ Watches the guests and the server while a test runs, and stops the agent tasks of the test once it ends.
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
