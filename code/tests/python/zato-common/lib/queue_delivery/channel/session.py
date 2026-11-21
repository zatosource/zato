# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What a channel suite's conftest.py builds its session fixture out of - one server, started before enmasse runs
# because a channel points to a service and the service has to be deployed first.

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
from zato.common.typing_ import cast_
from zato.common.test.conftest_base_pubsub import find_free_port, render_template, run_quickstart_and_enmasse, \
    SessionState, start_server_process, wait_for_worker_reload
from zato.common.test.pickup_listener import PickupListener

# Test support
from queue_delivery.backends import get_db_path, pubsub_path_env
from queue_delivery.channel.client import Counting_Pickup_Name
from queue_delivery.type_under_test import TestConfig

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    from queue_delivery.channel.type_under_test import ChannelTypeUnderTest

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.queue_delivery.channel.session')

_directory = os.path.dirname(__file__)

_shared_services_source = os.path.join(_directory, '..', 'shared_services.py')
_shared_services_pickup_name = 'queue_delivery_shared_services.py'

# The counting service's module without the hook - the one a redeploy replaces and then puts back
Counting_Source = os.path.join(_directory, 'counting_services.py')

# The same module with the hook defined
Counting_Hooked_Source = os.path.join(_directory, 'counting_services_hooked.py')

_leftover_kill_wait = 2

# How long enmasse waits for a service a channel points to - the services are deployed as the server starts
_missing_wait_time = '60'
_import_timeout = 180

# ################################################################################################################################
# ################################################################################################################################

class ChannelSession:
    """ One server, with the channels of a transport's template on it.
    """

    def __init__(self, type_under_test:'ChannelTypeUnderTest') -> 'None':
        self.type_under_test = type_under_test

        self.suite_name = type_under_test.suite_name
        self.logger_name = f'zato.test.queue_delivery_{self.suite_name}'

        self.state = SessionState(
            self.logger_name,
            f'server-logs-queue-delivery-{self.suite_name}.txt',
        )

        # The listener of the pickup directory, which is not running if the session did not start in full
        self.pickup_listener:'PickupListener | None' = None

        # Holds the pub/sub database environment for as long as the session runs
        self._exit_stack = ExitStack()

# ################################################################################################################################

    def _copy_services(self, server_directory:'str') -> 'None':
        """ Puts the shared services, the counting service and the transport's own services in the pickup directory,
        where the server deploys them from as it starts.
        """
        pickup_directory = os.path.join(server_directory, 'pickup', 'incoming', 'services')

        _ = shutil.copy2(_shared_services_source, os.path.join(pickup_directory, _shared_services_pickup_name))
        _ = shutil.copy2(Counting_Source, os.path.join(pickup_directory, Counting_Pickup_Name))

        services_source = self.type_under_test.services_source
        _ = shutil.copy2(services_source, os.path.join(pickup_directory, os.path.basename(services_source)))

# ################################################################################################################################

    def _import_channels(self, zato_bin:'str', server_directory:'str', rendered_yaml:'str', test_data_directory:'str') -> 'None':
        """ Imports the transport's template into the running server, the way a user does it.
        """
        input_path = os.path.join(test_data_directory, 'channels.yaml')

        with open(input_path, 'w') as input_file:
            _ = input_file.write(rendered_yaml)

        environment = os.environ.copy()
        _ = environment.pop('COVERAGE_PROCESS_START', None)

        command = [
            zato_bin, 'enmasse', server_directory,
            '--verbose',
            '--import',
            '--input', input_path,
            '--missing-wait-time', _missing_wait_time,
        ]

        reload_count = self.state.worker_reload_count

        result = subprocess.run(command, capture_output=True, text=True, timeout=_import_timeout, env=environment)

        if result.returncode != 0:
            raise Exception(f'enmasse import failed:\nstdout: {result.stdout}\nstderr: {result.stderr}')

        # The channels serve requests only once the worker has reloaded the configuration that the import changed
        wait_for_worker_reload(self.state, reload_count)

        logger.info('Channels imported from %s', input_path)

# ################################################################################################################################

    def start(self) -> 'None':
        """ Starts the server, imports the channels and points TestConfig at it all.
        """
        # Leftover servers from interrupted previous runs
        _ = subprocess.run(['pkill', '-f', 'zato.server.main'], capture_output=True)
        time.sleep(_leftover_kill_wait)

        start_time = time.monotonic()

        _ = atexit.register(self.state.cleanup)

        test_data_directory = mkdtemp(prefix=f'zato_queue_delivery_{self.suite_name}_')
        self.state.test_data_directory = test_data_directory

        db_path = get_db_path(test_data_directory)

        zato_base = os.environ['ZATO_TEST_BASE_DIR']
        zato_bin = os.path.join(zato_base, 'code', 'bin', 'zato')

        invoke_password = 'test.invoke.' + CryptoManager.generate_hex_string()

        # Every process started from here on inherits the SQLite file as its database
        self._exit_stack.enter_context(pubsub_path_env(db_path))

        # The channels are imported once the server runs, as their services are deployed only then
        server_directory = run_quickstart_and_enmasse(
            state=self.state,
            logger=logger,
            zato_bin=zato_bin,
            invoke_password=invoke_password,
            rendered_yaml='',
            quickstart_prefix=f'zato_queue_delivery_{self.suite_name}_qs_',
        )

        self._copy_services(server_directory)

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

        # The listener of the pickup directory runs next to the server for as long as the session does
        quickstart_directory = cast_('str', self.state.quickstart_directory)
        web_admin_repo_dir = os.path.join(quickstart_directory, 'web-admin', 'config', 'repo')

        self.pickup_listener = PickupListener(self.suite_name, server_directory, web_admin_repo_dir, server_port)
        self.pickup_listener.start()

        rendered_yaml = render_template(self.type_under_test.template_path, {})

        self._import_channels(zato_bin, server_directory, rendered_yaml, test_data_directory)

        logger.info('Total setup: %.1fs', time.monotonic() - start_time)

        type_under_test:'any_' = self.type_under_test

        TestConfig.type_under_test = type_under_test
        TestConfig.base_url = f'http://127.0.0.1:{server_port}'
        TestConfig.password = invoke_password
        TestConfig.server_directory = server_directory
        TestConfig.server_port = server_port
        TestConfig.zato_bin = zato_bin
        TestConfig.db_path = db_path
        TestConfig.pickup_listener = self.pickup_listener
        TestConfig.state = self.state
        TestConfig.receivers = {}

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Stops the listener of the pickup directory and the server.
        """
        if self.pickup_listener:
            self.pickup_listener.stop()

        self.state.cleanup()
        self._exit_stack.close()

# ################################################################################################################################
# ################################################################################################################################
