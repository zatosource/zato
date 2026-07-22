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
from uuid import uuid4

sys.path.insert(0, os.path.dirname(__file__))

# pytest
import pytest

# Zato
from zato.common.test.conftest_base_pubsub import create_zato_server_fixture
from zato.common.test.smb_ import SMBTestServer
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

# This suite runs its own private scheduler - the stream prefix keeps its Redis streams away
# from any other environment sharing the same Redis, and the HTTP port is a random free one
# so that parallel test runs and the user's own scheduler never clash on the default port.
# The port search starts at a random offset in a high range, away from the range that test servers
# allocate from, because the port is probed now but bound only once the scheduler starts.
_scheduler_stream_prefix = 'zato:scheduler:test-file-transfer-smb-' + uuid4().hex[:8]
_scheduler_http_port = get_free_port(randint(41000, 51000))

# ################################################################################################################################
# ################################################################################################################################

# Source code of the services that the schedules under test invoke. The first one records each file
# it receives in the evidence file, the second one always raises so that tests can confirm
# that files are left in place when the target service fails.
_test_services_template = '''# -*- coding: utf-8 -*-

# stdlib
from json import dumps

# Zato
from zato.server.service import Service

_evidence_file = '{evidence_file}'

class StoreFileTransferItem(Service):
    """ Records each file received on input.
    """
    name = '{service_store_file}'

    def handle(self):

        # The dispatch service hands us the item object itself
        item = self.request.raw_request

        data = item.data
        if isinstance(data, bytes):
            data = data.decode('utf-8')

        line = dumps({{
            'conn_type': item.conn_type,
            'conn_name': item.conn_name,
            'schedule_name': item.schedule_name,
            'directory': item.directory,
            'file_name': item.file_name,
            'full_path': item.full_path,
            'size': item.size,
            'data': data,
        }})

        with open(_evidence_file, 'a') as evidence:
            _ = evidence.write(line + '\\n')

class AlwaysRaiseFileTransfer(Service):
    """ Fails on purpose so that tests can confirm that files are never lost on errors.
    """
    name = '{service_always_raise}'

    def handle(self):
        raise Exception('This service always raises an error for file transfer tests')
'''

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
    work_directory = tempfile.mkdtemp(prefix='zato_file_transfer_smb_work_')

    evidence_file = os.path.join(work_directory, 'file-transfer-items.jsonl')
    TestConfig.evidence_file = evidence_file

    # Render the test services with the evidence file path embedded ..
    source = _test_services_template.format(
        evidence_file=evidence_file,
        service_store_file=TestConfig.service_store_file,
        service_always_raise=TestConfig.service_always_raise,
    )

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

zato_server = create_zato_server_fixture(
    logger_name='zato.test.file_transfer_scheduler_smb.conftest',
    server_log_copy_name='server-logs-file-transfer-scheduler-smb.txt',
    template_path='',
    quickstart_prefix='zato_file_transfer_smb_qs_',
    extra_server_env={

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
def smb_test_server() -> 'any_':
    server = SMBTestServer()
    server.start()
    yield server
    server.stop()

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
    environment.setdefault('Zato_Scheduler_Redis_Host', 'localhost')
    environment.setdefault('Zato_Scheduler_Redis_Port', '6379')
    environment.setdefault('Zato_Scheduler_Redis_Password', '')
    environment.setdefault('Zato_Scheduler_Log_Level', 'info')

    # The private stream prefix and HTTP port - the same ones the server under test received
    environment['Zato_Scheduler_Stream_Prefix'] = _scheduler_stream_prefix
    environment['Zato_Scheduler_HTTP_Port'] = str(_scheduler_http_port)

    log_file = open('/tmp/zato-file-transfer-smb-test-scheduler.log', 'w')

    process = subprocess.Popen([binary], env=environment, stdout=log_file, stderr=subprocess.STDOUT)

    # Wait until the scheduler's HTTP API is up, which means it is also consuming its command stream
    deadline = time.monotonic() + 30

    while time.monotonic() < deadline:
        try:
            with urlopen(f'http://127.0.0.1:{_scheduler_http_port}/metrics', timeout=1) as response:
                _ = response.read()
        except Exception:
            time.sleep(0.5)
            continue
        else:
            break

    yield process

    process.kill()
    _ = process.wait()
    log_file.close()

# ################################################################################################################################
# ################################################################################################################################
