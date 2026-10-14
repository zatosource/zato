# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# One quickstart server of this suite's own, with a private scheduler, its own audit log and pub/sub databases,
# the file pickup listener that deploys what lands in its pickup directory, and the file transfer demo rooted
# in the suite's own directory, so nothing of any other environment is touched. Only processes this suite
# started are ever stopped.

# stdlib
import logging
import os
import re
import shutil
import subprocess
import threading
import time
from random import randint
from urllib.request import urlopen

# pytest
import pytest

# Zato
from zato.common.api import PubSub
from zato.common.audit_log.api import ModuleCtx as AuditLogCtx
from zato.common.crypto.api import CryptoManager
from zato.common.sftp_local import LocalSFTPServer
from zato.common.test import kill_server_process
from zato.common.test.client import AdminClient
from zato.common.test.conftest_base_pubsub import find_free_port, run_quickstart_and_enmasse, SessionState, wait_for_server
from zato.common.test.process_util import kill_process_tree
from zato.common.util.local_server import read_pid_file, stop_pid
from zato.common.util.tcp import get_free_port
from zato.server.demo_file_transfer.common import get_paths, Root_Env_Name

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.demo_file_transfer.conftest')

# ################################################################################################################################
# ################################################################################################################################

# The private scheduler's Redis streams and HTTP port belong to this run only. The port search starts
# at a random offset in a high range, away from the range that test servers allocate from.
_scheduler_stream_prefix = 'zato:scheduler:test-demo-file-transfer-' + CryptoManager.generate_hex_string(32)
_scheduler_http_port = get_free_port(randint(41000, 51000))

# How long to wait for the scheduler's HTTP API to come up, in seconds
_scheduler_start_timeout = 30

# How long to sleep between two attempts at the scheduler's HTTP API, in seconds
_scheduler_start_sleep_time = 0.5

# Where the scheduler, the server and the file pickup listener of this suite write their output
_scheduler_log_path = '/tmp/zato-demo-file-transfer-test-scheduler.log'
_server_log_path = '/tmp/zato-demo-file-transfer-test-server.log'
_listener_log_path = '/tmp/zato-demo-file-transfer-test-listener.log'

# What the file pickup listener prints once its watch is in place - a file written to the pickup directory
# before that produces no event at all, so the demo's services would never be deployed
_listener_ready_marker = 'Watching for changes'

# How long the file pickup listener may take to start watching, in seconds
_listener_ready_timeout = 30

# How long a process may take to go away, in seconds
_kill_timeout = 5

# ################################################################################################################################
# ################################################################################################################################

def _start_scheduler() -> 'subprocess.Popen[bytes]':
    """ Starts this suite's private scheduler and waits until its HTTP API is up.
    """
    zato_base = os.environ['ZATO_TEST_BASE_DIR']
    binary = os.path.join(zato_base, 'code', 'zato-rust', 'zato_scheduler_core', 'target', 'release', '_zato_scheduler')

    environment = os.environ.copy()
    _ = environment.setdefault('Zato_Scheduler_Redis_Host', 'localhost')
    _ = environment.setdefault('Zato_Scheduler_Redis_Port', '6379')
    _ = environment.setdefault('Zato_Scheduler_Redis_Password', '')
    _ = environment.setdefault('Zato_Scheduler_Log_Level', 'info')

    environment['Zato_Scheduler_Stream_Prefix'] = _scheduler_stream_prefix
    environment['Zato_Scheduler_HTTP_Port'] = str(_scheduler_http_port)

    with open(_scheduler_log_path, 'w') as log_file:
        out = subprocess.Popen([binary], env=environment, stdout=log_file, stderr=subprocess.STDOUT)

    deadline = time.monotonic() + _scheduler_start_timeout
    metrics_url = f'http://127.0.0.1:{_scheduler_http_port}/metrics'

    while time.monotonic() < deadline:
        try:
            with urlopen(metrics_url, timeout=1) as response:
                _ = response.read()
        except Exception:
            time.sleep(_scheduler_start_sleep_time)
        else:
            break

    return out

# ################################################################################################################################

def _patch_server_conf(server_directory:'str', server_port:'int') -> 'None':
    """ Points the server at the test Redis database and makes it bind to its own port.
    """
    server_conf_path = os.path.join(server_directory, 'config', 'repo', 'server.conf')

    with open(server_conf_path) as server_conf_file:
        data = server_conf_file.read()

    data = re.sub(r'^(db\s*=\s*)\d+', f'\\g<1>{PubSub.Test_Redis_DB}', data, flags=re.MULTILINE)
    data = re.sub(r'^(bind\s*=\s*)\S+', f'\\g<1>127.0.0.1:{server_port}', data, flags=re.MULTILINE)

    with open(server_conf_path, 'w') as server_conf_file:
        _ = server_conf_file.write(data)

# ################################################################################################################################

def _start_server(zato_bin:'str', server_directory:'str', server_port:'int', environment:'stranydict') -> 'any_':
    """ Starts the server in the foreground with its output copied to a log file.
    """
    process = subprocess.Popen(
        [zato_bin, 'start', server_directory, '--fg'],
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    def _copy_output() -> 'None':
        stdout = process.stdout
        assert stdout is not None

        with open(_server_log_path, 'w') as log_file:
            for line in iter(stdout.readline, b''):
                text = line.decode('utf8', errors='replace')
                _ = log_file.write(text)
                log_file.flush()

    thread = threading.Thread(target=_copy_output, daemon=True)
    thread.start()

    return process

# ################################################################################################################################

def _start_listener(quickstart_directory:'str', server_directory:'str', server_port:'int') -> 'any_':
    """ Starts the file pickup listener the way an environment runs it and waits until it watches the pickup directory.
    """
    zato_base = os.environ['ZATO_TEST_BASE_DIR']

    environment = os.environ.copy()
    _ = environment.pop('COVERAGE_PROCESS_START', None)

    environment['Zato_Config_Bind_Port'] = str(server_port)
    environment['Zato_Web_Admin_Repo_Dir'] = os.path.join(quickstart_directory, 'web-admin', 'config', 'repo')
    environment['Zato_Server_Dir'] = server_directory

    process = subprocess.Popen(
        ['make', 'listener'],
        cwd=zato_base,
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )

    is_ready = threading.Event()

    def _copy_output() -> 'None':
        stdout = process.stdout
        assert stdout is not None

        with open(_listener_log_path, 'w') as log_file:
            for line in iter(stdout.readline, b''):
                text = line.decode('utf8', errors='replace')
                _ = log_file.write(text)
                log_file.flush()

                if _listener_ready_marker in text:
                    is_ready.set()

    thread = threading.Thread(target=_copy_output, daemon=True)
    thread.start()

    if not is_ready.wait(_listener_ready_timeout):
        kill_process_tree(process)
        raise Exception(f'File pickup listener was not watching within {_listener_ready_timeout}s, see {_listener_log_path}')

    return process

# ################################################################################################################################

def _stop_demo_processes() -> 'None':
    """ Stops the demo's SSH server and demo server if they are still there, recognized by their configuration paths,
    which are under this suite's own directory.
    """
    paths = get_paths()

    sftp_server = LocalSFTPServer(paths.sshd_dir, 0)
    sftp_server.stop_process()

    server_pid = read_pid_file(paths.server_pid)
    _ = stop_pid(server_pid, paths.server_config)

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def zato_server() -> 'any_':
    """ A quickstart server with the file transfer demo rooted in this suite's own directory.
    """
    zato_base = os.environ['ZATO_TEST_BASE_DIR']
    zato_bin = os.path.join(zato_base, 'code', 'bin', 'zato')

    invoke_password = 'test.invoke.' + CryptoManager.generate_hex_string()
    server_port = find_free_port()

    # The state object only remembers the quickstart directory - its own cleanup is never called,
    # because it stops every Zato server on the machine rather than only this suite's one.
    state = SessionState(logger.name, 'server-logs-demo-file-transfer.txt')

    server_directory = run_quickstart_and_enmasse(
        state=state,
        logger=logger,
        zato_bin=zato_bin,
        invoke_password=invoke_password,
        rendered_yaml='',
        quickstart_prefix='zato_demo_file_transfer_qs_',
    )

    quickstart_directory = state.quickstart_directory
    assert quickstart_directory is not None

    # Everything of the demo lives under this suite's directory, which the tests too need to know ..
    demo_root = os.path.join(quickstart_directory, 'demo-file-transfer')
    os.environ[Root_Env_Name] = demo_root

    # .. and so does the audit log database the tests read the transfers from.
    audit_db_path = os.path.join(quickstart_directory, 'audit.db')
    pubsub_db_path = os.path.join(quickstart_directory, 'pubsub.db')

    _patch_server_conf(server_directory, server_port)

    environment = os.environ.copy()
    _ = environment.pop('COVERAGE_PROCESS_START', None)

    environment['Zato_Config_Bind_Port'] = str(server_port)
    environment['Zato_Broker_HTTP_Port'] = str(find_free_port())
    environment['Zato_Scheduler_Stream_Prefix'] = _scheduler_stream_prefix
    environment['Zato_Scheduler_HTTP_Port'] = str(_scheduler_http_port)
    environment['Zato_Audit_Log_DB_Type'] = AuditLogCtx.Type_SQLite
    environment['Zato_Audit_Log_DB_Name'] = audit_db_path
    environment['Zato_PubSub_DB_Name'] = pubsub_db_path

    server_process = _start_server(zato_bin, server_directory, server_port, environment)
    listener_process = None
    scheduler_process = None

    try:
        wait_for_server(logger, '127.0.0.1', server_port)
        listener_process = _start_listener(quickstart_directory, server_directory, server_port)
        scheduler_process = _start_scheduler()

        base_url = f'http://127.0.0.1:{server_port}'
        client = AdminClient(base_url, invoke_password)

        yield {
            'client': client,
            'server_directory': server_directory,
            'demo_root': demo_root,
            'audit_db_path': audit_db_path,
        }

    finally:

        if scheduler_process:
            scheduler_process.kill()
            _ = scheduler_process.wait()

        kill_process_tree(listener_process)

        kill_server_process(server_process, _kill_timeout, server_directory=server_directory)

        # The server was killed, so it had no chance to stop what it started
        _stop_demo_processes()

        shutil.rmtree(quickstart_directory, ignore_errors=True)
        _ = os.environ.pop(Root_Env_Name, None)

# ################################################################################################################################
# ################################################################################################################################
