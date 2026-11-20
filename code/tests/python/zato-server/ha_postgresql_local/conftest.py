# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The takeover of the Zato database and the start of a server under the generation of an active-standby node,
# on one local cluster of PostgreSQL 19 per session, a primary with a synchronous standby on reserved ports.

# stdlib
import os
import sys

# pytest
import pytest

_here = os.path.dirname(os.path.abspath(__file__))
_server_tests_dir = os.path.dirname(_here)

# The modules of the suite and the clients of the pub/sub performance suite, which load the server
sys.path.insert(0, _server_tests_dir)
sys.path.insert(0, _here)

# Zato
from zato.common.test.pubsub_database import PubSubDBMode, pubsub_db_env, start_pubsub_database, stop_pubsub_database
from zato.common.test.resume import pytest_runtest_protocol as pytest_runtest_protocol
from zato.common.test.resume import pytest_runtest_teardown as pytest_runtest_teardown
from zato.common.test.takeover import take_over_as_another_server

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The name of the database of the session, which names its directories
    Database_Name = 'ha-local'

    # The pool size of the engine of the server that creates the schema, distinct from those of the tests
    Pool_Size_Schema = 1

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def pubsub_database() -> 'any_':
    """ The Zato database of the session on the local PostgreSQL 19, removed with its cluster at the end of the session.
    """
    database = start_pubsub_database(ModuleCtx.Database_Name, PubSubDBMode.PostgreSQL_Local)

    try:

        # The first server creates the schema and the row of the active server, which every test reads first
        backend = take_over_as_another_server(database.env, ModuleCtx.Pool_Size_Schema)

        with pubsub_db_env(database.env):
            guard = backend.generation_guard
            assert guard is not None
            guard.uninstall(backend.engine)

        yield database
    finally:
        stop_pubsub_database(database)

# ################################################################################################################################
# ################################################################################################################################
