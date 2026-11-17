# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys
from pathlib import Path
from time import monotonic, sleep
from uuid import uuid4

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib'))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'zato-common', 'lib')))

# pytest
import pytest

# Zato
from live_environment.parts import Parts, skip_or_fail, tear_down
from live_environment.scheduler import find_binary, SchedulerProcess
from live_windows.session import missing_guest_requirements, open_guests
from live_windows.settings import Suite, Versions

# Playwright helpers
from client import ZatoClient
from rest_channel import deploy_service_file

# Local
from _smb_windows_dashboard import DashboardSuite

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, iterator_, strlist

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The module of services that the schedules and the job invoke, shared with the backend suite
    Services_File = Path(__file__).parent.parent.parent.parent / 'zato-server' / 'smb_windows_live' / 'services' / \
        'file_exchange.py'

    # A service of that module, whose presence means that the module is deployed
    Probe_Service = 'file-exchange.route'

    # How long the module may take to deploy, and how often its presence is checked, in seconds
    Deploy_Timeout = 60
    Deploy_Poll_Interval = 0.5

# ################################################################################################################################
# ################################################################################################################################

# The server of the Dashboard environment copies the environment of this process when it starts,
# which is how it learns about the scheduler of this suite, and why this happens at import time.
_scheduler = SchedulerProcess()
os.environ.update(_scheduler.server_environment())

# The guests every test that takes a version runs against
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

def _wait_for_services(zato_dashboard:'anydict') -> 'None':
    """ Waits until the server reports the hot-deployed module of services as deployed.
    """
    client = ZatoClient(zato_dashboard['host'], zato_dashboard['server_port'], zato_dashboard['password'])
    request = {'name': ModuleCtx.Probe_Service}
    deadline = monotonic() + ModuleCtx.Deploy_Timeout

    while True:

        # The lookup fails until the module is deployed ..
        try:
            _ = client.invoke('zato.service.get-by-name', request)
        except Exception as e:
            if monotonic() > deadline:
                raise Exception(f'Service {ModuleCtx.Probe_Service} not deployed within {ModuleCtx.Deploy_Timeout}s') from e
            sleep(ModuleCtx.Deploy_Poll_Interval)

        # .. and succeeds once it is.
        else:
            return

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def smb_windows(zato_dashboard:'anydict') -> 'iterator_':
    """ The guests, the scheduler of this suite, the services and the definitions of each guest, for the whole session.
    """
    skip_or_fail(_requirements(), Suite.Required_Variable)

    parts = Parts()

    try:
        # The scheduler starts now that the server it belongs to runs ..
        _scheduler.start()
        parts.add('scheduler', _scheduler.cleanup)

        # .. the services are deployed while the guests boot ..
        source = ModuleCtx.Services_File.read_text()
        _ = deploy_service_file(zato_dashboard['server_dir'], ModuleCtx.Services_File.name, source)

        handles, started_versions = open_guests(_versions)

        suite = DashboardSuite(zato_dashboard, handles, started_versions)
        parts.add('guests', suite.stop)

        _wait_for_services(zato_dashboard)

        # .. and the connections to each guest are imported once both are in place.
        for version in handles:
            suite.import_guest(version)

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
def monitor(smb_windows:'DashboardSuite', run:'str', request:'any_') -> 'iterator_':
    """ Watches the guests and the server while a test runs, and stops the agent tasks of the test once it ends.
    """
    out = smb_windows.new_monitor(request.node.name)
    out.start()

    try:
        yield out

    finally:
        for handle in smb_windows.handles.values():
            handle.stop_run(run)

        out.stop()

# ################################################################################################################################
# ################################################################################################################################
