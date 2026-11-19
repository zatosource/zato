# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The file-transfer listener of the pickup directory of a test environment. The listener is a process of the environment,
# started next to the server as the Docker image starts it with `make file-pickup-listener`, and it runs independently
# of the server process, so the server can be started, killed and started again while the listener runs.

# stdlib
import logging
import os
import subprocess
import threading
import time

# Zato
from zato.common.test.process_util import kill_process_tree
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from typing import IO
    from zato.common.typing_ import strset
    bytesio = IO[bytes]

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The environment variable with the base directory of the repository
    Env_Base_Dir = 'ZATO_TEST_BASE_DIR'

    # The listener, relative to the base directory of the repository
    Listener_Path = os.path.join('code', 'zato-common', 'src', 'zato', 'common', 'file_transfer', 'listener.py')

    # The line that the listener writes once the server deployed a file, followed by the path of the file
    Deployed_Marker = 'Deployed -> '

    # How long the listener sets its directory watch up, and how long a file may take to be deployed, in seconds
    Settle_Seconds = 2
    Deploy_Timeout = 30

# ################################################################################################################################
# ################################################################################################################################

class PickupListener:
    """ The file-transfer listener of the pickup directory of one server.
    """

    def __init__(self, name:'str', server_directory:'str', web_admin_repo_dir:'str', server_port:'int') -> 'None':

        self.name = name
        self.pickup_directory = os.path.join(server_directory, 'pickup', 'incoming', 'services')
        self.web_admin_repo_dir = web_admin_repo_dir
        self.server_port = server_port

        base_dir = os.environ[ModuleCtx.Env_Base_Dir]
        self.zato_python = os.path.join(base_dir, 'code', 'bin', 'python')
        self.listener_path = os.path.join(base_dir, ModuleCtx.Listener_Path)

        self.logger = logging.getLogger(f'zato.test.pickup_listener.{name}')

        self.process:'subprocess.Popen[bytes] | None' = None

        # Every path that the listener reported as deployed
        self.deployed_paths:'strset' = set()
        self.deployed_condition = threading.Condition()

# ################################################################################################################################

    def start(self) -> 'None':
        """ Starts the listener with the credentials of the Dashboard of the environment and the port of its server.
        """
        environment = dict(os.environ)
        environment['Zato_Config_Bind_Port'] = str(self.server_port)
        environment['Zato_Web_Admin_Repo_Dir'] = self.web_admin_repo_dir
        _ = environment.pop('COVERAGE_PROCESS_START', None)

        # The listener runs in a session of its own, so that stopping it reaches every process that it started ..
        self.process = subprocess.Popen(
            [self.zato_python, self.listener_path, self.pickup_directory],
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )

        # .. its output is drained, which is where the deployed paths are read from ..
        output_thread = threading.Thread(
            target=self._read_output,
            args=(self.process,),
            name=f'zato-pickup-listener-{self.name}',
            daemon=True,
        )
        output_thread.start()

        # .. and a file written before the directory watch is in place would not be deployed.
        time.sleep(ModuleCtx.Settle_Seconds)

# ################################################################################################################################

    def _read_output(self, process:'subprocess.Popen[bytes]') -> 'None':
        """ Logs each line that the listener writes and records the path of each file that the server deployed.
        """
        stdout = cast_('bytesio', process.stdout)

        for line in iter(stdout.readline, b''):
            text = line.decode('utf8', errors='replace').rstrip()
            self.logger.info('%s', text)

            if ModuleCtx.Deployed_Marker in text:
                _, deployed_path = text.split(ModuleCtx.Deployed_Marker)

                with self.deployed_condition:
                    self.deployed_paths.add(deployed_path)
                    self.deployed_condition.notify_all()

# ################################################################################################################################

    def deploy(self, file_name:'str', data:'bytes') -> 'None':
        """ Writes a file into the pickup directory and waits until the listener reports that the server deployed it.
        """
        file_path = os.path.join(self.pickup_directory, file_name)

        # A path deployed before must be reported again for this write ..
        with self.deployed_condition:
            self.deployed_paths.discard(file_path)

        # .. the file is written ..
        with open(file_path, 'wb') as file_handle:
            _ = file_handle.write(data)

        def _is_deployed() -> 'bool':
            out = file_path in self.deployed_paths
            return out

        # .. and the listener deploys it.
        with self.deployed_condition:
            is_deployed = self.deployed_condition.wait_for(_is_deployed, timeout=ModuleCtx.Deploy_Timeout)

        if not is_deployed:
            raise Exception(f'The listener did not deploy {file_path} within {ModuleCtx.Deploy_Timeout}s')

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Stops the listener, which is not running if the environment was not created in full.
        """
        if self.process:
            kill_process_tree(self.process)
            self.process = None

# ################################################################################################################################
# ################################################################################################################################
