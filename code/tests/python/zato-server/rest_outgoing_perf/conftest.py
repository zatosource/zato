# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import atexit
import base64
import os
import secrets
import subprocess
import sys
import tempfile

# The services of the suite, which the server deploys from its pickup directory
sys.path.insert(0, os.path.dirname(__file__))

# psutil
import psutil

# pytest
import pytest

# Zato
from _services import invoke_service_source
from request_driver import build_go_program, ModuleCtx as DriverCtx
from zato.common.test.client import AdminClient
from zato.common.test.conftest_base_pubsub import create_zato_server_fixture, get_server_pids, import_into_running_server, \
    render_template

# ################################################################################################################################
# ################################################################################################################################

if 0:
    import logging
    from zato.common.test.conftest_base_pubsub import SessionState
    from zato.common.typing_ import anydict, strdict

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:
    Logger_Name = 'zato.test.rest_outgoing_perf.conftest'

    # The security definition, the outgoing connections and the channels, imported once the services are deployed
    Template_Path = os.path.join(os.path.dirname(__file__), '_enmasse_template.yaml')

    Services_File_Name = '_test_perf_outgoing.py'

    # The length of the generated password, in bytes
    Secret_Bytes = 16

    # How long the target endpoint is given to stop, in seconds
    Stop_Timeout = 5

# ################################################################################################################################
# ################################################################################################################################

# The files of the session, which the session removes when it ends
_data_dir = tempfile.mkdtemp(prefix='zato_rest_outgoing_perf_')

# The credentials of the security definition of the outgoing connections, which the target endpoint expects
_credentials:'strdict' = {
    'basic_username': 'test.perf.outgoing.basic',
    'basic_password': secrets.token_hex(ModuleCtx.Secret_Bytes),
}

# What the tests know of the server once it runs
_server_info:'anydict' = {}

# ################################################################################################################################
# ################################################################################################################################

def _stop_target(process:'subprocess.Popen[str]') -> 'None':
    process.terminate()
    _ = process.wait(ModuleCtx.Stop_Timeout)

# ################################################################################################################################

def _start_target() -> 'int':
    """ Starts the target endpoint of the outgoing connections and returns its plain HTTP port.
    """
    target_server = build_go_program(DriverCtx.Target_Server, _data_dir)

    credentials = f'{_credentials["basic_username"]}:{_credentials["basic_password"]}'.encode('utf-8')
    basic_authorization = 'Basic ' + base64.b64encode(credentials).decode('ascii')

    command = [
        target_server,
        '-mode', 'server',
        '-cert-dir', _data_dir,
        '-basic-authorization', basic_authorization,
    ]

    process = subprocess.Popen(command, stdout=subprocess.PIPE, text=True)
    _ = atexit.register(_stop_target, process)

    stdout = process.stdout
    assert stdout is not None

    # The endpoint prints its plain HTTP and HTTPS ports once it listens
    ready_line = stdout.readline().split()

    out = int(ready_line[1])
    return out

# ################################################################################################################################

def _build_config(
    state:'SessionState',
    logger:'logging.Logger',
    zato_bin:'str',
    server_port:'int',
    invoke_password:'str',
    ) -> 'anydict':
    """ Starts the target endpoint, and returns the services to deploy and what imports the connections
    and channels once the server runs.
    """
    state.test_data_directory = _data_dir

    placeholders = dict(_credentials)
    placeholders['target_port'] = _start_target()

    services_path = os.path.join(_data_dir, ModuleCtx.Services_File_Name)

    with open(services_path, 'w') as services_file:
        _ = services_file.write(invoke_service_source)

    def _populate(
        host:'str',
        server_port:'int',
        invoke_password:'str',
        server_directory:'str',
        zato_bin:'str',
        ) -> 'None':

        yaml_text = render_template(ModuleCtx.Template_Path, placeholders)
        import_into_running_server(zato_bin, server_directory, yaml_text, _data_dir)

        processes:'list[psutil.Process]' = []

        for pid in get_server_pids(state):
            processes.append(psutil.Process(pid))

        _server_info['host'] = host
        _server_info['port'] = server_port
        _server_info['password'] = invoke_password
        _server_info['database'] = state.pubsub_database
        _server_info['processes'] = processes

    out:'anydict' = {
        'placeholders': {},
        'populate_callback': _populate,
        'hot_deploy_sources': [services_path],
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

zato_server_process = create_zato_server_fixture(
    logger_name=ModuleCtx.Logger_Name,
    server_log_copy_name='server-logs-rest-outgoing-perf.txt',
    template_path='',
    quickstart_prefix='zato_rest_outgoing_perf_qs_',
    extra_server_env={},
    patch_server_conf_bind=True,
    build_config_callback=_build_config,
    log_to_files=False,
)

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def zato_server(zato_server_process:'None') -> 'anydict':
    """ Returns the address, the password, the database and the processes of the server of the session.
    """
    out = dict(_server_info)
    return out

# ################################################################################################################################

@pytest.fixture(scope='session')
def zato_client(zato_server:'anydict') -> 'AdminClient':
    """ Returns the client of the services of the server of the session.
    """
    base_url = f'http://{zato_server["host"]}:{zato_server["port"]}'

    out = AdminClient(base_url, zato_server['password'])
    return out

# ################################################################################################################################

@pytest.fixture(scope='session')
def load_client() -> 'str':
    """ Returns the path of the load client, compiled for the session.
    """
    out = build_go_program(DriverCtx.Load_Client, _data_dir)
    return out

# ################################################################################################################################

@pytest.fixture(scope='session')
def data_dir() -> 'str':
    """ Returns the directory of the files of the session.
    """
    out = _data_dir
    return out

# ################################################################################################################################
# ################################################################################################################################
