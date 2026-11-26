# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import subprocess
from base64 import b64encode
from http.client import OK
from threading import Event, Thread
from time import monotonic, sleep
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

# PyPI
import pytest

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.test.client import AdminClient

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, intlist, strlist, strnone

# ################################################################################################################################
# ################################################################################################################################

auth_header_list = list['strnone']

# ################################################################################################################################
# ################################################################################################################################

_zato_bin = os.path.join(os.environ['ZATO_TEST_BASE_DIR'], 'code', 'bin', 'zato')

_suffix = CryptoManager.generate_hex_string()

_security_name = f'test.reload.channel.security.{_suffix}'
_group_name    = f'test.reload.channel.group.{_suffix}'
_channel_name  = f'test.reload.channel.{_suffix}'
_url_path      = f'/test/reload/channel/{_suffix}'

_username       = f'test.reload.channel.user.{_suffix}'
_password       = 'test.reload.channel.' + CryptoManager.generate_hex_string()
_wrong_password = 'test.reload.channel.wrong.' + CryptoManager.generate_hex_string()

_enmasse_timeout = 120

# How long a request to the channel may take, and how long the channel has to start answering after the import
_request_timeout = 10
_channel_ready_timeout = 60

# How many configuration reloads the test runs, how long it waits between them,
# and how long the callers keep calling after the last one, since a worker reloads after the invoker returns
_reload_count = 5
_reload_interval = 1.0
_settle_time = 3.0

# The records that the requests without valid credentials cause on the server
_expected_server_records = (
    'Received neither Basic Auth, bearer token nor API key (groups)',
    'Invalid Basic Auth credentials (groups)',
)

_enmasse_template = """
security:
  - name: {security_name}
    type: basic_auth
    username: {username}
    password: "{password}"

groups:
  - name: {group_name}
    members:
      - {security_name}

channel_rest:
  - name: {channel_name}
    service: demo.ping
    url_path: {url_path}
    groups:
      - {group_name}
"""

# ################################################################################################################################
# ################################################################################################################################

class _CallerResults:
    """ What the requests of one caller received while the configuration was being reloaded.
    """
    def __init__(self) -> 'None':
        self.status_codes:'intlist' = []
        self.connection_errors:'strlist' = []

# ################################################################################################################################
# ################################################################################################################################

def _basic_auth_header(username:'str', password:'str') -> 'str':
    credentials = f'{username}:{password}'.encode('utf8')
    encoded = b64encode(credentials).decode('utf8')

    out = 'Basic ' + encoded
    return out

# ################################################################################################################################

def _call_channel(url:'str', auth_header:'strnone') -> 'int':
    """ Invokes the channel and returns the HTTP status code of its response.
    """
    request = Request(url, method='GET')

    if auth_header:
        request.add_header('Authorization', auth_header)

    try:
        with urlopen(request, timeout=_request_timeout) as response:
            _ = response.read()
            out = response.status
    except HTTPError as e:
        _ = e.read()
        out = e.code

    return out

# ################################################################################################################################

def _call_until_stopped(url:'str', auth_headers:'auth_header_list', stop_event:'Event', results:'_CallerResults') -> 'None':
    """ Invokes the channel with each of the Authorization headers in turn until the stop event is set.
    """
    while not stop_event.is_set():
        for auth_header in auth_headers:
            try:
                status_code = _call_channel(url, auth_header)
            except URLError as e:
                results.connection_errors.append(str(e))
            else:
                results.status_codes.append(status_code)

# ################################################################################################################################

def _import_enmasse(server_dir:'str', tmp_dir:'str') -> 'None':
    """ Creates the Basic Auth definition, the security group and the REST channel through enmasse.
    """
    yaml_text = _enmasse_template.format(
        security_name=_security_name,
        username=_username,
        password=_password,
        group_name=_group_name,
        channel_name=_channel_name,
        url_path=_url_path,
    )

    yaml_path = os.path.join(tmp_dir, f'test-reload-channel-security-{_suffix}.yaml')

    with open(yaml_path, 'w') as yaml_file:
        _ = yaml_file.write(yaml_text)

    command = [_zato_bin, 'enmasse', server_dir, '--verbose', '--import', '--input', yaml_path, '--missing-wait-time', '15']
    result = subprocess.run(command, capture_output=True, text=True, timeout=_enmasse_timeout)

    if result.returncode != 0:
        raise Exception(f'enmasse --import failed (exit {result.returncode}):\nstdout: {result.stdout}\nstderr: {result.stderr}')

# ################################################################################################################################

def _wait_for_channel(url:'str', auth_header:'str') -> 'None':
    """ Waits until the worker serves the imported channel to a caller with valid credentials.
    """
    deadline = monotonic() + _channel_ready_timeout

    while monotonic() < deadline:
        status_code = _call_channel(url, auth_header)
        if status_code == OK:
            break
        sleep(0.5)
    else:
        raise Exception(f'Channel {_channel_name} did not respond with {OK} within {_channel_ready_timeout}s')

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='module')
def channel_url(zato_server:'any_') -> 'str':

    # The requests without valid credentials are refused on purpose ..
    for record in _expected_server_records:
        zato_server['expected_server_records'].append(record)

    # .. the objects the test calls are created the way a user creates them ..
    _import_enmasse(zato_server['server_dir'], zato_server['tmpdir'])

    # .. and the channel is called once it is in place.
    out = f'http://{zato_server["host"]}:{zato_server["port"]}{_url_path}'

    valid_auth_header = _basic_auth_header(_username, _password)
    _wait_for_channel(out, valid_auth_header)

    return out

# ################################################################################################################################

@pytest.fixture(scope='module')
def admin_client(zato_server:'any_') -> 'AdminClient':
    base_url = f'http://{zato_server["host"]}:{zato_server["port"]}'

    out = AdminClient(base_url, zato_server['password'])
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_channel_security_holds_during_configuration_reloads(channel_url:'str', admin_client:'AdminClient') -> 'None':

    valid_auth_header = _basic_auth_header(_username, _password)
    wrong_auth_header = _basic_auth_header(_username, _wrong_password)

    stop_event = Event()

    refused_results = _CallerResults()
    accepted_results = _CallerResults()

    # One caller without credentials and with wrong credentials, the other with valid credentials ..
    refused_auth_headers:'auth_header_list' = [None, wrong_auth_header]
    accepted_auth_headers:'auth_header_list' = [valid_auth_header]

    refused_args = (channel_url, refused_auth_headers, stop_event, refused_results)
    accepted_args = (channel_url, accepted_auth_headers, stop_event, accepted_results)

    refused_caller = Thread(target=_call_until_stopped, args=refused_args)
    accepted_caller = Thread(target=_call_until_stopped, args=accepted_args)

    refused_caller.start()
    accepted_caller.start()

    # .. both call the channel while the configuration is reloaded repeatedly ..
    try:
        for _ in range(_reload_count):
            _ = admin_client.invoke('zato.server.invoker', {'func_name': 'reload_config'})
            sleep(_reload_interval)

        sleep(_settle_time)

    finally:
        stop_event.set()
        refused_caller.join()
        accepted_caller.join()

    # .. every request reached the server ..
    assert refused_results.connection_errors == []
    assert accepted_results.connection_errors == []

    refused_count = len(refused_results.status_codes)
    accepted_count = len(accepted_results.status_codes)

    assert refused_count > 0
    assert accepted_count > 0

    # .. no request without valid credentials was served ..
    for status_code in refused_results.status_codes:
        assert status_code != OK

    # .. and every request with valid credentials was.
    for status_code in accepted_results.status_codes:
        assert status_code == OK

# ################################################################################################################################
# ################################################################################################################################
