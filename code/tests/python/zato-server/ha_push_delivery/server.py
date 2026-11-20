# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# A Zato server for the tests of push delivery batches, on a SQLite database of its own and on reserved ports.
# The server is started with `zato start`, stopped with `zato stop` or killed with SIGKILL, and started again
# on the same data. The endpoint that its outgoing REST connection calls runs in the test process on a reserved port.

# stdlib
import errno
import logging
import os
import shutil
import subprocess
from functools import partial

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.db_env.database_env import DatabaseEnv
from zato.common.db_env.fence import ModuleCtx as FenceCtx
from zato.common.test.conftest_base_pubsub import run_quickstart_and_enmasse, SessionState, start_server_process
from zato.common.test.process_util import kill_process_tree_at_once
from zato.common.test.receiver import WebhookReceiver
from zato.common.test.reservation import PortInUse, reserve_port, start_on_reserved_port
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.reservation import PortReservation, ReservedStart
    from zato.common.typing_ import strstrdict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.ha_push_delivery')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The purpose under which the ports of the server and of the endpoint are reserved
    Port_Purpose = 'ha-push-delivery'

    # The environment variable with the base directory of the repository
    Env_Base_Dir = 'ZATO_TEST_BASE_DIR'

    # The prefix of the quickstart directory and the name of the copy of the server log
    Quickstart_Prefix    = 'zato_ha_push_delivery_'
    Server_Log_Copy_Name = 'server-logs-ha-push-delivery.txt'

    # The name of the file of the generation of the active server in the server directory
    Generation_File_Name = 'database-generation'

    # The address that the server and the endpoint listen on
    Host = '127.0.0.1'

    # How long a stopped server is given to exit, in seconds
    Stop_Timeout = 120

# ################################################################################################################################
# ################################################################################################################################

class PushDeliveryServer:
    """ One Zato server that a test starts, stops or kills, and starts again on the same data.
    """

    def __init__(self, server_env:'strstrdict') -> 'None':

        self.state = SessionState(logger.name, ModuleCtx.Server_Log_Copy_Name)

        base_dir = os.environ[ModuleCtx.Env_Base_Dir]
        self.zato_bin = os.path.join(base_dir, 'code', 'bin', 'zato')

        self.invoke_password = 'test.invoke.' + CryptoManager.generate_hex_string()
        self.server_env = dict(server_env)

        # The ports of the broker and of MLLP stay the same across the starts of the server ..
        self.broker_port = reserve_port(ModuleCtx.Port_Purpose)
        self.mllp_port = reserve_port(ModuleCtx.Port_Purpose)
        self.state.mllp_port = self.mllp_port.port

        # .. while its own port is reserved anew each time that it starts.
        self.server_port:'PortReservation | None' = None
        self.base_url = ''

        self.server_directory = ''

# ################################################################################################################################

    def create(self, rendered_yaml:'str', services_path:'str') -> 'None':
        """ Creates the quickstart environment of the server, imports its enmasse file, places its services
        in the pickup directory and selects its SQLite database, which the test process reads too.
        """
        self.server_directory = run_quickstart_and_enmasse(
            state=self.state,
            logger=logger,
            zato_bin=self.zato_bin,
            invoke_password=self.invoke_password,
            rendered_yaml=rendered_yaml,
            quickstart_prefix=ModuleCtx.Quickstart_Prefix,
        )

        # The server deploys the services of its pickup directory as it starts ..
        pickup_dir = os.path.join(self.server_directory, 'pickup', 'incoming', 'services')
        _ = shutil.copy2(services_path, pickup_dir)

        # .. and the server and the test process use one database ..
        database_path = os.path.join(self.server_directory, DatabaseEnv.File_Name)
        generation_path = os.path.join(self.server_directory, ModuleCtx.Generation_File_Name)

        database_env = {
            DatabaseEnv.Env_Type: DatabaseEnv.Type_SQLite,
            DatabaseEnv.Env_Path: database_path,
            FenceCtx.Env_Generation_File: generation_path,
        }

        # .. which the test process selects as well.
        os.environ.update(database_env)
        self.server_env.update(database_env)

        logger.info('Zato database: %s', database_path)

# ################################################################################################################################

    def start(self) -> 'None':
        """ Starts the server on a newly reserved port and waits until its worker is ready.
        """
        # The port of a previous start is no longer in use ..
        if self.server_port:
            self.server_port.release()
            self.server_port = None

        # .. and the server starts on a port that no other test holds.
        started = start_on_reserved_port(ModuleCtx.Port_Purpose, self._start_on_port)

        self.server_port = started.reservation
        self.base_url = f'http://{ModuleCtx.Host}:{self.server_port.port}'

# ################################################################################################################################

    def _start_on_port(self, port:'int') -> 'float':
        """ Starts the server on the port, which start_server_process also sets in the server configuration.
        """
        out = start_server_process(
            state=self.state,
            logger=logger,
            zato_bin=self.zato_bin,
            server_directory=self.server_directory,
            server_port=port,
            broker_port=self.broker_port.port,
            extra_server_env=self.server_env,
            patch_server_conf_bind=True,
        )

        return out

# ################################################################################################################################

    def kill(self) -> 'None':
        """ Kills the server and every process that it started with SIGKILL.
        """
        kill_process_tree_at_once(self.state.server_process)
        self.state.server_process = None

        logger.info('Server killed')

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Stops the server with `zato stop` and waits until it has exited.
        """
        command = [self.zato_bin, 'stop', self.server_directory]
        _ = subprocess.run(command, capture_output=True, check=False, timeout=ModuleCtx.Stop_Timeout)

        server_process = cast_('subprocess.Popen[bytes]', self.state.server_process)
        _ = server_process.wait(timeout=ModuleCtx.Stop_Timeout)

        self.state.server_process = None

        logger.info('Server stopped')

# ################################################################################################################################

    def remove(self) -> 'None':
        """ Kills the server if it runs, removes its environment and releases its ports.
        """
        if self.state.server_process:
            self.kill()

        self.state.cleanup()

        if self.server_port:
            self.server_port.release()

        self.broker_port.release()
        self.mllp_port.release()

# ################################################################################################################################
# ################################################################################################################################

def _start_receiver(output_dir:'str', url_path:'str', port:'int') -> 'WebhookReceiver':
    """ Starts the endpoint on the port, raising PortInUse if another process took the port before it was bound.
    """
    out = WebhookReceiver(port, output_dir, url_path, ModuleCtx.Host)

    try:
        out.start()
    except OSError as e:
        if e.errno == errno.EADDRINUSE:
            raise PortInUse(f'Port {port} of the endpoint is in use') from e
        raise

    return out

# ################################################################################################################################

def start_receiver(output_dir:'str', url_path:'str') -> 'ReservedStart':
    """ Starts the endpoint that the outgoing REST connection of the server calls, on a reserved port.
    The result holds the reservation of the port and the receiver.
    """
    start = partial(_start_receiver, output_dir, url_path)

    out = start_on_reserved_port(ModuleCtx.Port_Purpose, start)
    return out

# ################################################################################################################################
# ################################################################################################################################
