# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# A Zato server for the power loss tests. The server is created from a quickstart environment and an enmasse file,
# started with `zato start`, killed with SIGKILL together with every process it started, and started again
# on the same data.

# stdlib
import logging
import os
import shutil

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.test.conftest_base_pubsub import find_free_port, render_template, run_quickstart_and_enmasse, \
    SessionState, start_server_process
from zato.common.test.pickup_listener import PickupListener
from zato.common.test.process_util import kill_process_tree_at_once
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strlist, strstrdict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.durability.power_loss')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The environment variable with the base directory of the repository
    Env_Base_Dir = 'ZATO_TEST_BASE_DIR'

    # The environment variable with the file in which the generation of the active server is recorded
    Env_Generation_File = 'Zato_Database_Generation_File'

    # The name of that file in the server directory
    Generation_File_Name = 'database-generation'

    # The address that the server listens on
    Host = '127.0.0.1'

# ################################################################################################################################
# ################################################################################################################################

class PowerLossServer:
    """ One Zato server that a test starts, kills and starts again on the same data.
    """

    def __init__(
        self,
        name:'str',
        parent_dir:'str',
        template_path:'str',
        placeholders:'strstrdict',
        hot_deploy_sources:'strlist',
        database_env:'strstrdict',
        ) -> 'None':

        self.name = name
        self.parent_dir = parent_dir
        self.template_path = template_path
        self.placeholders = placeholders
        self.hot_deploy_sources = hot_deploy_sources
        self.database_env = database_env

        self.state = SessionState(f'zato.test.durability.power_loss.{name}', f'server-logs-power-loss-{name}.txt')
        self.logger = logging.getLogger(f'zato.test.durability.power_loss.{name}')

        base_dir = os.environ[ModuleCtx.Env_Base_Dir]
        self.zato_bin = os.path.join(base_dir, 'code', 'bin', 'zato')

        self.invoke_password = 'test.invoke.' + CryptoManager.generate_hex_string()
        self.server_port = find_free_port()
        self.base_url = f'http://{ModuleCtx.Host}:{self.server_port}'

        self.server_directory = ''
        self.server_env:'strstrdict' = {}

        # The listener of the pickup directory, a process of the environment that runs from its creation to its removal
        self.listener:'PickupListener | None' = None

# ################################################################################################################################

    def create(self) -> 'None':
        """ Creates the quickstart environment of the server, imports its enmasse file, deploys its services
        and starts the file-transfer listener of its pickup directory.
        """
        rendered_yaml = render_template(self.template_path, self.placeholders)

        self.server_directory = run_quickstart_and_enmasse(
            state=self.state,
            logger=self.logger,
            zato_bin=self.zato_bin,
            invoke_password=self.invoke_password,
            rendered_yaml=rendered_yaml,
            quickstart_prefix=f'zato_power_loss_{self.name}_',
            quickstart_parent_dir=self.parent_dir,
        )

        pickup_dir = os.path.join(self.server_directory, 'pickup', 'incoming', 'services')

        for source_path in self.hot_deploy_sources:
            _ = shutil.copy2(source_path, pickup_dir)

        generation_file_path = os.path.join(self.server_directory, ModuleCtx.Generation_File_Name)

        self.server_env = dict(self.database_env)
        self.server_env[ModuleCtx.Env_Generation_File] = generation_file_path

        quickstart_directory = self.state.quickstart_directory
        quickstart_directory = cast_('str', quickstart_directory)

        web_admin_repo_dir = os.path.join(quickstart_directory, 'web-admin', 'config', 'repo')

        self.listener = PickupListener(self.name, self.server_directory, web_admin_repo_dir, self.server_port)
        self.listener.start()

# ################################################################################################################################

    def start(self) -> 'None':
        """ Starts the server and waits until its worker is ready.
        """
        broker_port = find_free_port()

        _ = start_server_process(
            state=self.state,
            logger=self.logger,
            zato_bin=self.zato_bin,
            server_directory=self.server_directory,
            server_port=self.server_port,
            broker_port=broker_port,
            extra_server_env=self.server_env,
            patch_server_conf_bind=True,
        )

# ################################################################################################################################

    def deploy(self, file_name:'str', data:'bytes') -> 'None':
        """ Writes a file into the pickup directory and waits until the listener reports that the server deployed it.
        """
        listener = cast_('PickupListener', self.listener)
        listener.deploy(file_name, data)

# ################################################################################################################################

    def kill(self) -> 'None':
        """ Kills the server and every process that it started with SIGKILL.
        """
        kill_process_tree_at_once(self.state.server_process)
        self.state.server_process = None

        logger.info('Server %s killed', self.name)

# ################################################################################################################################

    def remove(self) -> 'None':
        """ Stops the listener and the server and removes the quickstart environment of the server.
        """
        if self.listener:
            self.listener.stop()

        self.state.cleanup()

# ################################################################################################################################
# ################################################################################################################################
