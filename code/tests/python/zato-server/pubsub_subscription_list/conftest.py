# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# gevent
from gevent import monkey
monkey.patch_all()

# pytest
import pytest

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.test.pubsub_in_process import InProcessServer
from zato.common.test.pubsub_in_process_support import RESTPushEndpoint

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

_suffix = CryptoManager.generate_hex_string(8)

Topic_Pull = f'sub.list.pull.{_suffix}'
Topic_Push_Rest = f'sub.list.push.rest.{_suffix}'
Topic_Push_Service = f'sub.list.push.service.{_suffix}'
Topic_Second = f'sub.list.second.{_suffix}'

Security_Pull = f'sub.list.sec.pull.{_suffix}'
Security_Push_Rest = f'sub.list.sec.push.rest.{_suffix}'
Security_Push_Service = f'sub.list.sec.push.service.{_suffix}'

Password = 'password.' + CryptoManager.generate_hex_string()

Service_Push_Name = f'sub.list.push.service.{_suffix}'
Service_Push_Module = f'sub_list_push_service_{_suffix}.py'

# ################################################################################################################################

def _initial_enmasse(push_rest_url:'str') -> 'str':
    """ Returns the enmasse YAML of the topics, security definitions and subscriptions of each in-process server.
    """
    out = f"""
security:
  - name: {Security_Pull}
    username: {Security_Pull}
    password: {Password}
    type: basic_auth

  - name: {Security_Push_Rest}
    username: {Security_Push_Rest}
    password: {Password}
    type: basic_auth

  - name: {Security_Push_Service}
    username: {Security_Push_Service}
    password: {Password}
    type: basic_auth

pubsub_topic:
  - name: {Topic_Pull}
  - name: {Topic_Push_Rest}
  - name: {Topic_Push_Service}
  - name: {Topic_Second}

pubsub_permission:
  - security: {Security_Pull}
    pub: ['{Topic_Pull}', '{Topic_Second}']
    sub: ['{Topic_Pull}', '{Topic_Second}']

  - security: {Security_Push_Rest}
    pub: ['{Topic_Push_Rest}', '{Topic_Second}']
    sub: ['{Topic_Push_Rest}', '{Topic_Second}']

  - security: {Security_Push_Service}
    pub: ['{Topic_Push_Service}', '{Topic_Second}']
    sub: ['{Topic_Push_Service}', '{Topic_Second}']

outgoing_rest:
  - name: sub.list.push.endpoint.{_suffix}
    host: {push_rest_url}
    url_path: /
    data_format: json

pubsub_subscription:
  - security: {Security_Pull}
    delivery_type: pull
    topic_list:
      - {Topic_Pull}

  - security: {Security_Push_Rest}
    delivery_type: push
    push_rest_endpoint: sub.list.push.endpoint.{_suffix}
    topic_list:
      - {Topic_Push_Rest}

  - security: {Security_Push_Service}
    delivery_type: push
    push_service: {Service_Push_Name}
    topic_list:
      - {Topic_Push_Service}
"""
    return out

# ################################################################################################################################

_push_service_source = f'''
# -*- coding: utf-8 -*-

from zato.server.service import Service

class {_suffix.replace("-", "_").title().replace("_", "")}Push(Service):
    name = '{Service_Push_Name}'

    def handle(self):
        pass
'''

# ################################################################################################################################

@pytest.fixture(params=['sqlite', 'postgresql'])
def in_process_server(request:'any_') -> 'any_':
    """ An in-process server on SQLite or on PostgreSQL with the initial subscriptions of the suite.
    """
    push_endpoint = RESTPushEndpoint()
    push_endpoint.start()

    enmasse_yaml = _initial_enmasse(push_endpoint.address)

    service_modules = {
        Service_Push_Module: _push_service_source,
    }

    server = InProcessServer(
        db_mode=request.param,
        enmasse_yaml=enmasse_yaml,
        service_modules=service_modules,
    )
    server.start()

    try:
        yield server, push_endpoint
    finally:
        server.stop()
        push_endpoint.stop()

# ################################################################################################################################

@pytest.fixture
def postgresql_server() -> 'any_':
    """ An in-process server on PostgreSQL alone, for the lock timeout suite.
    """
    push_endpoint = RESTPushEndpoint()
    push_endpoint.start()

    enmasse_yaml = _initial_enmasse(push_endpoint.address)

    server = InProcessServer(
        db_mode='postgresql',
        enmasse_yaml=enmasse_yaml,
        service_modules={Service_Push_Module: _push_service_source},
    )
    server.start()

    try:
        yield server, push_endpoint
    finally:
        server.stop()
        push_endpoint.stop()

# ################################################################################################################################
# ################################################################################################################################
