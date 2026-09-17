# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import time
from base64 import b64encode
from json import dumps, loads
from urllib.error import HTTPError
from urllib.request import Request, urlopen

# Zato
from zato.common.const import ServiceConst
from zato.common.test.config_hot_deploy import TestConfig

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

# The service an IDE plugin's /ide-deploy channel points to
_service_name = 'zato.hot-deploy.create'

# How long to wait for the pickup directory listener to deploy what the plugin uploaded
_deploy_wait = 15

# Timeout in seconds for the admin invoke HTTP requests
_invoke_timeout = 30

# ################################################################################################################################
# ################################################################################################################################

def _admin_invoke(service_name:'str', payload:'anydict') -> 'any_':
    """ Invokes a service on the live server through the admin.invoke channel.
    """
    url = f'{TestConfig.base_url}/zato/api/invoke/{service_name}'
    body = dumps(payload).encode()

    credentials = f'{ServiceConst.API_Admin_Invoke_Username}:{TestConfig.password}'
    auth = b64encode(credentials.encode()).decode()

    request = Request(url, data=body, method='POST')
    request.add_header('Authorization', f'Basic {auth}')
    request.add_header('Content-Type', 'application/json')

    try:
        with urlopen(request, timeout=_invoke_timeout) as response:
            raw = response.read()
    except HTTPError as error:
        raw = error.read()
        error_text = raw.decode('utf-8', errors='replace')
        raise Exception(f'{service_name} returned HTTP {error.code}: {error_text}')

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

def test_empty_request_confirms_the_server_is_reachable(zato_server:'any_') -> 'None':
    """ A request with nothing to deploy is a connection test and receives a success reply.
    """
    response = _admin_invoke(_service_name, {})

    result = response['zato_ide_deploy_create_response']
    assert result['success'] is True
    assert result['msg'] == 'OK, server reached'

# ################################################################################################################################
# ################################################################################################################################

def test_file_name_with_payload_is_deployed(zato_server:'any_') -> 'None':
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

    response = _admin_invoke(_service_name, {
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
