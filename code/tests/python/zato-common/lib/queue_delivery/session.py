# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What a type's conftest.py builds its fixtures out of - one server with an endpoint per connection of the type's
# template, and the reset every test starts and ends with.

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
from zato.common.test.zato_database import isolated_database_env

# Test support
from queue_delivery.client import get_client, wait_for_queue_empty
from queue_delivery.dlq import discard_all_dlqs
from queue_delivery.type_under_test import Connection_Keys, TestConfig

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strstrdict
    from queue_delivery.receiver import RecordingReceiver
    from queue_delivery.type_under_test import TypeUnderTest

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.queue_delivery.session')

_shared_services_source = os.path.join(os.path.dirname(__file__), 'shared_services.py')

# The shared services land in the pickup under this name, next to the type's own
_shared_services_pickup_name = 'queue_delivery_shared_services.py'

_leftover_kill_wait = 2

# ################################################################################################################################
# ################################################################################################################################

class Session:
    """ One server, with the receivers of a type's connections around it.
    """

    def __init__(self, type_under_test:'TypeUnderTest') -> 'None':
        self.type_under_test = type_under_test

        self.suite_name = type_under_test.suite_name
        self.logger_name = f'zato.test.queue_delivery_{self.suite_name}'

        self.state = SessionState(
            self.logger_name,
            f'server-logs-queue-delivery-{self.suite_name}.txt',
        )

        # Holds the Zato database of the session for as long as the session runs
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

    def start(self) -> 'None':
        """ Starts the receivers and the server, and points TestConfig at them.
        """
        # Leftover servers from interrupted previous runs
        _ = subprocess.run(['pkill', '-f', 'zato.server.main'], capture_output=True)
        time.sleep(_leftover_kill_wait)

        start_time = time.monotonic()

        _ = atexit.register(self.state.cleanup)

        self.state.test_data_directory = mkdtemp(prefix=f'zato_queue_delivery_{self.suite_name}_')

        zato_base = os.environ['ZATO_TEST_BASE_DIR']
        zato_bin = os.path.join(zato_base, 'code', 'bin', 'zato')

        invoke_password = 'test.invoke.' + CryptoManager.generate_hex_string()

        placeholders = self._start_receivers()
        rendered_yaml = render_template(self.type_under_test.template_path, placeholders)

        # Every process started from here on inherits the Zato database of the session
        database_env = self._exit_stack.enter_context(isolated_database_env())

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
            extra_server_env=dict(self.type_under_test.server_environment),
            patch_server_conf_bind=True,
        )

        logger.info('Total setup: %.1fs', time.monotonic() - start_time)

        TestConfig.type_under_test = self.type_under_test
        TestConfig.base_url = f'http://127.0.0.1:{server_port}'
        TestConfig.password = invoke_password
        TestConfig.server_directory = server_directory
        TestConfig.server_port = server_port
        TestConfig.zato_bin = zato_bin
        TestConfig.database_env = database_env
        TestConfig.state = self.state

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Stops the server and the receivers.
        """
        self.state.cleanup()
        self._exit_stack.close()

# ################################################################################################################################
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
