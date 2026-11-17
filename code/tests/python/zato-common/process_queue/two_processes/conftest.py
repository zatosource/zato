# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# gevent - the test process forks the worker and the config process as the arbiter does, which runs under gevent,
# so the patching runs before anything else is imported.
from gevent import monkey
_ = monkey.patch_all()

# stdlib
import atexit
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'lib')))

# pytest
import pytest

# Zato
from perf import silence_logging_teardown
from zato.common.db_env.database_env import DatabaseEnv

# The late log-handler cleanup would otherwise fail under gevent once the hub is gone.
_ = atexit.register(silence_logging_teardown)

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path

    Path = Path

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture
def database_path(tmp_path:'Path', monkeypatch:'pytest.MonkeyPatch') -> 'str':
    """ Points the Zato database of the test process, and of each process that it forks, at a SQLite file of the test.
    """
    out = os.path.join(str(tmp_path), DatabaseEnv.File_Name)

    monkeypatch.setenv(DatabaseEnv.Env_Type, DatabaseEnv.Type_SQLite)
    monkeypatch.setenv(DatabaseEnv.Env_Path, out)

    return out

# ################################################################################################################################
# ################################################################################################################################
