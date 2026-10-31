# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# gevent
from gevent import monkey
_ = monkey.patch_all()

# stdlib
import os
import shutil
import sys
import tempfile

_here = os.path.dirname(__file__)
_perf_dir = os.path.abspath(os.path.join(_here, '..', 'pubsub_backend_perf'))
_lib_dir = os.path.abspath(os.path.join(_here, '..', 'lib'))

sys.path.insert(0, _lib_dir)
sys.path.insert(0, _perf_dir)
sys.path.insert(0, _here)

# pytest
import pytest

# Zato
from zato.common.pubsub.sql.config import get_pubsub_engine, ModuleCtx
from zato.common.test.pubsub_database import get_db_mode, get_runtime_dir, is_postgresql_mode, pubsub_db_env, \
    start_pubsub_database, stop_pubsub_database

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from zato.common.typing_ import strstrdict

# ################################################################################################################################
# ################################################################################################################################

# How many fully delivered messages each topic keeps during the stability runs, which bounds the tables.
_delivered_max_messages = '10000'

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='module')
def stability_env() -> 'Iterator[strstrdict]':
    """ The pub/sub database of one stability suite in the mode that Zato_Test_PubSub_DB_Mode selects,
    a SQLite file or a PostgreSQL container, with the generation file and the retention of the run.
    """
    mode = get_db_mode()
    work_dir = tempfile.mkdtemp(prefix='zato-pubsub-stability-', dir=get_runtime_dir())

    env:'strstrdict' = {
        ModuleCtx.Env_Generation_File: os.path.join(work_dir, 'pubsub-generation'),
        ModuleCtx.Env_Delivered_Max_Messages: _delivered_max_messages,
    }

    database = None

    if is_postgresql_mode(mode):
        database = start_pubsub_database('stability', mode)
        env.update(database.env)
    else:
        env[ModuleCtx.Env_Path] = os.path.join(work_dir, 'pubsub.db')

    try:
        with pubsub_db_env(env):
            yield env
            get_pubsub_engine().dispose()
    finally:
        if database:
            stop_pubsub_database(database)
        shutil.rmtree(work_dir, ignore_errors=True)

# ################################################################################################################################
# ################################################################################################################################
