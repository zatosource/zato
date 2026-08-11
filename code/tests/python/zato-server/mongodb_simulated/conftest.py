# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys

# The simulator lives in lib/ and the connection helpers are shared with the container-based suite
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'mongodb')))

# pytest
import pytest

# Zato
from containers import MongoDBServer
from mongodb_test_server import find_free_port, start_mongodb_test_server

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator

    servergen = Iterator[MongoDBServer]

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def mongodb_server() -> 'servergen':
    """ The in-process MongoDB simulator, described the same way the container-based suite
    describes its servers so the shared connection helpers work unchanged.
    """
    port = find_free_port()
    server = start_mongodb_test_server(port)

    yield MongoDBServer(
        container_name='',
        host='127.0.0.1',
        port=port,
        username='',
        password='',
    )

    server.shutdown()
    server.server_close()

# ################################################################################################################################
# ################################################################################################################################
