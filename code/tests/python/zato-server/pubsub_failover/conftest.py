# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import shutil
import sys
import tempfile
from contextlib import contextmanager
from dataclasses import dataclass, field

# pytest
import pytest

sys.path.insert(0, os.path.dirname(__file__))

# Zato
from failover import build_server_env, ContainerServer, create_container, get_failover_dir, remove_container, \
    run_container, save_container_logs, wait_until_up
from zato.common.crypto.api import CryptoManager
from zato.common.test.conftest_base_pubsub import find_free_port, patch_server_conf, render_template, \
    run_quickstart_and_enmasse, SessionState
from zato.common.test.pubsub_database import get_db_mode, get_runtime_dir, is_postgresql_mode, PubSubDBMode, \
    start_pubsub_database, stop_pubsub_database
from zato.common.test.receiver import WebhookReceiver

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.pubsub_database import PubSubDatabase
    from zato.common.typing_ import any_, strstrdict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.pubsub_failover.conftest')

_pubsub_push_dir = os.path.join(os.path.dirname(__file__), '..', 'pubsub_push')
_pubsub_push_dir = os.path.abspath(_pubsub_push_dir)
_template_path = os.path.join(_pubsub_push_dir, '_enmasse_template.yaml')

_topic_names = [
    'iam.user.created',
    'iam.user.deleted',
    'iam.role.assigned',
    'iam.password.changed',
    'iam.login.failed',
    'customer.registered',
    'customer.updated',
    'customer.deactivated',
    'order.placed',
    'order.shipped',
]

_zato_bin = os.path.join(os.environ['ZATO_TEST_BASE_DIR'], 'code', 'bin', 'zato')

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class FailoverEnvironment:
    """ The two servers of the pair, the shared database, the receivers of push deliveries and the credentials.
    """
    database: 'PubSubDatabase'
    server_a: 'ContainerServer'
    server_b: 'ContainerServer'
    work_dir: 'str'
    publisher_username: 'str' = 'test.pubsub.publisher'
    publisher_password: 'str' = ''
    puller_username: 'str' = 'test.pubsub.puller'
    puller_password: 'str' = ''
    receivers: 'dict' = field(default_factory=dict)

# ################################################################################################################################
# ################################################################################################################################

def _topic_to_key(topic_name:'str') -> 'str':
    out = topic_name.replace('.', '_')
    return out

# ################################################################################################################################

def _new_server(name:'str', state:'SessionState', rendered_yaml:'str', invoke_password:'str',
    database:'PubSubDatabase') -> 'ContainerServer':
    """ Creates the quickstart environment of one server of the pair from the shared enmasse file.
    """
    server_directory = run_quickstart_and_enmasse(
        state=state,
        logger=logger,
        zato_bin=_zato_bin,
        invoke_password=invoke_password,
        rendered_yaml=rendered_yaml,
        quickstart_prefix=f'zato_pubsub_failover_{name}_',
    )

    out = ContainerServer(
        name=name,
        container_name=f'zato-pubsub-test-failover-{name}',
        server_directory=server_directory,
        port=find_free_port(),
        broker_port=find_free_port(),
    )

    patch_server_conf(server_directory, out.port, False)
    build_server_env(out, database)

    return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='module')
def failover_env() -> 'any_':
    """ Server A runs as the active server, server B is a stopped container that the controller may start.
    """
    mode = get_db_mode()

    if not is_postgresql_mode(mode):
        mode = PubSubDBMode.PostgreSQL

    with _environment(mode) as environment:
        yield environment

# ################################################################################################################################

@pytest.fixture(scope='module')
def crash_env() -> 'any_':
    """ The same pair of servers on the pub/sub database of the mode that Zato_Test_PubSub_DB_Mode selects,
    which is a SQLite file in the runtime directory when the mode is SQLite.
    """
    mode = get_db_mode()

    with _environment(mode) as environment:
        yield environment

# ################################################################################################################################

@contextmanager
def _environment(mode:'str') -> 'any_':
    """ Builds the pair of servers on a pub/sub database of the given mode and removes everything afterwards.
    """
    database = start_pubsub_database('failover', mode)

    # A SQLite file is in the runtime directory, which the containers of the servers mount.
    sqlite_dir = tempfile.mkdtemp(prefix='zato_pubsub_failover_sqlite_', dir=get_runtime_dir())

    if not is_postgresql_mode(mode):
        database.env = {'Zato_PubSub_DB_Path': os.path.join(sqlite_dir, 'pubsub.db')}

    state_a = SessionState('zato.test.pubsub_failover.a', 'server-logs-failover-a.txt')
    state_b = SessionState('zato.test.pubsub_failover.b', 'server-logs-failover-b.txt')

    # The receivers of push deliveries and the credentials are shared by both servers ..
    state_a.test_data_directory = tempfile.mkdtemp(prefix='zato_pubsub_failover_data_')

    placeholders:'strstrdict' = {}
    placeholders['publisher_password'] = 'test.pub.' + CryptoManager.generate_hex_string()
    placeholders['puller_password'] = 'test.pull.' + CryptoManager.generate_hex_string()

    receivers:'dict' = {}

    for topic_name in _topic_names:
        key = _topic_to_key(topic_name)
        port = find_free_port()

        placeholders[f'sub_{key}_password'] = 'test.sub.' + CryptoManager.generate_hex_string()
        placeholders[f'port_{key}'] = str(port)

        output_directory = os.path.join(state_a.test_data_directory, 'receivers', key)
        os.makedirs(output_directory, exist_ok=True)

        receiver = WebhookReceiver(port, output_directory)
        receiver.start()

        state_a.receivers.append(receiver)
        receivers[topic_name] = receiver

    rendered_yaml = render_template(_template_path, placeholders)
    invoke_password = 'test.invoke.' + CryptoManager.generate_hex_string()

    # .. each server has a quickstart environment of its own, created from the same enmasse file ..
    server_a = _new_server('a', state_a, rendered_yaml, invoke_password, database)
    server_b = _new_server('b', state_b, rendered_yaml, invoke_password, database)

    environment = FailoverEnvironment(
        database=database,
        server_a=server_a,
        server_b=server_b,
        work_dir=get_failover_dir(),
        publisher_password=placeholders['publisher_password'],
        puller_password=placeholders['puller_password'],
        receivers=receivers,
    )

    # .. server A becomes active and server B waits as a stopped container.
    run_container(server_a)
    _ = wait_until_up(server_a)
    create_container(server_b)

    try:
        yield environment
    finally:
        for server in (server_a, server_b):
            save_container_logs(server, environment.work_dir)
            remove_container(server)

        state_a.cleanup()
        state_b.cleanup()
        stop_pubsub_database(database)
        shutil.rmtree(sqlite_dir, ignore_errors=True)

# ################################################################################################################################
# ################################################################################################################################
