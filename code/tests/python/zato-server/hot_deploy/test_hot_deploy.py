# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from base64 import b64encode
from http.client import OK
from json import dumps, loads
from urllib.request import Request, urlopen

# Zato
from zato.common.const import ServiceConst
from zato.common.test.config_hot_deploy import TestConfig

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.pickup_listener import PickupListener
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

# Timeout in seconds for the HTTP requests that invoke the services deployed
_invoke_timeout = 30

# ################################################################################################################################
# ################################################################################################################################

def _read_server_log(server_directory:'str') -> 'str':
    log_path = os.path.join(server_directory, 'logs', 'server.log')
    with open(log_path, 'r') as f:
        return f.read()

# ################################################################################################################################

def _deploy(listener:'PickupListener', relative_path:'str', source:'str') -> 'None':
    """ Writes a file of the project and returns once the server deployed it.
    """
    data = source.encode('utf8')
    listener.deploy(relative_path, data)

# ################################################################################################################################

def _invoke(service_name:'str') -> 'anydict':
    """ Invokes a service on the live server through the admin.invoke channel and returns its response.
    """
    url = f'{TestConfig.base_url}/zato/api/invoke/{service_name}'

    credentials = f'{ServiceConst.API_Admin_Invoke_Username}:{TestConfig.password}'
    auth = b64encode(credentials.encode()).decode()

    request = Request(url, data=dumps({}).encode(), method='POST')
    request.add_header('Authorization', f'Basic {auth}')
    request.add_header('Content-Type', 'application/json')

    with urlopen(request, timeout=_invoke_timeout) as response:
        assert response.status == OK
        raw = response.read()

    out = loads(raw)
    return out

# ################################################################################################################################

def _get_service_source(class_name:'str', service_name:'str', imports:'str', value:'str') -> 'str':
    """ Returns the source of a module with one service that returns the given expression.
    """
    out = f'''
from zato.server.service import Service
{imports}

class {class_name}(Service):
    name = '{service_name}'

    def handle(self):
        self.response.payload = {{'value': {value}}}
'''
    return out

# ################################################################################################################################

def _count_deployments(relative_path:'str') -> 'int':
    """ Returns how many times the server log shows the service of a file deployed.
    """
    path = os.path.join(TestConfig.project_directory, relative_path)
    log_content = _read_server_log(TestConfig.server_directory)

    out = log_content.count(f'Deployed 1 service from `{path}`')
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_deploy_py_file(zato_server:'PickupListener') -> 'None':
    """ A .py service file dropped into the project is deployed by the listener.
    """
    service_content = '''
from zato.server.service import Service

class HotDeployTestService(Service):
    name = 'hot-deploy.test.service-1'

    def handle(self):
        self.response.payload = 'hot-deploy-test-ok'
'''

    _deploy(zato_server, 'src/services/test_hot_deploy_svc.py', service_content)

    log_content = _read_server_log(TestConfig.server_directory)
    assert 'hot-deploy.test.service-1' in log_content, \
        f'Expected service name in server log but not found. Last 2000 chars:\n{log_content[-2000:]}'

# ################################################################################################################################
# ################################################################################################################################

def test_deploy_ini_file(zato_server:'PickupListener') -> 'None':
    """ A .ini config file dropped into the project is picked up and synced.
    """
    ini_content = '''[hot_deploy_test]
key1=value1
key2=value2
'''

    _deploy(zato_server, 'src/user-conf/hot_deploy_test.ini', ini_content)

    log_content = _read_server_log(TestConfig.server_directory)
    assert 'hot_deploy_test.ini' in log_content, \
        f'Expected .ini file name in server log but not found. Last 2000 chars:\n{log_content[-2000:]}'

# ################################################################################################################################
# ################################################################################################################################

def test_deploy_zrules_file(zato_server:'PickupListener') -> 'None':
    """ A .zrules file dropped into the project is picked up and loaded.
    """
    zrules_content = '''rule hot_deploy_test_rule:
    when:
        event.type == "test"
    then:
        log("hot deploy test rule fired")
'''

    _deploy(zato_server, 'src/user-conf/hot_deploy_test.zrules', zrules_content)

    log_content = _read_server_log(TestConfig.server_directory)
    assert 'hot_deploy_test.zrules' in log_content, \
        f'Expected .zrules file name in server log but not found. Last 2000 chars:\n{log_content[-2000:]}'

# ################################################################################################################################
# ################################################################################################################################

def test_deploy_enmasse_file(zato_server:'PickupListener') -> 'None':
    """ A .yaml enmasse file dropped into the project is picked up and executed.
    """
    enmasse_content = '''channel_rest:
  - name: "hot-deploy-test-channel"
    service: "demo.my-service"
    url_path: "/hot-deploy-test"
    security: "anonymous"
'''

    _deploy(zato_server, 'src/enmasse.yaml', enmasse_content)

    log_content = _read_server_log(TestConfig.server_directory)
    assert 'enmasse' in log_content.lower(), \
        f'Expected enmasse reference in server log but not found. Last 2000 chars:\n{log_content[-2000:]}'

# ################################################################################################################################
# ################################################################################################################################

def test_indirect_importer_is_redeployed(zato_server:'PickupListener') -> 'None':
    """ A service that imports a module which imports another one returns what the other one holds after it changes.
    """
    service_name = 'hot-deploy.test.chain'

    _deploy(zato_server, 'src/common/chain/__init__.py', '')
    _deploy(zato_server, 'src/common/chain/models.py', 'VALUE = 1\n')
    _deploy(zato_server, 'src/common/chain/api.py', 'from common.chain.models import VALUE\n')

    service_source = _get_service_source('ChainService', service_name, 'from common.chain import api', 'api.VALUE')
    _deploy(zato_server, 'src/services/hot_deploy_chain.py', service_source)

    assert _invoke(service_name) == {'value': 1}

    _deploy(zato_server, 'src/common/chain/models.py', 'VALUE = 2\n')

    assert _invoke(service_name) == {'value': 2}

# ################################################################################################################################
# ################################################################################################################################

def test_package_attribute_importer_is_redeployed(zato_server:'PickupListener') -> 'None':
    """ A module that imports another one as an attribute of its package reads the module as it is after the change.
    """
    service_name = 'hot-deploy.test.package-attribute'

    _deploy(zato_server, 'src/common/attribute/__init__.py', '')
    _deploy(zato_server, 'src/common/attribute/models.py', 'VALUE = 1\n')
    _deploy(zato_server, 'src/common/attribute/api.py', 'from common.attribute import models\n\nVALUE = models.VALUE\n')

    service_source = _get_service_source('PackageAttributeService', service_name, 'import common.attribute.api',
        'common.attribute.api.VALUE')
    _deploy(zato_server, 'src/services/hot_deploy_package_attribute.py', service_source)

    assert _invoke(service_name) == {'value': 1}

    _deploy(zato_server, 'src/common/attribute/models.py', 'VALUE = 2\n')

    assert _invoke(service_name) == {'value': 2}

# ################################################################################################################################
# ################################################################################################################################

def test_relative_importer_is_redeployed(zato_server:'PickupListener') -> 'None':
    """ A package that imports its own module relatively passes the changed value on to the service that imports it.
    """
    service_name = 'hot-deploy.test.relative'

    _deploy(zato_server, 'src/common/relative/models.py', 'VALUE = 1\n')
    _deploy(zato_server, 'src/common/relative/__init__.py', 'from .models import VALUE\n')

    service_source = _get_service_source('RelativeService', service_name, 'from common.relative import VALUE', 'VALUE')
    _deploy(zato_server, 'src/services/hot_deploy_relative.py', service_source)

    assert _invoke(service_name) == {'value': 1}

    _deploy(zato_server, 'src/common/relative/models.py', 'VALUE = 2\n')

    assert _invoke(service_name) == {'value': 2}

# ################################################################################################################################
# ################################################################################################################################

def test_import_cycle_is_redeployed(zato_server:'PickupListener') -> 'None':
    """ Two service modules that import each other are both redeployed once one of them changes.
    """
    first_name = 'hot-deploy.test.cycle-first'
    second_name = 'hot-deploy.test.cycle-second'

    first_path = 'src/services/hot_deploy_cycle_first.py'
    second_path = 'src/services/hot_deploy_cycle_second.py'

    first_imports = 'import services.hot_deploy_cycle_second\n\nVALUE = {}\n'
    second_imports = 'import services.hot_deploy_cycle_first'
    second_value = 'services.hot_deploy_cycle_first.VALUE'

    # The second module imports the first one only after the first one exists, which imports the second one in turn
    _deploy(zato_server, second_path, _get_service_source('CycleSecond', second_name, '', '0'))
    _deploy(zato_server, first_path, _get_service_source('CycleFirst', first_name, first_imports.format(1), 'VALUE'))
    _deploy(zato_server, second_path, _get_service_source('CycleSecond', second_name, second_imports, second_value))

    assert _invoke(first_name) == {'value': 1}
    assert _invoke(second_name) == {'value': 1}

    _deploy(zato_server, first_path, _get_service_source('CycleFirst', first_name, first_imports.format(2), 'VALUE'))

    assert _invoke(first_name) == {'value': 2}
    assert _invoke(second_name) == {'value': 2}

# ################################################################################################################################
# ################################################################################################################################

def test_diamond_importer_is_redeployed_once(zato_server:'PickupListener') -> 'None':
    """ A service that imports two modules which both import a shared one is redeployed once per change of the shared one.
    """
    service_name = 'hot-deploy.test.diamond'
    service_path = 'src/services/hot_deploy_diamond.py'

    _deploy(zato_server, 'src/common/diamond/__init__.py', '')
    _deploy(zato_server, 'src/common/diamond/shared.py', 'VALUE = 1\n')
    _deploy(zato_server, 'src/common/diamond/left.py', 'from common.diamond.shared import VALUE\n')
    _deploy(zato_server, 'src/common/diamond/right.py', 'from common.diamond.shared import VALUE\n')

    imports = 'from common.diamond import left, right'
    service_source = _get_service_source('DiamondService', service_name, imports, '[left.VALUE, right.VALUE]')
    _deploy(zato_server, service_path, service_source)

    assert _invoke(service_name) == {'value': [1, 1]}

    # Each process of the server logs the deployment of the service once
    initial_count = _count_deployments(service_path)

    _deploy(zato_server, 'src/common/diamond/shared.py', 'VALUE = 2\n')

    assert _invoke(service_name) == {'value': [2, 2]}
    assert _count_deployments(service_path) == initial_count * 2

# ################################################################################################################################
# ################################################################################################################################
