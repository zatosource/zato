# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import atexit
import os
import shutil
import socket
import subprocess
import threading
import time
from http.client import OK
from urllib.request import Request, urlopen

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.test.client import AdminClient
from zato.common.test.process_util import kill_process_tree
from zato.common.typing_ import cast_
from zato.common.util.config import get_config_object, update_config_file

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strstrdict

# ################################################################################################################################
# ################################################################################################################################

environment_list = list['ZatoEnvironment']

# ################################################################################################################################
# ################################################################################################################################

_zato_base_dir = os.environ['ZATO_TEST_BASE_DIR']
_zato_bin      = os.path.join(_zato_base_dir, 'code', 'bin', 'zato')
_zato_python   = os.path.join(_zato_base_dir, 'code', 'bin', 'python')

# The file-transfer listener that watches the pickup directory, which is what deploys a service
# written after the server has already started
_listener_path = os.path.join(
    _zato_base_dir, 'code', 'zato-common', 'src', 'zato', 'common', 'file_transfer', 'listener.py')

# Every environment binds its server here
Host = '127.0.0.1'

# The variable the server reads the path of its audit database from
_Audit_DB_Variable = 'Zato_Audit_Log_DB_Name'

_server_ready_timeout    = 60
_hot_deploy_timeout      = 30
_listener_settle_seconds = 2
_quickstart_timeout      = 120
_import_timeout          = 120

# How long enmasse waits for an object a definition refers to but has not seen yet
_missing_wait_time = '15'

# Every environment this process started, so the atexit handler can end what a killed run left behind
_environments:'environment_list' = []

# ################################################################################################################################
# ################################################################################################################################

def find_free_port() -> 'int':
    """ Asks the operating system for a port nothing is listening on.
    """
    temporary_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    temporary_socket.bind((Host, 0))

    _, port = temporary_socket.getsockname()
    temporary_socket.close()

    out = port
    return out

# ################################################################################################################################

def _wait_for_server(port:'int') -> 'None':
    """ Polls the server's ping endpoint until it answers.
    """
    url = f'http://{Host}:{port}/zato/ping'
    deadline = time.monotonic() + _server_ready_timeout

    while time.monotonic() < deadline:

        try:
            request = Request(url, method='GET')
            with urlopen(request, timeout=5) as response:
                if response.status == OK:
                    return
        except Exception:

            # A server that is still starting refuses the connection, which is not yet a failure
            pass

        time.sleep(0.5)

    raise Exception(f'The server at {Host}:{port} did not answer within {_server_ready_timeout}s')

# ################################################################################################################################

def _subprocess_environment() -> 'strstrdict':
    """ The environment a process of ours starts with - coverage tracking of a subprocess would write
    into the run's own data file, which nothing here reads.
    """
    out = dict(os.environ)
    _ = out.pop('COVERAGE_PROCESS_START', None)

    return out

# ################################################################################################################################

def _stop_all() -> 'None':
    """ Ends every environment one process started, whether the run ended well or not.
    """
    for environment in list(_environments):
        environment.stop()

_ = atexit.register(_stop_all)

# ################################################################################################################################
# ################################################################################################################################

class ZatoEnvironment:
    """ A throwaway quickstart environment - one server on ports nothing else uses, the listener that
    hot-deploys services written after the start, and enmasse for everything a test creates.
    """

    def __init__(self, directory:'str', *, password_prefix:'str') -> 'None':

        # Where everything of this environment goes, removed on stop
        self.directory = directory

        self.environment_directory = os.path.join(directory, 'env')
        self.server_directory = os.path.join(self.environment_directory, 'server1')
        self.pickup_directory = os.path.join(self.server_directory, 'pickup', 'incoming', 'services')

        # Where the server writes its audit trail, which a test reads back what was received and delivered from
        self.audit_db_path = os.path.join(directory, 'audit.db')

        self.password = password_prefix + '.' + CryptoManager.generate_hex_string()

        self.server_port = find_free_port()

        # Where the server's own MLLP listener sits - settled on here so that whatever fronts it
        # can name the port before the server has started
        self.mllp_internal_port = find_free_port()

        self._server_process:'any_' = None
        self._listener_process:'any_' = None

        # Every path the listener reported as deployed, filled by the thread draining its output
        self._deployed_paths:'set[str]' = set()
        self._deployed_condition = threading.Condition()

        _environments.append(self)

# ################################################################################################################################

    def create(self, *, needs_scheduler:'bool'=False) -> 'None':
        """ Lays the environment down with quickstart - into a directory of its own, because quickstart
        refuses to write into one that already holds anything. Without needs_scheduler the scheduler component is left out.
        """
        os.makedirs(self.environment_directory)

        command = [
            _zato_bin, 'quickstart', 'create', self.environment_directory,
            '--servers', '1',
            '--password', self.password,
            '--server-api-client-for-scheduler-password', self.password,
        ]

        if not needs_scheduler:
            command.append('--no-scheduler')

        result = subprocess.run(
            command, capture_output=True, text=True, timeout=_quickstart_timeout, env=_subprocess_environment())

        if result.returncode != 0:
            raise Exception(f'quickstart create failed:\nstdout: {result.stdout}\nstderr: {result.stderr}')

        self._set_server_port()

# ################################################################################################################################

    def _set_server_port(self) -> 'None':
        """ Points the server at its port. The bind address is set along with it because the check
        that runs before the server starts reads that one.
        """
        repository_location = os.path.join(self.server_directory, 'config', 'repo')

        config = get_config_object(repository_location, 'server.conf')
        config = cast_('any_', config)

        main_config = config['main']
        main_config['port'] = str(self.server_port)
        main_config['bind'] = f'{Host}:{self.server_port}'

        update_config_file(config, repository_location, 'server.conf')

# ################################################################################################################################

    def _stream_output(self, process:'any_', label:'str') -> 'None':
        """ Drains what a process writes so a full pipe never blocks it, and puts every line where a
        failing run can be read back from.
        """
        for line in iter(process.stdout.readline, b''):
            text = line.decode('utf8', errors='replace').rstrip()
            print(f'[{label}] {text}')

            # The listener prints this once the server confirmed a file, which is what a deploy waits on
            if 'Deployed -> ' in text:
                deployed_path = text.split('Deployed -> ')[1]
                with self._deployed_condition:
                    self._deployed_paths.add(deployed_path)
                    self._deployed_condition.notify_all()

# ################################################################################################################################

    def _start_process(self, command:'list[str]', environment:'strstrdict', label:'str') -> 'any_':
        """ Starts one of our processes in a session of its own, so the teardown can end the whole
        group - a shell wrapper and whatever it launched included - and drains its output.
        """
        process = subprocess.Popen(
            command,
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )

        output_thread = threading.Thread(target=self._stream_output, args=(process, label), daemon=True)
        output_thread.start()

        out = process
        return out

# ################################################################################################################################

    def start(self, extra_environment:'strstrdict') -> 'None':
        """ Starts the server in the foreground with the MLLP listener on the internal port, waits for it and starts
        the pickup listener. The extra environment is what the hot-deployed services read at import time.
        """
        environment = _subprocess_environment()
        environment['Zato_Config_Bind_Port'] = str(self.server_port)
        environment['Zato_Broker_HTTP_Port'] = str(find_free_port())
        environment['Zato_HL7_MLLP_Port'] = str(self.mllp_internal_port)
        environment[_Audit_DB_Variable] = self.audit_db_path
        environment.update(extra_environment)

        self._server_process = self._start_process(
            [_zato_bin, 'start', self.server_directory, '--fg'], environment, 'SERVER')

        # A detached watchdog ends the group once this process is gone - a pytest run killed outright
        # never reaches the cleanup, and a server left behind would go on running and logging
        watchdog_script = (
            f'while kill -0 {os.getpid()} 2>/dev/null; do sleep 5; done; '
            f'kill -- -{self._server_process.pid} 2>/dev/null'
        )
        _ = subprocess.Popen(['/bin/sh', '-c', watchdog_script], start_new_session=True)

        _wait_for_server(self.server_port)

        self._start_listener()

# ################################################################################################################################

    def _start_listener(self) -> 'None':
        """ Starts the file-transfer listener on the pickup directory. The server's own scan only covers
        what was there when it started, so a service written now needs it.
        """
        os.makedirs(self.pickup_directory, exist_ok=True)

        environment = _subprocess_environment()
        environment['Zato_Config_Bind_Port'] = str(self.server_port)
        environment['Zato_Web_Admin_Repo_Dir'] = os.path.join(self.environment_directory, 'web-admin', 'config', 'repo')

        self._listener_process = self._start_process(
            [_zato_python, _listener_path, self.pickup_directory], environment, 'LISTENER')

        # The listener needs a moment to set its directory watch up before a file written lands in it
        time.sleep(_listener_settle_seconds)

# ################################################################################################################################

    def deploy(self, file_name:'str', source:'str') -> 'None':
        """ Writes one module of services into the pickup directory and waits for the server to confirm it.
        """
        file_path = os.path.join(self.pickup_directory, file_name)

        with open(file_path, 'w') as file_handle:
            _ = file_handle.write(source)

        def _is_deployed() -> 'bool':
            out = file_path in self._deployed_paths
            return out

        with self._deployed_condition:
            is_deployed = self._deployed_condition.wait_for(_is_deployed, timeout=_hot_deploy_timeout)

        if not is_deployed:
            raise Exception(f'The listener did not deploy {file_path} within {_hot_deploy_timeout}s')

        print(f'[DEPLOY] Deployed {file_path}')

# ################################################################################################################################

    def import_yaml(self, file_name:'str', definitions:'str') -> 'str':
        """ Creates what a YAML file describes by importing it the way a user does. Returns the path of
        the file imported, which a failing run is read from.
        """
        input_path = os.path.join(self.directory, file_name)

        with open(input_path, 'w') as input_file:
            _ = input_file.write(definitions)

        command = [
            _zato_bin, 'enmasse', self.server_directory,
            '--verbose',
            '--import',
            '--input', input_path,
            '--missing-wait-time', _missing_wait_time,
        ]

        result = subprocess.run(command, capture_output=True, text=True, timeout=_import_timeout)

        if result.returncode != 0:
            raise Exception(f'enmasse import failed:\nstdout: {result.stdout}\nstderr: {result.stderr}')

        print(f'[ENMASSE] Imported {input_path}')

        out = input_path
        return out

# ################################################################################################################################

    def client(self) -> 'AdminClient':
        """ A client invoking services on the server with the environment's own password.
        """
        out = AdminClient(f'http://{Host}:{self.server_port}', self.password)
        return out

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Ends the processes in the reverse of the order they started in and removes the directory.
        """
        if self in _environments:
            _environments.remove(self)

        # The listener goes before the server so that it does not race the server's shutdown
        kill_process_tree(self._listener_process)
        self._listener_process = None

        kill_process_tree(self._server_process)
        self._server_process = None

        if os.path.isdir(self.directory):
            shutil.rmtree(self.directory, ignore_errors=True)

# ################################################################################################################################
# ################################################################################################################################
