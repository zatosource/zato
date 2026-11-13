# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The environment REST and SOAP channels are invoked in - a Redis instance of its own, a quickstart server
# with the user services of the suite deployed from pickup, and the objects of the suite imported through enmasse.

# stdlib
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
from http.client import OK
from urllib.error import URLError
from urllib.request import Request, urlopen

# psutil
import psutil

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.test import kill_server_process
from zato.common.typing_ import cast_
from zato.common.util.config import get_config_object, update_config_file

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strdict, strlist

# ################################################################################################################################
# ################################################################################################################################

# The command line interface of the virtualenv the tests run in
Zato_Bin = os.path.join(os.path.dirname(sys.executable), 'zato')

# The interface the server and Redis listen on
Host = '127.0.0.1'

# The environment variables through which server components find Redis
_redis_environment_keys = (
    'Zato_Queue_Bridge_Redis',
    'Zato_Rule_Engine_Redis',
    'Zato_Scheduler_Redis',
)

# The variables naming the databases and sockets that otherwise default to the shared quickstart directory,
# each with the name of the file it points to in the temporary directory of the environment
_isolated_file_variables = (
    ('Zato_Audit_Log_DB_Name', 'audit.db'),
    ('Zato_Common_DB_Name', 'common.db'),
    ('Zato_PubSub_DB_Name', 'pubsub.db'),
    ('Zato_Analytics_DB_Path', 'analytics.db'),
    ('Zato_HA_Barrier_Socket', 'barrier.sock'),
)

# The rule engine names its database through a URL rather than through a path
_rule_engine_variable = 'Zato_Rule_Engine_Dashboard_DB_URL'
_rule_engine_file_name = 'rule-engine.db'

_process_kill_timeout = 5
_server_wait_timeout  = 120
_redis_wait_timeout   = 10
_quickstart_timeout   = 180
_enmasse_timeout      = 180
_poll_interval        = 0.2

# How long enmasse waits for a service that a channel names to be deployed, in seconds
_missing_wait_time = '30'

# The process of a server, as its command line names it
_server_module = 'zato.server.main'
_interpreter_name = 'python'

# ################################################################################################################################
# ################################################################################################################################

def find_free_port() -> 'int':
    """ Returns a TCP port on the loopback interface that nothing listens on.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
        tcp_socket.bind((Host, 0))
        socket_address = tcp_socket.getsockname()

    out = socket_address[1]
    return out

# ################################################################################################################################

def _wait_for_port(port:'int', timeout:'float') -> 'None':
    """ Waits until something accepts TCP connections on the given port.
    """
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        try:
            connection = socket.create_connection((Host, port), timeout=_process_kill_timeout)
        except OSError:
            time.sleep(_poll_interval)
        else:
            connection.close()
            return

    raise Exception(f'Nothing listens on {Host}:{port} after {timeout}s')

# ################################################################################################################################

def _wait_for_server(port:'int') -> 'None':
    """ Polls the server's ping endpoint until it returns 200 or the timeout expires.
    """
    ping_url = f'http://{Host}:{port}/zato/ping'
    deadline = time.monotonic() + _server_wait_timeout

    while time.monotonic() < deadline:

        try:
            request = Request(ping_url, method='GET')

            with urlopen(request, timeout=_process_kill_timeout) as response:
                if response.status == OK:
                    return

        except (ConnectionRefusedError, OSError, URLError):
            pass

        time.sleep(_poll_interval)

    raise Exception(f'Server at {Host}:{port} did not respond within {_server_wait_timeout}s')

# ################################################################################################################################
# ################################################################################################################################

class ChannelEnvironment:
    """ A quickstart server with a Redis instance of its own, the user services of the suite in pickup
    and the objects of the suite imported through enmasse.
    """

    def __init__(
        self,
        services:'strdict',
        *,
        name_prefix:'str',
        extra_environment:'strdict | None' = None,
        start_command_prefix:'strlist | None' = None,
        ) -> 'None':

        # The file name in pickup of each service module, mapped to the path of the module
        self.services = services

        self.name_prefix = name_prefix

        if extra_environment is None:
            extra_environment = {}

        # A command the start command runs under, such as a profiler
        if start_command_prefix is None:
            start_command_prefix = []

        self.extra_environment = extra_environment
        self.start_command_prefix = start_command_prefix

        self.temp_directory = ''
        self.server_directory = ''
        self.port = 0
        self.redis_port = 0
        self.base_url = ''

        self.redis_process:'any_' = None
        self.server_process:'any_' = None
        self.server_output_path = ''

        # The monotonic clock reading at which the start command was launched
        self.server_start_time = 0.0

        self.invoke_password = 'test.invoke.' + CryptoManager.generate_hex_string()

# ################################################################################################################################

    @property
    def logs_directory(self) -> 'str':
        out = os.path.join(self.server_directory, 'logs')
        return out

# ################################################################################################################################

    def get_log_path(self, name:'str') -> 'str':
        """ Returns the path of a log file of the server, e.g. server.log or rest.log.
        """
        out = os.path.join(self.logs_directory, name)
        return out

# ################################################################################################################################

    def start(self) -> 'None':
        """ Starts Redis, creates the quickstart environment, deploys the services and starts the server.
        """
        self.temp_directory = tempfile.mkdtemp(prefix=self.name_prefix)

        self._start_redis()
        self._create_quickstart()
        self._start_server()

# ################################################################################################################################

    def _start_redis(self) -> 'None':
        """ Starts a Redis instance that holds no data on disk and listens on a free port.
        """
        self.redis_port = find_free_port()

        command = [
            'redis-server',
            '--port', str(self.redis_port),
            '--bind', Host,
            '--save', '',
            '--appendonly', 'no',
            '--dir', self.temp_directory,
        ]

        self.redis_process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        _wait_for_port(self.redis_port, _redis_wait_timeout)

# ################################################################################################################################

    def _create_quickstart(self) -> 'None':
        """ Creates the quickstart environment and points its server at its own port and its own Redis.
        """
        environment_directory = os.path.join(self.temp_directory, 'env')
        os.mkdir(environment_directory)

        command = [
            Zato_Bin, 'quickstart', 'create', environment_directory,
            '--password', self.invoke_password,
            '--server-api-client-for-scheduler-password', self.invoke_password,
            '--no-scheduler',
        ]

        environment = self._get_isolated_environment()

        result = subprocess.run(
            command, env=environment, capture_output=True, text=True, check=False, timeout=_quickstart_timeout)

        if result.returncode != 0:
            raise Exception(f'quickstart create failed:\nstdout: {result.stdout}\nstderr: {result.stderr}')

        self.server_directory = os.path.join(environment_directory, 'server1')
        self.port = find_free_port()
        self.base_url = f'http://{Host}:{self.port}'

        # The server listens on a port of its own and uses the Redis instance of this environment ..
        repo_location = os.path.join(self.server_directory, 'config', 'repo')
        config = get_config_object(repo_location, 'server.conf')
        config = cast_('any_', config)

        config['main']['bind'] = f'{Host}:{self.port}'
        config['redis']['host'] = Host
        config['redis']['port'] = str(self.redis_port)
        config['redis']['password'] = ''

        update_config_file(config, repo_location, 'server.conf')

        # .. and the services of the suite deploy from pickup during boot.
        pickup_directory = os.path.join(self.server_directory, 'pickup', 'incoming', 'services')
        os.makedirs(pickup_directory, exist_ok=True)

        for file_name, source_path in self.services.items():
            target_path = os.path.join(pickup_directory, file_name)
            _ = shutil.copy2(source_path, target_path)

# ################################################################################################################################

    def _get_isolated_environment(self) -> 'strdict':
        """ Returns the environment variables of every command of this environment, which point each database
        and socket that defaults to a location under the home directory at a file in the temporary directory.
        """
        out = os.environ.copy()

        for variable, file_name in _isolated_file_variables:
            out[variable] = os.path.join(self.temp_directory, file_name)

        rule_engine_path = os.path.join(self.temp_directory, _rule_engine_file_name)
        out[_rule_engine_variable] = 'sqlite:///' + rule_engine_path

        return out

# ################################################################################################################################

    def _get_server_environment(self) -> 'strdict':
        """ Returns the environment variables the server process starts with.
        """
        out = self._get_isolated_environment()

        out['Zato_Config_Bind_Port'] = str(self.port)
        out['Zato_Broker_HTTP_Port'] = str(find_free_port())

        for prefix in _redis_environment_keys:
            out[prefix + '_Host'] = Host
            out[prefix + '_Port'] = str(self.redis_port)

        out.update(self.extra_environment)

        return out

# ################################################################################################################################

    def _start_server(self) -> 'None':
        """ Starts the server in the foreground with its output in a file and waits until it responds.
        """
        self.server_output_path = os.path.join(self.temp_directory, 'server-output.log')
        server_output = open(self.server_output_path, 'w')

        environment = self._get_server_environment()
        command = self.start_command_prefix + [Zato_Bin, 'start', self.server_directory, '--fg']

        self.server_start_time = time.monotonic()
        self.server_process = subprocess.Popen(
            command,
            env=environment,
            stdout=server_output,
            stderr=subprocess.STDOUT,
        )

        try:
            _wait_for_server(self.port)
        except Exception:
            self.stop()
            raise

# ################################################################################################################################

    def get_server_pid(self) -> 'int':
        """ Returns the ID of the process the server runs in, which the start command spawns.
        """
        start_process = psutil.Process(self.server_process.pid)

        # A shell script starts the interpreter and the server renames its own process, so of the two
        # processes naming the server module, the one whose executable is the interpreter is the server.
        for item in start_process.children(recursive=True):
            command_line = item.cmdline()
            if _server_module in command_line:
                executable_name = os.path.basename(item.exe())
                if executable_name.startswith(_interpreter_name):
                    out = item.pid
                    break
        else:
            raise Exception(f'No server process under {self.server_process.pid}')

        return out

# ################################################################################################################################

    def import_yaml(self, yaml_text:'str') -> 'None':
        """ Imports the given enmasse YAML into the running server.
        """
        yaml_path = os.path.join(self.temp_directory, 'enmasse.yaml')

        with open(yaml_path, 'w') as yaml_file:
            _ = yaml_file.write(yaml_text)

        command:'strlist' = [
            Zato_Bin, 'enmasse', self.server_directory, '--verbose', '--import', '--input', yaml_path,
            '--missing-wait-time', _missing_wait_time,
        ]

        environment = self._get_isolated_environment()

        result = subprocess.run(
            command, env=environment, capture_output=True, text=True, check=False, timeout=_enmasse_timeout)

        if result.returncode != 0:
            raise Exception(f'enmasse --import failed:\nstdout: {result.stdout}\nstderr: {result.stderr}')

# ################################################################################################################################

    def stop_server_process(self, timeout:'float') -> 'None':
        """ Stops the server process alone and waits until the command it runs under exits on its own.
        """
        server_pid = self.get_server_pid()
        server = psutil.Process(server_pid)
        server.terminate()

        _ = server.wait(timeout)
        _ = self.server_process.wait(timeout)

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Stops the server and Redis and removes the environment.
        """
        if self.server_process:
            kill_server_process(self.server_process, _process_kill_timeout, server_directory=self.server_directory)
            self.server_process = None

        if self.redis_process:
            self.redis_process.terminate()
            _ = self.redis_process.wait(_process_kill_timeout)
            self.redis_process = None

        if self.temp_directory:
            shutil.rmtree(self.temp_directory, ignore_errors=True)
            self.temp_directory = ''

# ################################################################################################################################
# ################################################################################################################################
