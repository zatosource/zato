# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import atexit
import logging
import os
import shutil
import subprocess
import sys
import time
from tempfile import mkdtemp

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'zato-common', 'lib')))

# pytest
import pytest

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.test.conftest_base_pubsub import find_free_port, render_template, run_quickstart_and_enmasse, \
    SessionState, start_server_process

# local
from _amqp import add_amqp_config, declare_broker_queues
from _backends import get_backend_names, PubSub_Env_Prefix, start_backend
from _dlq_helpers import discard_all_dlqs
from _helpers import Connections, get_client, TestConfig, wait_for_queue_empty
from _receiver import RecordingReceiver
from certificates import generate_certificates
from live_sql.env import database_env

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from certificates import CertificatePaths
    from zato.common.typing_ import any_, strstrdict

    certificatesgen = Iterator[CertificatePaths]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.queue_delivery_rest.conftest')

_template_path = os.path.join(os.path.dirname(__file__), '_enmasse_template.yaml')
_services_source = os.path.join(os.path.dirname(__file__), '_services.py')

# The database users inside the containers must be able to traverse into the certificate directory
_certificate_dir_mode = 0o755

_leftover_kill_wait = 2

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def certificate_paths() -> 'certificatesgen':
    """ Generates the throwaway CA along with server and client certificates once per session.
    """
    directory = mkdtemp(prefix='zato-queue-delivery-rest-certificates-')
    os.chmod(directory, _certificate_dir_mode)

    out = generate_certificates(directory)
    yield out

    shutil.rmtree(directory, ignore_errors=True)

# ################################################################################################################################
# ################################################################################################################################

def _start_receivers(state:'SessionState') -> 'strstrdict':
    """ Starts one endpoint per connection of the template and returns the port placeholders they fill in.
    """
    receivers:'dict[str, RecordingReceiver]' = {}
    placeholders:'strstrdict' = {}

    for key in Connections:
        port = find_free_port()

        receiver = RecordingReceiver(port)
        receiver.start()

        receivers[key] = receiver
        state.receivers.append(receiver)

        placeholders['port_' + key] = str(port)

    TestConfig.receivers = receivers

    logger.info('Receivers started on ports %s', sorted(placeholders.values()))

    return placeholders

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session', params=get_backend_names(), autouse=True)
def zato_server(request:'any_', certificate_paths:'CertificatePaths') -> 'any_':
    """ One quickstart server per pub/sub backend.
    """
    backend_name = request.param

    # Leftover servers from interrupted previous runs
    _ = subprocess.run(['pkill', '-f', 'zato.server.main'], capture_output=True)
    time.sleep(_leftover_kill_wait)

    start_time = time.monotonic()

    state = SessionState('zato.test.queue_delivery_rest', f'server-logs-queue-delivery-rest-{backend_name}.txt')
    _ = atexit.register(state.cleanup)

    state.test_data_directory = mkdtemp(prefix=f'zato_queue_delivery_rest_{backend_name}_')

    backend = start_backend(backend_name, state.test_data_directory, certificate_paths)
    logger.info('Backend %s ready: %.1fs', backend_name, time.monotonic() - start_time)

    zato_base = os.environ['ZATO_TEST_BASE_DIR']
    zato_bin = os.path.join(zato_base, 'code', 'bin', 'zato')

    invoke_password = 'test.invoke.' + CryptoManager.generate_hex_string()

    placeholders = _start_receivers(state)
    rendered_yaml = render_template(_template_path, placeholders)

    if backend.broker:
        declare_broker_queues(backend.broker)
        rendered_yaml = add_amqp_config(rendered_yaml, backend.broker)

    # The audit log gets a file of its own, or the events land in the developer's database
    audit_db_path = os.path.join(state.test_data_directory, 'audit.db')
    os.environ['Zato_Audit_Log_DB_Name'] = audit_db_path

    # Every process started from here on inherits the backend as its pub/sub database
    with database_env(PubSub_Env_Prefix, backend.details):

        server_directory = run_quickstart_and_enmasse(
            state=state,
            logger=logger,
            zato_bin=zato_bin,
            invoke_password=invoke_password,
            rendered_yaml=rendered_yaml,
            quickstart_prefix='zato_queue_delivery_rest_qs_',
        )

        pickup_directory = os.path.join(server_directory, 'pickup', 'incoming', 'services')
        _ = shutil.copy2(_services_source, os.path.join(pickup_directory, os.path.basename(_services_source)))

        server_port = find_free_port()
        broker_port = find_free_port()

        _ = start_server_process(
            state=state,
            logger=logger,
            zato_bin=zato_bin,
            server_directory=server_directory,
            server_port=server_port,
            broker_port=broker_port,
            extra_server_env={},
            patch_server_conf_bind=True,
        )

        logger.info('Total setup on %s: %.1fs', backend_name, time.monotonic() - start_time)

        TestConfig.base_url = f'http://127.0.0.1:{server_port}'
        TestConfig.password = invoke_password
        TestConfig.server_directory = server_directory
        TestConfig.server_port = server_port
        TestConfig.zato_bin = zato_bin
        TestConfig.backend = backend
        TestConfig.state = state

        yield

        state.cleanup()

    backend.stop()

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(autouse=True)
def clear_receivers() -> 'any_':
    """ Every test starts with endpoints that have received nothing and are accepting everything.
    """
    for receiver in TestConfig.receivers.values():
        receiver.clear()

    yield

    for receiver in TestConfig.receivers.values():
        receiver.accept_all()

    client = get_client()

    for conn_name in Connections.values():
        queue = wait_for_queue_empty(client, conn_name)

        if queue['depth'] != 0 or queue['messages']:
            raise Exception(f'Queue of `{conn_name}` did not drain, depth {queue["depth"]}, messages {queue["messages"]}')

    discard_all_dlqs()

# ################################################################################################################################
# ################################################################################################################################
