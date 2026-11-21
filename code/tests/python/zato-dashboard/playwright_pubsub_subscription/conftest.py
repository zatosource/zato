# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import importlib.util
import os
import sys
import tempfile
from pathlib import Path

# pytest
import pytest

# Zato
from zato.common.db_env.database_env import DatabaseEnv
from zato.common.test.pubsub_in_process_support import FilesystemFault, ModuleCtx as SupportCtx, SQLiteWriteLock

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

_playwright_dir = Path(__file__).resolve().parent.parent / 'playwright_'
_playwright_conftest_path = _playwright_dir / 'conftest.py'

sys.path.insert(0, str(_playwright_dir / 'lib'))
sys.path.insert(0, str(_playwright_dir))

_spec = importlib.util.spec_from_file_location('playwright_parent_conftest', _playwright_conftest_path)
_parent_conftest = importlib.util.module_from_spec(_spec)
sys.modules['playwright_parent_conftest'] = _parent_conftest
_spec.loader.exec_module(_parent_conftest)

zato_dashboard = _parent_conftest.zato_dashboard
logged_in_page = _parent_conftest.logged_in_page
browser_context = getattr(_parent_conftest, 'browser_context', None)
page = getattr(_parent_conftest, 'page', None)

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture
def sqlite_write_lock(zato_dashboard:'any_') -> 'any_':
    """ Returns a write lock of the SQLite Zato database of the Dashboard server, released on teardown.
    """
    db_path = zato_dashboard['pubsub_db_path']

    if not db_path:
        db_path = os.path.join(zato_dashboard['server_dir'], DatabaseEnv.File_Name)

    lock = SQLiteWriteLock(db_path)

    try:
        yield lock
    finally:
        if lock._process:
            lock.release()

# ################################################################################################################################

@pytest.fixture
def filesystem_fault(zato_dashboard:'any_') -> 'any_':
    """ Controls fsfault.so against the configuration database of the Dashboard server.
    """
    if SupportCtx.Env_FSFault_Control not in os.environ:
        control_file = tempfile.NamedTemporaryFile(prefix='fsfault-control-', delete=False)
        control_file.write(b'prefix=\n')
        control_file.close()
        os.environ[SupportCtx.Env_FSFault_Control] = control_file.name

    config_db = os.path.join(zato_dashboard['server_dir'], 'config.db')
    fault = FilesystemFault(config_db)

    try:
        yield fault
    finally:
        fault.clear()

# ################################################################################################################################
# ################################################################################################################################
