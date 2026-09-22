# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import time
from base64 import b64encode
from http.client import OK
from json import dumps, loads
from urllib.error import HTTPError
from urllib.request import Request, urlopen

# pytest
import pytest

# Zato
from zato.common.api import IDEDeploy
from zato.common.const import ServiceConst
from zato.common.test.config_hot_deploy import TestConfig

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

# The channel an IDE plugin deploys through - a direct one to zato.hot-deploy.create, which is why its reply
# keeps the zato_ide_deploy_create_response wrapper that the plugin reads. Through /zato/api/invoke the wrapper
# would be stripped, as it is for any service with a direct I/O declaration invoked that way.
_ide_deploy_path = '/ide-deploy'

# The channel's security definition is created with a random password, so the tests set one they know first
_service_change_password = 'zato.security.basic-auth.change-password'
_ide_password = 'test.ide.deploy.password'

# How long to wait for the new password to reach the server's in-RAM config, in seconds
_password_wait = 30

# How often to check whether the new password is accepted, in seconds
_password_poll_interval = 0.5

# How long to wait for the pickup directory listener to deploy what the plugin uploaded
_deploy_wait = 15

# Timeout in seconds for the HTTP requests
_invoke_timeout = 30

# ################################################################################################################################
# ################################################################################################################################

def _post_json(url:'str', username:'str', password:'str', payload:'anydict') -> 'tuple[int, bytes]':
    """ Posts a JSON payload with basic auth and returns the status code with the raw body, whatever the status was.
    """
    body = dumps(payload).encode()

    credentials = f'{username}:{password}'
    auth = b64encode(credentials.encode()).decode()

    request = Request(url, data=body, method='POST')
    request.add_header('Authorization', f'Basic {auth}')
    request.add_header('Content-Type', 'application/json')

    try:
        with urlopen(request, timeout=_invoke_timeout) as response:
            out = (response.status, response.read())
    except HTTPError as error:
        out = (error.code, error.read())

    return out

# ################################################################################################################################

def _admin_invoke(service_name:'str', payload:'anydict') -> 'any_':
    """ Invokes a service on the live server through the admin.invoke channel.
    """
    url = f'{TestConfig.base_url}/zato/api/invoke/{service_name}'
    status, raw = _post_json(url, ServiceConst.API_Admin_Invoke_Username, TestConfig.password, payload)

    if status != OK:
        error_text = raw.decode('utf-8', errors='replace')
        raise Exception(f'{service_name} returned HTTP {status}: {error_text}')

    if not raw:
        return {}

    out = loads(raw)
    return out

# ################################################################################################################################

def _ide_deploy(payload:'anydict') -> 'any_':
    """ Sends a request the way an IDE plugin does - through the /ide-deploy channel with the ide_publisher credentials.
    """
    url = f'{TestConfig.base_url}{_ide_deploy_path}'
    status, raw = _post_json(url, IDEDeploy.Username, _ide_password, payload)

    if status != OK:
        error_text = raw.decode('utf-8', errors='replace')
        raise Exception(f'{_ide_deploy_path} returned HTTP {status}: {error_text}')

    out = loads(raw)
    return out

# ################################################################################################################################

def _read_server_log() -> 'str':
    log_path = os.path.join(TestConfig.server_directory, 'logs', 'server.log')
    with open(log_path, 'r') as log_file:
        out = log_file.read()
        return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='module')
def ide_credentials(zato_server:'any_') -> 'None':
    """ Gives the ide_publisher security definition a password the tests know and waits until the channel accepts it.
    """
    _ = _admin_invoke(_service_change_password, {
        'name': IDEDeploy.Username,
        'password': _ide_password,
    })

    # The change reaches the server's in-RAM config asynchronously, so the channel is polled until it lets us in
    url = f'{TestConfig.base_url}{_ide_deploy_path}'
    deadline = time.monotonic() + _password_wait

    while True:
        status, raw = _post_json(url, IDEDeploy.Username, _ide_password, {})

        if status == OK:
            return

        if time.monotonic() >= deadline:
            error_text = raw.decode('utf-8', errors='replace')
            raise Exception(f'{_ide_deploy_path} still refuses the new password after {_password_wait}s -> HTTP {status}: {error_text}')

        time.sleep(_password_poll_interval)

# ################################################################################################################################
# ################################################################################################################################

def test_empty_request_confirms_the_server_is_reachable(ide_credentials:'None') -> 'None':
    """ A request with nothing to deploy is a connection test and receives a success reply.
    """
    response = _ide_deploy({})

    result = response['zato_ide_deploy_create_response']
    assert result['success'] is True
    assert result['msg'] == 'OK, server reached'

# ################################################################################################################################
# ################################################################################################################################

def test_file_name_with_payload_is_deployed(ide_credentials:'None') -> 'None':
    """ A bare file name with a payload is written to the pickup directory and deployed from there.
    """
    service_content = '''
from zato.server.service import Service

class IDEDeployTestService(Service):
    name = 'hot-deploy.test.ide-deploy'

    def handle(self):
        self.response.payload = 'ide-deploy-test-ok'
'''

    payload = b64encode(service_content.encode()).decode()

    response = _ide_deploy({
        'payload': payload,
        'payload_name': 'test_ide_deploy_service.py',
    })

    result = response['zato_ide_deploy_create_response']
    assert result['success'] is True
    assert result['msg'] == 'OK, deployed to server'

    time.sleep(_deploy_wait)

    log_content = _read_server_log()
    assert 'hot-deploy.test.ide-deploy' in log_content, \
        f'Expected service name in server log but not found. Last 2000 chars:\n{log_content[-2000:]}'

# ################################################################################################################################
# ################################################################################################################################
