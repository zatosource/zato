# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import subprocess
import sys
import tempfile
import time
from random import randint
from urllib.request import urlopen

sys.path.insert(0, os.path.dirname(__file__))

# pytest
import pytest

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.test.client import AdminClient
from zato.common.test.conftest_base_pubsub import create_zato_server_fixture
from zato.common.test.file_transfer_harness.evidence import build_test_services_source
from zato.common.test.file_transfer_harness.sftp_adapter import Key_Env_Name, SFTPAdapter
from zato.common.test.file_transfer_harness.smb_adapter import SMBAdapter
from zato.common.util.tcp import get_free_port

# Local test helpers
from _config import TestConfig

# ################################################################################################################################
# ################################################################################################################################

if 0:
    import logging
    from zato.common.test.conftest_base_pubsub import SessionState
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

# The SFTP client key's path must be known before the Zato server starts because the server receives it
# through an environment variable, while the key itself is written out only once the test SSH server runs.
_key_directory = tempfile.mkdtemp(prefix='zato_file_transfer_key_')
_key_path = os.path.join(_key_directory, 'client-key')

# This suite runs its own private scheduler - the stream prefix keeps its Redis streams away
# from any other environment sharing the same Redis, and the HTTP port is a random free one
# so that parallel test runs and the user's own scheduler never clash on the default port.
# The port search starts at a random offset in a high range, away from the range that test servers
# allocate from, because the port is probed now but bound only once the scheduler starts.
_scheduler_stream_prefix = 'zato:scheduler:test-file-transfer-' + CryptoManager.generate_hex_string(32)
_scheduler_http_port = get_free_port(randint(41000, 51000))

# How long to wait for the scheduler's HTTP API to come up, in seconds
_scheduler_start_timeout = 30

# How long to sleep between two attempts at the scheduler's HTTP API, in seconds
_scheduler_start_sleep_time = 0.5

# Where the scheduler this suite runs writes its log
_scheduler_log_path = '/tmp/zato-file-transfer-test-scheduler.log'

# ################################################################################################################################
# ################################################################################################################################

def _build_config(
    state:'SessionState',
    logger:'logging.Logger',
    zato_bin:'str',
    server_port:'int',
    invoke_password:'str',
) -> 'anydict':

    # A directory for the evidence file and the generated source code of the test services
    work_directory = tempfile.mkdtemp(prefix='zato_file_transfer_work_')

    evidence_file = os.path.join(work_directory, 'file-transfer-items.jsonl')
    TestConfig.evidence_file = evidence_file

    # Render the test services with the evidence file path embedded ..
    source = build_test_services_source(evidence_file)

    # .. and write them out for the fixture to copy into the server's pickup directory.
    source_path = os.path.join(work_directory, 'file_transfer_scheduler_test_services.py')

    with open(source_path, 'w') as source_file:
        _ = source_file.write(source)

    def _populate(
        host:'str',
        server_port:'int',
        invoke_password:'str',
        server_directory:'str',
        zato_bin:'str',
    ) -> 'None':
        TestConfig.host = host
        TestConfig.server_port = server_port
        TestConfig.invoke_password = invoke_password
        TestConfig.server_directory = server_directory

    out:'anydict' = {
        'placeholders': {},
        'populate_callback': _populate,
        'hot_deploy_sources': [source_path],
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

# One Zato server serves every protocol's tests - starting a quickstart environment is by far
# the most expensive thing this suite does, so it happens exactly once.
zato_server = create_zato_server_fixture(
    logger_name='zato.test.file_transfer_scheduler.conftest',
    server_log_copy_name='server-logs-file-transfer-scheduler.txt',
    template_path='',
    quickstart_prefix='zato_file_transfer_qs_',
    extra_server_env={
        Key_Env_Name: _key_path,

        # The server must talk to this suite's private scheduler, not to any other one
        'Zato_Scheduler_Stream_Prefix': _scheduler_stream_prefix,
        'Zato_Scheduler_HTTP_Port': str(_scheduler_http_port),
    },
    patch_server_conf_bind=True,
    build_config_callback=_build_config,
)

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def admin_client(zato_server:'any_') -> 'AdminClient':
    """ Talks to the one server that every protocol's tests share.
    """
    base_url = f'http://{TestConfig.host}:{TestConfig.server_port}'

    out = AdminClient(base_url, TestConfig.invoke_password)
    return out

# ################################################################################################################################

@pytest.fixture(scope='session')
def evidence_file(zato_server:'any_') -> 'str':
    """ The file that the hot-deployed test services record each received file in.
    """
    out = TestConfig.evidence_file
    return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def sftp_adapter() -> 'any_':
    """ The SFTP protocol under test, with its own SSH server.
    """
    adapter = SFTPAdapter(_key_path)
    adapter.start_server()

    yield adapter

    adapter.stop_server()

# ################################################################################################################################

@pytest.fixture(scope='session')
def smb_adapter() -> 'any_':
    """ The SMB protocol under test, with its own SMB server.
    """
    adapter = SMBAdapter()
    adapter.start_server()

    yield adapter

    adapter.stop_server()

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def scheduler_process(zato_server:'any_') -> 'any_':
    """ Starts this suite's own private scheduler for tests that need real fire events. Its stream prefix
    and HTTP port are unique to this run, so it never interferes with any other scheduler - be it
    the user's own one or one belonging to another test suite running in parallel.
    It depends on the server fixture so that it starts only after quickstart wiped the Redis keys.
    """
    zato_base = os.environ['ZATO_TEST_BASE_DIR']
    binary = os.path.join(zato_base, 'code', 'zato-rust', 'zato_scheduler_core', 'target', 'release', '_zato_scheduler')

    environment = os.environ.copy()
    _ = environment.setdefault('Zato_Scheduler_Redis_Host', 'localhost')
    _ = environment.setdefault('Zato_Scheduler_Redis_Port', '6379')
    _ = environment.setdefault('Zato_Scheduler_Redis_Password', '')
    _ = environment.setdefault('Zato_Scheduler_Log_Level', 'info')

    # The private stream prefix and HTTP port - the same ones the server under test received
    environment['Zato_Scheduler_Stream_Prefix'] = _scheduler_stream_prefix
    environment['Zato_Scheduler_HTTP_Port'] = str(_scheduler_http_port)

    log_file = open(_scheduler_log_path, 'w')

    process = subprocess.Popen([binary], env=environment, stdout=log_file, stderr=subprocess.STDOUT)

    # Wait until the scheduler's HTTP API is up, which means it is also consuming its command stream
    deadline = time.monotonic() + _scheduler_start_timeout
    metrics_url = f'http://127.0.0.1:{_scheduler_http_port}/metrics'

    while time.monotonic() < deadline:
        try:
            with urlopen(metrics_url, timeout=1) as response:
                _ = response.read()
        except Exception:
            time.sleep(_scheduler_start_sleep_time)
            continue
        else:
            break

    yield process

    process.kill()
    _ = process.wait()
    log_file.close()

# ################################################################################################################################
# ################################################################################################################################
