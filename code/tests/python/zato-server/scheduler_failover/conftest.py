# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import shutil
import sys
import tempfile

# pytest
import pytest

sys.path.insert(0, os.path.dirname(__file__))

# Zato
from pair import build_pair, remove_pair
from zato.common.test.pubsub_database import get_runtime_dir, get_suite_modes, PubSubDatabase, PubSubDBMode, \
    start_pubsub_database, stop_pubsub_database

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

# The modes of the shared database that the suite runs in.
_default_modes = [PubSubDBMode.PostgreSQL, PubSubDBMode.PostgreSQL_TLS]

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='module', params=get_suite_modes(_default_modes))
def database(request:'any_') -> 'any_':
    """ The shared database of the servers, one for each mode and test module.
    """
    out = start_pubsub_database('scheduler', request.param)

    try:
        yield out
    finally:
        stop_pubsub_database(out)

# ################################################################################################################################

@pytest.fixture
def pair(database:'PubSubDatabase') -> 'any_':
    """ Server A runs as the active server and server B waits as a stopped container.
    """
    out = build_pair(database, 2, False)

    try:
        yield out
    finally:
        remove_pair(out)

# ################################################################################################################################

@pytest.fixture
def workload_pair(database:'PubSubDatabase') -> 'any_':
    """ The same servers with the objects of the pub/sub workload in addition to the jobs.
    """
    out = build_pair(database, 2, True)

    try:
        yield out
    finally:
        remove_pair(out)

# ################################################################################################################################

@pytest.fixture
def sqlite_server() -> 'any_':
    """ A single server whose shared objects are in the SQLite file of pub/sub.
    """
    sqlite_dir = tempfile.mkdtemp(prefix='zato_scheduler_failover_sqlite_', dir=get_runtime_dir())

    database = PubSubDatabase(mode=PubSubDBMode.SQLite)
    database.env = {'Zato_PubSub_DB_Path': os.path.join(sqlite_dir, 'pubsub.db')}

    out = build_pair(database, 1, False)

    try:
        yield out
    finally:
        remove_pair(out)
        shutil.rmtree(sqlite_dir, ignore_errors=True)

# ################################################################################################################################
# ################################################################################################################################
