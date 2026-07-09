# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time
from http.client import OK
from urllib.error import HTTPError
from urllib.request import Request, urlopen

# pytest
import pytest

# Zato - test utilities
from zato.common.test.client import AdminClient

# Zato - conftest
import conftest

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

# The DEBUG line the fixture service emits through its logger
_debug_marker = 'Refreshed the customer cache, entries: 128'

# The channel created for the per-logger override test
_channel_name     = 'logging-tests.rest-level'
_channel_url_path = '/test/logging/rest-level'

# How long to wait for a newly created channel to answer
_channel_wait_timeout = 30

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='module')
def client(zato_server:'anydict') -> 'AdminClient':
    base_url = f'http://{zato_server["host"]}:{zato_server["server_port"]}'
    out = AdminClient(base_url, zato_server['password'])
    return out

# ################################################################################################################################
# ################################################################################################################################

def _wait_for_channel(url:'str', timeout:'int'=_channel_wait_timeout) -> 'None':
    """ Polls a channel URL until it answers with an OK, or raises after the timeout.
    """
    deadline = time.monotonic() + timeout
    last_error = None

    while time.monotonic() < deadline:
        try:
            request = Request(url, data=b'{}', headers={'Content-Type': 'application/json'}, method='POST')
            with urlopen(request, timeout=5) as response:
                if response.status == OK:
                    return

        except HTTPError as channel_error:
            last_error = channel_error

        time.sleep(0.5)

    raise Exception(f'Channel {url} did not become ready within {timeout}s, last error: {last_error!r}')

# ################################################################################################################################
# ################################################################################################################################

class TestLogLevelEnvOverride:
    """ The server runs with Zato_Log_Level=DEBUG and Zato_Log_Level_REST=WARN,
    so DEBUG lines from services must land in server.log while INFO lines
    from the zato_rest logger must not.
    """

    def test_global_debug_override(self, zato_server:'anydict', client:'AdminClient') -> 'None':

        # Invoke the fixture service that emits a DEBUG line ..
        response = client.invoke('logging-tests.debug-writer')
        assert response['result'] == 'ok'

        # .. the line must land in server.log because Zato_Log_Level=DEBUG
        # .. lowered every logger's level, including the root logger the service logger inherits from.
        contents = conftest.wait_for_log_content(zato_server['server_dir'], 'server.log', _debug_marker)

        # .. and the line must carry the DEBUG level.
        for line in contents.splitlines():
            if _debug_marker in line:
                assert ' - DEBUG - ' in line, f'Expected a DEBUG line, got: {line}'
                break

# ################################################################################################################################

    def test_per_logger_rest_override(self, zato_server:'anydict', client:'AdminClient') -> 'None':

        # Create a plain REST channel whose requests the zato_rest logger would
        # normally describe with an INFO line in server.log ..
        response = client.create('zato.http-soap.create',
            cluster_id=1,
            name=_channel_name,
            is_active=True,
            is_internal=False,
            url_path=_channel_url_path,
            connection='channel',
            transport='plain_http',
            service='logging-tests.debug-writer',
            data_format='json',
            merge_url_params_req=True,
        )
        assert 'id' in response

        # .. wait until the channel answers, proving the request reached the server ..
        host = zato_server['host']
        server_port = zato_server['server_port']
        _wait_for_channel(f'http://{host}:{server_port}{_channel_url_path}')

        # .. the HTTP layer's own access log must confirm the requests were processed ..
        _ = conftest.wait_for_log_content(zato_server['server_dir'], 'access.log', _channel_url_path)

        # .. yet server.log must carry no INFO line from zato_rest for this channel
        # .. because Zato_Log_Level_REST=WARN silenced them, winning over the global DEBUG.
        contents = conftest.read_log_file(zato_server['server_dir'], 'server.log')

        for line in contents.splitlines():
            if 'REST cha' in line:
                assert _channel_url_path not in line, f'Unexpected zato_rest INFO line: {line}'

# ################################################################################################################################
# ################################################################################################################################
