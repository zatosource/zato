# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys

# pytest
import pytest

# The helpers that the tests of this directory share
sys.path.insert(0, os.path.dirname(__file__))

# Zato
from server_common import new_socket_dir, remove_socket_dir, terminate_started_servers # noqa: E402

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from server_common import SocketDir
    from zato.common.typing_ import generator_

    SocketDir = SocketDir

    nonegenerator      = generator_[None, None, None]
    socketdirgenerator = generator_[SocketDir, None, None]

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(autouse=True)
def terminate_servers() -> 'nonegenerator':
    """ Kills the server processes of a test after it completes, so a failed test leaves no process behind.
    """
    yield
    terminate_started_servers()

# ################################################################################################################################

@pytest.fixture
def socket_dir() -> 'socketdirgenerator':
    """ A directory of its own for the socket file of a test, removed after the test.
    """
    out = new_socket_dir()
    yield out
    remove_socket_dir(out)

# ################################################################################################################################
# ################################################################################################################################
