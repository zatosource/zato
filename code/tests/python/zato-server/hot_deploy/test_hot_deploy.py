# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))

from config import TestConfig

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

_deploy_wait = 15

# ################################################################################################################################
# ################################################################################################################################

def _read_server_log(server_directory:'str') -> 'str':
    log_path = os.path.join(server_directory, 'logs', 'server.log')
    with open(log_path, 'r') as f:
        return f.read()

# ################################################################################################################################
# ################################################################################################################################

def _write_file(path:'str', content:'str') -> 'None':
    with open(path, 'w') as f:
        _ = f.write(content)

# ################################################################################################################################
# ################################################################################################################################

def test_deploy_py_file(zato_server:'any_') -> 'None':
    """ A .py service file dropped into the project is deployed by the listener.
    """
    service_content = '''
from zato.server.service import Service

class HotDeployTestService(Service):
    name = 'hot-deploy.test.service-1'

    def handle(self):
        self.response.payload = 'hot-deploy-test-ok'
'''

    file_path = os.path.join(TestConfig.project_directory, 'src', 'services', 'test_hot_deploy_svc.py')
    _write_file(file_path, service_content)

    time.sleep(_deploy_wait)

    log_content = _read_server_log(TestConfig.server_directory)
    assert 'hot-deploy.test.service-1' in log_content, \
        f'Expected service name in server log but not found. Last 2000 chars:\n{log_content[-2000:]}'

# ################################################################################################################################
# ################################################################################################################################

def test_deploy_ini_file(zato_server:'any_') -> 'None':
    """ A .ini config file dropped into the project is picked up and synced.
    """
    ini_content = '''[hot_deploy_test]
key1=value1
key2=value2
'''

    file_path = os.path.join(TestConfig.project_directory, 'src', 'user-conf', 'hot_deploy_test.ini')
    _write_file(file_path, ini_content)

    time.sleep(_deploy_wait)

    log_content = _read_server_log(TestConfig.server_directory)
    assert 'hot_deploy_test.ini' in log_content, \
        f'Expected .ini file name in server log but not found. Last 2000 chars:\n{log_content[-2000:]}'

# ################################################################################################################################
# ################################################################################################################################

def test_deploy_zrules_file(zato_server:'any_') -> 'None':
    """ A .zrules file dropped into the project is picked up and loaded.
    """
    zrules_content = '''rule hot_deploy_test_rule:
    when:
        event.type == "test"
    then:
        log("hot deploy test rule fired")
'''

    file_path = os.path.join(TestConfig.project_directory, 'src', 'user-conf', 'hot_deploy_test.zrules')
    _write_file(file_path, zrules_content)

    time.sleep(_deploy_wait)

    log_content = _read_server_log(TestConfig.server_directory)
    assert 'hot_deploy_test.zrules' in log_content, \
        f'Expected .zrules file name in server log but not found. Last 2000 chars:\n{log_content[-2000:]}'

# ################################################################################################################################
# ################################################################################################################################

def test_deploy_enmasse_file(zato_server:'any_') -> 'None':
    """ A .yaml enmasse file dropped into the project is picked up and executed.
    """
    enmasse_content = '''channel_rest:
  - name: "hot-deploy-test-channel"
    service: "demo.my-service"
    url_path: "/hot-deploy-test"
    security: "anonymous"
'''

    file_path = os.path.join(TestConfig.project_directory, 'src', 'enmasse.yaml')
    _write_file(file_path, enmasse_content)

    time.sleep(_deploy_wait)

    log_content = _read_server_log(TestConfig.server_directory)
    assert 'enmasse' in log_content.lower(), \
        f'Expected enmasse reference in server log but not found. Last 2000 chars:\n{log_content[-2000:]}'

# ################################################################################################################################
# ################################################################################################################################
