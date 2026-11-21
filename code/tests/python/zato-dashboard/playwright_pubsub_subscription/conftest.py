# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import importlib.util
import os
import shutil
import sys
import tempfile
from collections.abc import Generator
from pathlib import Path

_here = os.path.dirname(__file__)
_playwright_dir = Path(_here).resolve().parent / 'playwright_'
_playwright_conftest_path = _playwright_dir / 'conftest.py'

sys.path.insert(0, str(_playwright_dir / 'lib'))
sys.path.insert(0, str(_playwright_dir))
sys.path.insert(0, _here)

# pytest
import pytest

# Zato
from zato.common.db_env.database_env import DatabaseEnv
from zato.common.db_env.fence import ModuleCtx as FenceCtx
from zato.common.test.pubsub_database import get_db_mode, pubsub_db_env, start_pubsub_database, stop_pubsub_database
from zato.common.test.pubsub_in_process_support import FilesystemFault, SQLiteWriteLock

# Local
from _support import TableWriteLock, is_postgresql

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.pubsub_database import PubSubDatabase
    from zato.common.typing_ import any_, anydict, strstrdict

    any_ = any_
    anydict = anydict
    PubSubDatabase = PubSubDatabase
    strstrdict = strstrdict

# ################################################################################################################################
# ################################################################################################################################

class SuiteCtx:
    Work_Directory_Prefix = 'zato_playwright_pubsub_subscription_work_'
    Database_Label = 'playwright-pubsub-subscription'
    Generation_File_Name = 'database-generation'
    Config_DB_Name = 'config.db'

# ################################################################################################################################
# ################################################################################################################################

_spec = importlib.util.spec_from_file_location('playwright_parent_conftest', _playwright_conftest_path)

if _spec is None:
    raise Exception(f'Could not load {_playwright_conftest_path}')

if _spec.loader is None:
    raise Exception(f'Could not load {_playwright_conftest_path}')

_parent_conftest = importlib.util.module_from_spec(_spec)
sys.modules['playwright_parent_conftest'] = _parent_conftest
_spec.loader.exec_module(_parent_conftest)

_parent_zato_dashboard = _parent_conftest.zato_dashboard._get_wrapped_function()

playwright_browser = _parent_conftest.playwright_browser
playwright_context = _parent_conftest.playwright_context
logged_in_page = _parent_conftest.logged_in_page

pytest_runtest_makereport = _parent_conftest.pytest_runtest_makereport
pytest_internalerror = _parent_conftest.pytest_internalerror
pytest_sessionfinish = _parent_conftest.pytest_sessionfinish

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def pubsub_database() -> 'Generator[PubSubDatabase | None, None, None]':
    """ The PostgreSQL container of the session on PostgreSQL, and nothing on SQLite.
    """
    if not is_postgresql():
        yield None
        return

    mode = get_db_mode()
    out = start_pubsub_database(SuiteCtx.Database_Label, mode)

    try:
        yield out
    finally:
        stop_pubsub_database(out)

# ################################################################################################################################

@pytest.fixture(scope='session')
def zato_dashboard(pubsub_database:'PubSubDatabase | None') -> 'Generator[anydict, None, None]':
    """ The server and Dashboard of playwright_/conftest.py, with the Zato database of the mode of the session.
    """
    work_dir = tempfile.mkdtemp(prefix=SuiteCtx.Work_Directory_Prefix)
    generation_file = os.path.join(work_dir, SuiteCtx.Generation_File_Name)

    env:'strstrdict' = {
        FenceCtx.Env_Generation_File: generation_file,
    }

    if pubsub_database is None:
        env[DatabaseEnv.Env_Type] = DatabaseEnv.Type_SQLite
    else:
        env.update(pubsub_database.env)

    try:
        with pubsub_db_env(env):
            yield from _parent_zato_dashboard()
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)

# ################################################################################################################################

@pytest.fixture
def write_lock(zato_dashboard:'anydict', pubsub_database:'PubSubDatabase | None') -> 'Generator[any_, None, None]':
    """ A lock that makes the writes of the server to the table of pairs wait, released on teardown.
    It is the write lock of the SQLite file on SQLite and a lock of the table on PostgreSQL.
    """
    if pubsub_database is None:
        lock = SQLiteWriteLock(zato_dashboard['pubsub_db_path'])
    else:
        lock = TableWriteLock(pubsub_database)

    try:
        yield lock
    finally:
        lock.release()

# ################################################################################################################################

@pytest.fixture
def filesystem_fault(zato_dashboard:'anydict') -> 'Generator[FilesystemFault, None, None]':
    """ Controls fsfault.so against config.db of the server, cleared on teardown.
    """
    config_db_path = os.path.join(zato_dashboard['temporary_dir'], SuiteCtx.Config_DB_Name)
    config_db_path = os.path.realpath(config_db_path)

    fault = FilesystemFault(config_db_path)

    try:
        yield fault
    finally:
        fault.clear()

# ################################################################################################################################
# ################################################################################################################################
