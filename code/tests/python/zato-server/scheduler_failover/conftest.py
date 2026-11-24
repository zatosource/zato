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

sys.path.insert(0, os.path.dirname(__file__))

# Zato
from pair import build_pair, remove_pair
from zato.common.test.pubsub_database import get_suite_modes, PubSubDatabase, PubSubDBMode, start_pubsub_database, \
    stop_pubsub_database

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

# The modes of the shared database that the suite runs in. The outage of the database, which breaks the connections
# of a server, runs over TLS as well, through a fixture of its own.
_default_modes = [PubSubDBMode.PostgreSQL]

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(params=get_suite_modes(_default_modes))
def database(request:'any_') -> 'any_':
    """ The shared database of the servers, one for each mode and test, which holds the configuration
    that quickstart creates for the servers of the test.
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
    out = build_pair(database, False)

    try:
        yield out
    finally:
        remove_pair(out)

# ################################################################################################################################

@pytest.fixture
def tls_database() -> 'any_':
    """ The shared database of the servers over TLS, one for each test.
    """
    out = start_pubsub_database('scheduler', PubSubDBMode.PostgreSQL_TLS)

    try:
        yield out
    finally:
        stop_pubsub_database(out)

# ################################################################################################################################

@pytest.fixture
def tls_pair(tls_database:'PubSubDatabase') -> 'any_':
    """ Server A runs as the active server and server B waits as a stopped container, both connected over TLS.
    """
    out = build_pair(tls_database, False)

    try:
        yield out
    finally:
        remove_pair(out)

# ################################################################################################################################

@pytest.fixture
def workload_pair(database:'PubSubDatabase') -> 'any_':
    """ The same servers with the objects of the pub/sub workload in addition to the jobs.
    """
    out = build_pair(database, True)

    try:
        yield out
    finally:
        remove_pair(out)

# ################################################################################################################################
# ################################################################################################################################
