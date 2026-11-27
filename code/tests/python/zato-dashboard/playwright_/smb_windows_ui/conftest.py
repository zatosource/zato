# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys
from pathlib import Path
from threading import Thread
from time import monotonic, sleep

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib'))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'zato-server', 'smb_windows_live')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'zato-common', 'lib')))

# pytest
import pytest

# Zato
from live_environment.parts import Parts, skip_or_fail, tear_down
from live_environment.redis_process import RedisProcess
from live_environment.scheduler import find_binary, SchedulerProcess
from live_windows.containers import stop_guests
from live_windows.guest_versions import needed_versions, version_items
from live_windows.session import missing_guest_requirements, open_guests
from live_windows.settings import Step, Suite, Versions
from live_windows.shard_selection import current_shard, is_sharded, shard_items
from zato.common.crypto.api import CryptoManager

# Playwright helpers
from client import ZatoClient
from login import login as login_to_dashboard
from rest_channel import deploy_service_file

# Local
from _dashboard_writer import DashboardWriter
from _smb_windows_ui_suite import UISuite

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pytest import Config, Item
    from live_windows.progress import Monitor
    from live_windows.session import handledict
    from zato.common.typing_ import any_, anydict, anylist, iterator_, strlist

    itemlist = list[Item]

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

    # The label of the logs that this suite checks after each test, and where they are, relative to the Dashboard
    Dashboard_Log_Label = 'dashboard'
    Dashboard_Log_Dir   = 'logs'

    # The prefix of each progress line
    Progress_Prefix = '[SMB UI]'

    # How many random bits make the name of the run of each test unique
    Run_Suffix_Bits = 32

# ################################################################################################################################
# ################################################################################################################################

# The server of the Playwright environment copies the environment of this process when it starts,
# which is how it learns about the scheduler of this suite and its Redis, and why this happens at import time.
# The Redis is one of this suite's own, because other suites delete keys in the shared one while they run.
_scheduler = SchedulerProcess()
_scheduler_redis = RedisProcess()
os.environ.update(_scheduler.server_environment())
os.environ.update(_scheduler_redis.server_environment())

# The guests every test that takes a version runs against
_versions = list(Versions.All)

# The versions of the guests that the tests of the session run against
_versions_key = pytest.StashKey['strlist']()

_version_ids:'strlist' = []
for _version in _versions:
    _version_ids.append(f'win{_version}')

# ################################################################################################################################
# ################################################################################################################################

@pytest.hookimpl(trylast=True)
def pytest_collection_modifyitems(config:'Config', items:'itemlist') -> 'None':
    """ Keeps the tests of the shard of this process, if the tests are divided into shards, or those of the version
    of the step that this session runs, if a step is given, and records the versions of the guests that the remaining
    tests run against. It runs after the selection by keywords and markers, so that a session resumes only the guests
    of the tests it runs.
    """
    if is_sharded():
        index, count = current_shard()
        selected = shard_items(items, index, count)

    elif Step.Variable in os.environ:
        step_version = os.environ[Step.Variable]
        selected = version_items(items, step_version)

    else:
        selected = items

    deselected:'itemlist' = []

    for item in items:
        if item not in selected:
            deselected.append(item)

    config.hook.pytest_deselected(items=deselected)
    items[:] = selected

    config.stash[_versions_key] = needed_versions(items)

# ################################################################################################################################
# ################################################################################################################################

def _requirements(versions:'strlist') -> 'strlist':
    out = missing_guest_requirements(versions)

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

class _GuestStart:
    """ Boots the guests in a thread of its own, so that they come up while the services deploy.
    """
    def __init__(self, versions:'strlist') -> 'None':
        self.versions = versions
        self.handles:'handledict' = {}
        self.started_versions:'strlist' = []
        self.error:'Exception | None' = None
        self.thread = Thread(target=self._run, daemon=True, name='smb-windows-ui-guests')

    def _run(self) -> 'None':
        try:
            self.handles, self.started_versions = open_guests(self.versions)
        except Exception as e:
            self.error = e

    def start(self) -> 'None':
        self.thread.start()

    def wait(self) -> 'None':
        self.thread.join()

        if self.error is not None:
            raise self.error

    def stop(self) -> 'None':
        """ Closes the connections to the guests and removes every guest, so that none is left running once the session ends.
        """
        self.thread.join()

        for handle in self.handles.values():
            handle.close()

        guest_versions = list(self.handles)
        stop_guests(guest_versions)

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session', autouse=True)
def scheduler_redis() -> 'iterator_':
    """ The Redis of the scheduler of this suite, which runs before the server that connects to it starts,
    because an autouse fixture is set up ahead of the fixtures that a test requests.
    """
    _scheduler_redis.start()

    try:
        yield _scheduler_redis
    finally:
        # The streams of the scheduler are removed only once the server that reads them has stopped
        _scheduler.cleanup()
        _scheduler_redis.cleanup()

# ################################################################################################################################

@pytest.fixture(scope='session')
def smb_suite(zato_dashboard:'anydict', playwright_browser:'any_', request:'any_') -> 'iterator_':
    """ The guests, the scheduler of this suite, the services, and the definitions of each guest created through
    the Dashboard, for the whole session.
    """
    versions = request.config.stash[_versions_key]

    skip_or_fail(_requirements(versions), Suite.Required_Variable)

    parts = Parts()

    try:
        # The guests boot while everything else is prepared ..
        guest_start = _GuestStart(versions)
        parts.add('guests', guest_start.stop)
        guest_start.start()

        # .. the scheduler starts now that the server it belongs to runs ..
        _scheduler.start()
        parts.add('scheduler', _scheduler.stop)

        # .. the services are deployed ..
        source = ModuleCtx.Services_File.read_text()
        _ = deploy_service_file(zato_dashboard['server_dir'], ModuleCtx.Services_File.name, source)

        # .. the definitions are written through a browser context of their own, because each test
        # .. clears the cookies of the context that the tests share ..
        context = playwright_browser.new_context()
        parts.add('browser context', context.close)

        page = context.new_page()
        dashboard_url = zato_dashboard['dashboard_url']
        login_to_dashboard(page, dashboard_url, zato_dashboard['password'])

        writer = DashboardWriter(page, dashboard_url)

        _wait_for_services(zato_dashboard)
        guest_start.wait()

        suite = UISuite(zato_dashboard, writer, guest_start.handles, guest_start.started_versions)

        print(f'{ModuleCtx.Progress_Prefix} Server log in {suite.server_log_path}', flush=True)
        print(f'{ModuleCtx.Progress_Prefix} Dashboard in {zato_dashboard["dashboard_dir"]}', flush=True)

        # .. and the connections, the schedules and the job of each guest are created once all of it is in place.
        suite.import_all()

        yield suite

    finally:
        tear_down(parts)

# ################################################################################################################################

@pytest.fixture
def checked_log_dirs(zato_dashboard:'anydict') -> 'anylist':
    """ The Dashboard logs only, because the monitor of each test checks the server log against what the test expects.
    """
    log_dir = os.path.join(zato_dashboard['dashboard_dir'], ModuleCtx.Dashboard_Log_Dir)

    out = [(ModuleCtx.Dashboard_Log_Label, log_dir)]
    return out

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
    suffix = CryptoManager.generate_hex_string(ModuleCtx.Run_Suffix_Bits)

    out = f'{request.node.originalname}-{suffix}'
    return out

# ################################################################################################################################

@pytest.fixture
def monitor(smb_suite:'UISuite', run:'str', request:'any_') -> 'iterator_':
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
