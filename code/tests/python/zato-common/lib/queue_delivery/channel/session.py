# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What a channel suite's conftest.py builds its session fixture out of - one server per pub/sub backend, started before
# enmasse runs because a channel points to a service and the service has to be deployed first.

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
    SessionState, start_server_process

# Test support
from live_sql.env import database_env
from queue_delivery.amqp import build_amqp_yaml, declare_broker_queues
from queue_delivery.backends import PubSub_Env_Prefix, start_backend
from queue_delivery.channel.client import Counting_Pickup_Name
from queue_delivery.type_under_test import TestConfig

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from certificates import CertificatePaths
    from zato.common.typing_ import any_
    from queue_delivery.backends import Backend
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
    """ One server on one backend, with the channels of a transport's template on it.
    """

    def __init__(self, type_under_test:'ChannelTypeUnderTest', backend_name:'str') -> 'None':
        self.type_under_test = type_under_test
        self.backend_name = backend_name

        self.suite_name = type_under_test.suite_name
        self.logger_name = f'zato.test.queue_delivery_{self.suite_name}'

        self.state = SessionState(
            self.logger_name,
            f'server-logs-queue-delivery-{self.suite_name}-{backend_name}.txt',
        )

        self.backend:'Backend' = cast_('Backend', None)

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

        result = subprocess.run(command, capture_output=True, text=True, timeout=_import_timeout, env=environment)

        if result.returncode != 0:
            raise Exception(f'enmasse import failed:\nstdout: {result.stdout}\nstderr: {result.stderr}')

        logger.info('Channels imported from %s', input_path)

# ################################################################################################################################

    def start(self, certificate_paths:'CertificatePaths') -> 'None':
        """ Starts the backend and the server, imports the channels and points TestConfig at it all.
        """
        # Leftover servers from interrupted previous runs
        _ = subprocess.run(['pkill', '-f', 'zato.server.main'], capture_output=True)
        time.sleep(_leftover_kill_wait)

        start_time = time.monotonic()

        _ = atexit.register(self.state.cleanup)

        test_data_directory = mkdtemp(prefix=f'zato_queue_delivery_{self.suite_name}_{self.backend_name}_')
        self.state.test_data_directory = test_data_directory

        backend = start_backend(self.backend_name, test_data_directory, certificate_paths, self.suite_name)
        self.backend = backend

        logger.info('Backend %s ready: %.1fs', self.backend_name, time.monotonic() - start_time)

        zato_base = os.environ['ZATO_TEST_BASE_DIR']
        zato_bin = os.path.join(zato_base, 'code', 'bin', 'zato')

        invoke_password = 'test.invoke.' + CryptoManager.generate_hex_string()

        # The audit log gets a file of its own, or the events land in the developer's database
        audit_db_path = os.path.join(test_data_directory, 'audit.db')
        os.environ['Zato_Audit_Log_DB_Name'] = audit_db_path

        # Every process started from here on inherits the backend as its pub/sub database
        self._exit_stack.enter_context(database_env(PubSub_Env_Prefix, backend.details))

        # On a broker backend every channel's topic is an AMQP-backed one, and the topics go in before the server
        # starts, which is when it reads which topics have a backend of their own. The channels themselves wait
        # until the server runs, as their services are deployed only then.
        if backend.broker:
            amqp_type:'any_' = self.type_under_test
            declare_broker_queues(backend.broker, amqp_type)
            pre_start_yaml = build_amqp_yaml(backend.broker, amqp_type)
        else:
            pre_start_yaml = ''

        server_directory = run_quickstart_and_enmasse(
            state=self.state,
            logger=logger,
            zato_bin=zato_bin,
            invoke_password=invoke_password,
            rendered_yaml=pre_start_yaml,
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

        rendered_yaml = render_template(self.type_under_test.template_path, {})

        self._import_channels(zato_bin, server_directory, rendered_yaml, test_data_directory)

        logger.info('Total setup on %s: %.1fs', self.backend_name, time.monotonic() - start_time)

        TestConfig.type_under_test = cast_('any_', self.type_under_test)
        TestConfig.base_url = f'http://127.0.0.1:{server_port}'
        TestConfig.password = invoke_password
        TestConfig.server_directory = server_directory
        TestConfig.server_port = server_port
        TestConfig.zato_bin = zato_bin
        TestConfig.backend = backend
        TestConfig.state = self.state
        TestConfig.receivers = {}

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Stops the server and the backend.
        """
        self.state.cleanup()
        self._exit_stack.close()
        self.backend.stop()

# ################################################################################################################################
# ################################################################################################################################
