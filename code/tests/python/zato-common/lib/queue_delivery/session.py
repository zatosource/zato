# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What a type's conftest.py builds its fixtures out of - the certificates of a session, one server per pub/sub
# backend with an endpoint per connection of the type's template, and the reset every test starts and ends with.

# stdlib
import atexit
import logging
import os
import shutil
import subprocess
import time
from contextlib import ExitStack
from tempfile import mkdtemp

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.test.conftest_base_pubsub import find_free_port, render_template, run_quickstart_and_enmasse, \
    SessionState, start_server_process

# Test support
from certificates import generate_certificates
from live_sql.env import database_env
from queue_delivery.amqp import add_amqp_config, declare_broker_queues
from queue_delivery.backends import PubSub_Env_Prefix, start_backend
from queue_delivery.client import get_client, wait_for_queue_empty
from queue_delivery.dlq import discard_all_dlqs
from queue_delivery.type_under_test import Connection_Keys, TestConfig

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from certificates import CertificatePaths
    from zato.common.typing_ import strstrdict
    from queue_delivery.backends import Backend
    from queue_delivery.receiver import RecordingReceiver
    from queue_delivery.type_under_test import TypeUnderTest

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.queue_delivery.session')

_shared_services_source = os.path.join(os.path.dirname(__file__), 'shared_services.py')

# The shared services land in the pickup under this name, next to the type's own
_shared_services_pickup_name = 'queue_delivery_shared_services.py'

# The database users inside the containers must be able to traverse into the certificate directory
_certificate_dir_mode = 0o755

_leftover_kill_wait = 2

# ################################################################################################################################
# ################################################################################################################################

class Session:
    """ One server on one backend, with the receivers of a type's connections around it.
    """

    def __init__(self, type_under_test:'TypeUnderTest', backend_name:'str') -> 'None':
        self.type_under_test = type_under_test
        self.backend_name = backend_name

        self.suite_name = type_under_test.suite_name
        self.logger_name = f'zato.test.queue_delivery_{self.suite_name}'

        self.state = SessionState(
            self.logger_name,
            f'server-logs-queue-delivery-{self.suite_name}-{backend_name}.txt',
        )

        self.backend:'Backend' = None # type: ignore[assignment]

        # Holds the pub/sub database environment for as long as the session runs
        self._exit_stack = ExitStack()

# ################################################################################################################################

    def _start_receivers(self) -> 'strstrdict':
        """ Starts one endpoint per connection of the template and returns the port placeholders they fill in.
        """
        receivers:'dict[str, RecordingReceiver]' = {}
        placeholders:'strstrdict' = {}

        for key in Connection_Keys:
            port = find_free_port()

            receiver = self.type_under_test.receiver_class(port)
            receiver.start()

            receivers[key] = receiver
            self.state.receivers.append(receiver)

            placeholders['port_' + key] = str(port)

        TestConfig.receivers = receivers

        logger.info('Receivers started on ports %s', sorted(placeholders.values()))

        return placeholders

# ################################################################################################################################

    def start(self, certificate_paths:'CertificatePaths') -> 'None':
        """ Starts the backend, the receivers and the server, and points TestConfig at them.
        """
        # Leftover servers from interrupted previous runs
        _ = subprocess.run(['pkill', '-f', 'zato.server.main'], capture_output=True)
        time.sleep(_leftover_kill_wait)

        start_time = time.monotonic()

        _ = atexit.register(self.state.cleanup)

        self.state.test_data_directory = mkdtemp(prefix=f'zato_queue_delivery_{self.suite_name}_{self.backend_name}_')

        backend = start_backend(self.backend_name, self.state.test_data_directory, certificate_paths, self.suite_name)
        self.backend = backend

        logger.info('Backend %s ready: %.1fs', self.backend_name, time.monotonic() - start_time)

        zato_base = os.environ['ZATO_TEST_BASE_DIR']
        zato_bin = os.path.join(zato_base, 'code', 'bin', 'zato')

        invoke_password = 'test.invoke.' + CryptoManager.generate_hex_string()

        placeholders = self._start_receivers()
        rendered_yaml = render_template(self.type_under_test.template_path, placeholders)

        if backend.broker:
            declare_broker_queues(backend.broker, self.type_under_test)
            rendered_yaml = add_amqp_config(rendered_yaml, backend.broker, self.type_under_test)

        # The audit log gets a file of its own, or the events land in the developer's database
        audit_db_path = os.path.join(self.state.test_data_directory, 'audit.db')
        os.environ['Zato_Audit_Log_DB_Name'] = audit_db_path

        # Every process started from here on inherits the backend as its pub/sub database
        self._exit_stack.enter_context(database_env(PubSub_Env_Prefix, backend.details))

        server_directory = run_quickstart_and_enmasse(
            state=self.state,
            logger=logger,
            zato_bin=zato_bin,
            invoke_password=invoke_password,
            rendered_yaml=rendered_yaml,
            quickstart_prefix=f'zato_queue_delivery_{self.suite_name}_qs_',
        )

        pickup_directory = os.path.join(server_directory, 'pickup', 'incoming', 'services')

        _ = shutil.copy2(_shared_services_source, os.path.join(pickup_directory, _shared_services_pickup_name))

        services_source = self.type_under_test.services_source
        _ = shutil.copy2(services_source, os.path.join(pickup_directory, os.path.basename(services_source)))

        server_port = find_free_port()
        broker_port = find_free_port()

        _ = start_server_process(
            state=self.state,
            logger=logger,
            zato_bin=zato_bin,
            server_directory=server_directory,
            server_port=server_port,
            broker_port=broker_port,
            extra_server_env={},
            patch_server_conf_bind=True,
        )

        logger.info('Total setup on %s: %.1fs', self.backend_name, time.monotonic() - start_time)

        TestConfig.type_under_test = self.type_under_test
        TestConfig.base_url = f'http://127.0.0.1:{server_port}'
        TestConfig.password = invoke_password
        TestConfig.server_directory = server_directory
        TestConfig.server_port = server_port
        TestConfig.zato_bin = zato_bin
        TestConfig.backend = backend
        TestConfig.state = self.state

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Stops the server, the receivers and the backend.
        """
        self.state.cleanup()
        self._exit_stack.close()
        self.backend.stop()

# ################################################################################################################################
# ################################################################################################################################

def make_certificate_directory() -> 'str':
    """ A directory the throwaway CA and the certificates of a session go to.
    """
    out = mkdtemp(prefix='zato-queue-delivery-certificates-')
    os.chmod(out, _certificate_dir_mode)

    return out

# ################################################################################################################################

def generate_session_certificates(directory:'str') -> 'CertificatePaths':
    """ The throwaway CA along with server and client certificates of a session.
    """
    out = generate_certificates(directory)
    return out

# ################################################################################################################################

def reset_before_test() -> 'None':
    """ Every test starts with endpoints that have received nothing and are accepting everything.
    """
    for receiver in TestConfig.receivers.values():
        receiver.clear()

# ################################################################################################################################

def reset_after_test() -> 'None':
    """ Every test leaves the endpoints accepting, the queues drained and the DLQs empty.
    """
    for receiver in TestConfig.receivers.values():
        receiver.accept_all()

    client = get_client()

    for key in Connection_Keys:
        conn_name = TestConfig.type_under_test.connections[key]
        queue = wait_for_queue_empty(client, conn_name)

        if queue['depth'] != 0 or queue['messages']:
            raise Exception(f'Queue of `{conn_name}` did not drain, depth {queue["depth"]}, messages {queue["messages"]}')

    discard_all_dlqs()

# ################################################################################################################################
# ################################################################################################################################
