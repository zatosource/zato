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
from base64 import b64encode
from dataclasses import dataclass
from subprocess import run as subprocess_run
from tempfile import mkdtemp

# gevent
from gevent.event import Event

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.defaults import default_env_base_dir
from zato.common.test.pubsub_database import get_runtime_dir, is_postgresql_mode, new_sqlite_database, \
     start_pubsub_database, stop_pubsub_database
from zato.common.util.api import get_zato_command
from zato.server.main import run as run_server

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.pubsub_database import PubSubDatabase
    from zato.common.typing_ import any_, anydict, anylist, strdict, strlist, strstrdict
    from zato.server.base.parallel import ParallelServer

    any_ = any_
    anydict = anydict
    anylist = anylist
    ParallelServer = ParallelServer
    PubSubDatabase = PubSubDatabase
    strdict = strdict
    strlist = strlist
    strstrdict = strstrdict

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The prefix of the temporary directory of each server
    Work_Dir_Prefix = 'zato-pubsub-in-process-'

    # The name of the quickstart environment and of its server
    Quickstart_Dir_Name = 'env'
    Server_Dir_Name = 'server1'

    # How long the creation of the quickstart environment may take, in seconds
    Quickstart_Timeout = 600

    # The directory of a server that it deploys files from, relative to the server's directory
    Pickup_Dir = os.path.join('pickup', 'incoming', 'services')

    # The file in which the active server records its generation, relative to the server's directory
    Generation_File_Name = 'database-generation'

    # The service that the file-pickup listener sends each file to
    Hot_Deploy_Service = 'zato.hot-deploy.create'

    # The server recognizes an enmasse file by the word in its name and by its extension
    Enmasse_File_Prefix = 'enmasse-'
    Enmasse_File_Suffix = '.yaml'

    # The enmasse file that each server is created with
    Initial_Enmasse_Name = 'initial'

    # How long an import of an enmasse file may take, in seconds
    Import_Timeout = 120

    # The logger that reports the end of each command that the server runs, and the message it reports it with
    Commands_Logger = 'zato.server.commands'
    Command_Completed_Prefix = 'Command `%s` completed in'

    # The position of the command and of its exit code in the arguments of that message
    Command_Arg_Index = 0
    Exit_Code_Arg_Index = 2

    # The variable that tells an import not to request a reload, which this process runs itself
    Env_Needs_Config_Reload = 'Zato_Needs_Config_Reload'

    # The variable with the path to the generation file of the active server
    Env_Generation_File = 'Zato_Database_Generation_File'

    # The variable that coverage reads in each process it measures, which quickstart does not run under
    Env_Coverage = 'COVERAGE_PROCESS_START'

    # The file that the server's startup creates in the default environment if it is missing
    Blocked_Paths_File = os.path.join(default_env_base_dir, 'blocked-paths.txt')

    # The label of the PostgreSQL containers of the in-process servers
    Database_Label = 'in-process'

    # The options that the command line of the server builds
    Run_Options:'anydict' = {
        'fg': True,
        'sync_internal': True,
        'secret_key': '',
        'stderr_path': None,
        'env_file': '',
        'stop_after': None,
        'deploy_auto_from': '',
    }

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class _LoggerState:
    level: 'int'
    disabled: 'bool'
    propagate: 'bool'
    handlers: 'anylist'

# ################################################################################################################################
# ################################################################################################################################

class _ProcessState:
    """ The state of this process that the startup of a server changes, which the server restores when it stops.
    """

    def __init__(self) -> 'None':
        self.environ:'strstrdict' = dict(os.environ)
        self.cwd = os.getcwd()
        self.sys_path:'strlist' = list(sys.path)
        self.has_env_base_dir = os.path.exists(default_env_base_dir)
        self.has_blocked_paths_file = os.path.exists(ModuleCtx.Blocked_Paths_File)
        self.root = self._get_logger_state(logging.root)
        self.loggers:'strdict' = {}

        for name, logger in logging.root.manager.loggerDict.items():
            if isinstance(logger, logging.Logger):
                self.loggers[name] = self._get_logger_state(logger)

# ################################################################################################################################

    def _get_logger_state(self, logger:'logging.Logger') -> '_LoggerState':
        out = _LoggerState()
        out.level = logger.level
        out.disabled = logger.disabled
        out.propagate = logger.propagate
        out.handlers = list(logger.handlers)

        return out

# ################################################################################################################################

    def _restore_logger(self, logger:'logging.Logger', state:'_LoggerState | None') -> 'None':
        """ Closes the handlers that the server added to a logger and restores the logger as it was.
        """
        if state is None:
            previous_handlers:'anylist' = []
        else:
            previous_handlers = state.handlers

        for handler in logger.handlers:
            if handler not in previous_handlers:
                handler.close()

        # A logger that the server created has no handlers and passes its records on ..
        if state is None:
            logger.handlers = []
            logger.disabled = False
            logger.propagate = True
            logger.setLevel(logging.NOTSET)

        # .. while any other one is restored as it was.
        else:
            logger.handlers = state.handlers
            logger.disabled = state.disabled
            logger.propagate = state.propagate
            logger.setLevel(state.level)

# ################################################################################################################################

    def restore(self) -> 'None':
        """ Restores the environment, the working directory, the import path, the logging and the default environment.
        """
        os.environ.clear()
        os.environ.update(self.environ)

        os.chdir(self.cwd)
        sys.path[:] = self.sys_path

        self._restore_logger(logging.root, self.root)

        for name, logger in logging.root.manager.loggerDict.items():
            if isinstance(logger, logging.Logger):
                state = self.loggers.get(name)
                self._restore_logger(logger, state)

        if not self.has_blocked_paths_file:
            if os.path.exists(ModuleCtx.Blocked_Paths_File):
                os.remove(ModuleCtx.Blocked_Paths_File)

        if not self.has_env_base_dir:
            if os.path.exists(default_env_base_dir):
                os.rmdir(default_env_base_dir)

# ################################################################################################################################
# ################################################################################################################################

class _ImportCompletion(logging.Handler):
    """ Waits for the end of the import of one enmasse file that the server runs as a command.
    """

    def __init__(self, path:'str') -> 'None':
        super().__init__()
        self.path = path
        self.exit_code = -1
        self.completed = Event()

# ################################################################################################################################

    def emit(self, record:'logging.LogRecord') -> 'None':
        """ Records the exit code of the command that imported the file.
        """
        message:'str' = record.msg

        if not message.startswith(ModuleCtx.Command_Completed_Prefix):
            return

        args:'any_' = record.args
        command = args[ModuleCtx.Command_Arg_Index]

        if self.path in command:
            self.exit_code = args[ModuleCtx.Exit_Code_Arg_Index]
            self.completed.set()

# ################################################################################################################################
# ################################################################################################################################

class InProcessServer:
    """ A Zato server that runs pub/sub in this process, under gevent, with the files of its configuration and of its
    pub/sub database in a temporary directory, and without the arbiter, the config process, the scheduler, the HTTP
    port or the listeners of the queue bridge, of the API portal and of the rule engine.
    """

    def __init__(self, *, db_mode:'str', enmasse_yaml:'str', service_modules:'strstrdict') -> 'None':
        self.db_mode = db_mode
        self.enmasse_yaml = enmasse_yaml
        self.service_modules = service_modules

        self.work_dir = ''
        self.server_dir = ''
        self.pickup_dir = ''
        self.db_env:'strstrdict' = {}

        self._database:'PubSubDatabase | None' = None
        self._process_state:'_ProcessState | None' = None
        self._server:'ParallelServer | None' = None

# ################################################################################################################################

    def __enter__(self) -> 'InProcessServer':
        self.start()
        return self

# ################################################################################################################################

    def __exit__(self, *args:'any_') -> 'None':
        self.stop()

# ################################################################################################################################

    @property
    def server(self) -> 'ParallelServer':
        if self._server is None:
            raise Exception('The server is not started')
        return self._server

# ################################################################################################################################

    def start(self) -> 'None':
        """ Creates the server's directory and database, assembles the server and applies its initial enmasse file.
        """

        # The directory of the server and the files that it deploys during its assembly ..
        self.work_dir = mkdtemp(prefix=ModuleCtx.Work_Dir_Prefix, dir=get_runtime_dir())
        self._create_server_directory()
        self._write_service_modules()

        # .. its pub/sub database ..
        self._start_database()

        # .. the state of this process that the server changes is kept for the stop ..
        self._process_state = _ProcessState()

        # .. the server reads its database from the environment and requests no reload after an import ..
        os.environ.update(self.db_env)
        os.environ[ModuleCtx.Env_Generation_File] = os.path.join(self.server_dir, ModuleCtx.Generation_File_Name)
        os.environ[ModuleCtx.Env_Needs_Config_Reload] = 'False'

        # .. the default environment may be missing, in which case the startup's file is created in a new one ..
        if not self._process_state.has_env_base_dir:
            os.makedirs(default_env_base_dir)

        # .. the server is assembled ..
        server = run_server(self.server_dir, start_server=False, options=ModuleCtx.Run_Options)

        if server is None:
            raise Exception('The server was not built')

        self._server = server
        self._assemble()

        # .. and its configuration is imported.
        exit_code = self.apply_enmasse(ModuleCtx.Initial_Enmasse_Name, self.enmasse_yaml)

        if exit_code != 0:
            raise Exception(f'The initial enmasse file could not be imported, exit code {exit_code}')

# ################################################################################################################################

    def _create_server_directory(self) -> 'None':
        """ Creates a quickstart environment with one server, whose directory the server runs from.
        """
        quickstart_dir = os.path.join(self.work_dir, ModuleCtx.Quickstart_Dir_Name)
        # A urlsafe password may begin with `-`, which argparse takes for a flag
        password = 'in.process.' + CryptoManager.generate_hex_string()

        command = [
            get_zato_command(), 'quickstart', 'create', quickstart_dir, '--force',
            '--password', password,
            '--server-api-client-for-scheduler-password', password,
            '--no-scheduler',
        ]

        env = dict(os.environ)
        _ = env.pop(ModuleCtx.Env_Coverage, None)

        result = subprocess_run(command, env=env, capture_output=True, text=True, timeout=ModuleCtx.Quickstart_Timeout)

        if result.returncode != 0:
            raise Exception(f'Quickstart failed with exit code {result.returncode}:\n{result.stdout}\n{result.stderr}')

        self.server_dir = os.path.join(quickstart_dir, ModuleCtx.Server_Dir_Name)
        self.pickup_dir = os.path.join(self.server_dir, ModuleCtx.Pickup_Dir)

        os.makedirs(self.pickup_dir, exist_ok=True)

# ################################################################################################################################

    def _write_service_modules(self) -> 'None':
        """ Writes the modules of the services that the tests use into the pickup directory.
        """
        for file_name, source in self.service_modules.items():
            path = os.path.join(self.pickup_dir, file_name)
            with open(path, 'w') as module_file:
                _ = module_file.write(source)

# ################################################################################################################################

    def _start_database(self) -> 'None':
        """ Starts a PostgreSQL container or selects an SQLite file in the temporary directory.
        """
        if is_postgresql_mode(self.db_mode):
            database = start_pubsub_database(ModuleCtx.Database_Label, self.db_mode)
        else:
            database = new_sqlite_database(self.work_dir)

        self._database = database
        self.db_env = database.env

# ################################################################################################################################

    def _assemble(self) -> 'None':
        """ Runs the stages of the server's startup that pub/sub needs, in the order in which the startup runs them.
        """
        server = self.server

        # The process, the ODB and the configuration read from it ..
        server._start_process()
        server_row = server._start_odb()
        server._pre_initialize()
        server._start_http_methods()
        server._start_config(server_row)
        server._start_hot_deploy_config()
        server.set_up_api_key_config()

        # .. the services, the config manager and the config dispatcher, which applies each event in this process ..
        locally_deployed = server._after_init_common(server_row)
        server._start_config_manager()
        server._start_hot_deploy_directories()
        server._start_config_dispatcher()
        server._after_init_accepted(locally_deployed)

        # .. the service modules of the pickup directory ..
        server.deploy_pickup_dir(is_relayed=False)

        # .. and pub/sub.
        server._start_pubsub_backend()

# ################################################################################################################################

    def apply_enmasse(self, name:'str', enmasse_yaml:'str') -> 'int':
        """ Places an enmasse file in the pickup directory and sends the server the request that the file-pickup listener
        sends for it. Once the import that the server runs ends with exit code 0, the server reloads its configuration,
        as a reload requested by the import does. Returns the exit code of the import.
        """
        file_name = ModuleCtx.Enmasse_File_Prefix + name + ModuleCtx.Enmasse_File_Suffix
        path = os.path.join(self.pickup_dir, file_name)

        with open(path, 'w') as enmasse_file:
            _ = enmasse_file.write(enmasse_yaml)

        # The request of the listener has the contents of the file and its path ..
        data = enmasse_yaml.encode('utf8')
        payload = b64encode(data)
        payload = payload.decode('ascii')

        request = {
            'payload': payload,
            'payload_name': path,
        }

        # .. the end of the import is reported by the logger of the commands that the server runs ..
        completion = _ImportCompletion(path)
        commands_logger = logging.getLogger(ModuleCtx.Commands_Logger)
        previous_level = commands_logger.level

        commands_logger.addHandler(completion)
        commands_logger.setLevel(logging.INFO)

        try:
            _ = self.server.invoke(ModuleCtx.Hot_Deploy_Service, request)

            if not completion.completed.wait(ModuleCtx.Import_Timeout):
                raise Exception(f'The import of `{path}` did not end within {ModuleCtx.Import_Timeout} s')

        finally:
            commands_logger.removeHandler(completion)
            commands_logger.setLevel(previous_level)

        # .. and only a successful import is followed by a reload.
        if completion.exit_code == 0:
            self.server.reload_config()

        out = completion.exit_code
        return out

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Releases the resources of the server, restores this process and removes the server's directory and database.
        """
        if self._server:
            _ = self._server.release_resources()
            self._server = None

        if self._process_state:
            self._process_state.restore()
            self._process_state = None

        if self._database:
            if is_postgresql_mode(self.db_mode):
                stop_pubsub_database(self._database)
            self._database = None

        if self.work_dir:
            shutil.rmtree(self.work_dir)
            self.work_dir = ''

# ################################################################################################################################
# ################################################################################################################################
