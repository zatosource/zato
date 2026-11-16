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

_current_dir = os.path.dirname(os.path.abspath(__file__))
_server_tests_dir = os.path.dirname(_current_dir)

_ha_sqlite_dir          = os.path.join(_server_tests_dir, 'ha_sqlite')
_ha_postgresql_dir      = os.path.join(_server_tests_dir, 'ha_postgresql')
_scheduler_failover_dir = os.path.join(_server_tests_dir, 'scheduler_failover')
_pubsub_failover_dir    = os.path.join(_server_tests_dir, 'pubsub_failover')
_container_lib_dir      = os.path.join(os.path.dirname(_server_tests_dir), 'zato-common', 'lib')

sys.path.insert(0, _container_lib_dir)
sys.path.insert(0, _pubsub_failover_dir)
sys.path.insert(0, _scheduler_failover_dir)
sys.path.insert(0, _ha_postgresql_dir)
sys.path.insert(0, _ha_sqlite_dir)
sys.path.insert(0, _server_tests_dir)

# Zato
from ha_env import remove_session
from pubsub_exactly_once_takeover.ha_pair import create_session, get_control_dir
from pubsub_exactly_once_takeover.server_pair import create_server_pair, remove_server_pair
from zato.common.crypto.api import CryptoManager
from zato.common.test.conftest_base_pubsub import render_template
from zato.common.test.exactly_once.config import TestConfig
from zato.common.test.exactly_once.control import Env_Dir

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strstrdict

# ################################################################################################################################
# ################################################################################################################################

_suite_dir = os.path.join(_server_tests_dir, 'pubsub_exactly_once')

_template_path   = os.path.join(_suite_dir, '_enmasse_template.yaml')
_services_source = os.path.join(_suite_dir, '_services.py')

_publisher_username = 'test.exactly-once.publisher'

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def relay_yaml() -> 'str':
    """ The definitions of the relay, rendered with the credentials of this session, which the publications
    of the tests use as well.
    """
    placeholders:'strstrdict' = {
        'publisher_password':    'test.publisher.' + CryptoManager.generate_hex_string(),
        'reader_password':       'test.reader.'    + CryptoManager.generate_hex_string(),
        'orders_password':       'test.orders.'    + CryptoManager.generate_hex_string(),
        'verifier_password':     'test.verifier.'  + CryptoManager.generate_hex_string(),
        'relay_delivery_active': 'true',
    }

    TestConfig.template_path = _template_path
    TestConfig.placeholders  = placeholders

    TestConfig.publisher_username = _publisher_username
    TestConfig.publisher_password = placeholders['publisher_password']

    out = render_template(_template_path, placeholders)
    return out

# ################################################################################################################################

@pytest.fixture(scope='session')
def ha_session(relay_yaml:'str') -> 'any_':
    """ The network, the referee, the receivers and the quickstart environments of both nodes, with the relay,
    which every test of the HA pair copies.
    """
    session = create_session(relay_yaml, _services_source)

    try:
        yield session
    finally:
        remove_session(session)

# ################################################################################################################################

@pytest.fixture
def relay_ha_session(ha_session:'any_') -> 'any_':
    """ The session of the HA pair, with the test process reading and writing the control files of its relay.
    """
    os.environ[Env_Dir] = get_control_dir(ha_session)
    return ha_session

# ################################################################################################################################

@pytest.fixture
def server_pair(relay_yaml:'str') -> 'any_':
    """ An active server and a standby container on a shared PostgreSQL database, with the relay on both.
    """
    pair = create_server_pair(relay_yaml, _services_source)
    os.environ[Env_Dir] = pair.control_dir

    try:
        yield pair
    finally:
        remove_server_pair(pair)

# ################################################################################################################################
# ################################################################################################################################
