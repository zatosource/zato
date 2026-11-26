# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import shutil
import tempfile
from collections.abc import Generator

# pytest
import pytest

# Zato
from zato.common.audit_log.api import ModuleCtx as AuditLogCtx
from zato.common.crypto.api import CryptoManager
from zato.common.test.order_to_cash.models import ServiceName

# Live environment
from live_environment.quickstart import Host, ZatoEnvironment
from live_environment.redis_process import ModuleCtx as RedisCtx, RedisProcess

# Order-to-cash
from order_to_cash.scenario import Channel, Module, render_definitions, Source, submit_order, submit_orders, wait_until

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.client import AdminClient
    from zato.common.typing_ import anydict, dictlist

    AdminClient = AdminClient

# ################################################################################################################################
# ################################################################################################################################

class SuiteCtx:
    Directory_Prefix   = 'zato_pubsub_services_'
    Password_Prefix    = 'test.pubsub.services'
    Definitions_File   = 'order-to-cash.yaml'
    Client_Timeout     = 30

# ################################################################################################################################
# ################################################################################################################################

class Suite:
    """ A live server with the order-to-cash integration, and the trading partner that submits orders to it.
    """
    def __init__(self, environment:'ZatoEnvironment', partner_password:'str') -> 'None':
        self.environment = environment
        self.partner_password = partner_password
        self.server_directory = environment.server_directory
        self.client:'AdminClient' = environment.client(SuiteCtx.Client_Timeout)
        self.channel_url = f'http://{Host}:{environment.server_port}{Channel.URL_Path}'

    def submit(self, order:'anydict') -> 'None':
        submit_order(self.channel_url, self.partner_password, order)

    def submit_many(self, orders:'dictlist') -> 'None':
        submit_orders(self.channel_url, self.partner_password, orders)

    def is_deployed(self, service_name:'str') -> 'bool':
        """ Whether the server has a service of the name deployed.
        """
        try:
            response = self.client.invoke('zato.service.get-by-name', {'name': service_name})

        # The server refuses the request for a service that it does not have
        except Exception:
            return False

        out = response['name'] == service_name
        return out

# ################################################################################################################################
# ################################################################################################################################

def _copy_module(environment:'ZatoEnvironment', file_name:'str', source_path:'str') -> 'None':
    """ Places a module into the pickup directory before the server starts, which deploys it during its startup.
    """
    os.makedirs(environment.pickup_directory, exist_ok=True)

    target = os.path.join(environment.pickup_directory, file_name)
    _ = shutil.copyfile(source_path, target)

# ################################################################################################################################

def _create_suite(*, is_receivables_deployed:'bool') -> 'Generator[Suite, None, None]':
    """ Creates the environment with the modules of the integration, starts it and imports its definitions.
    Without is_receivables_deployed the receivables module is left out and its subscription holds its messages.
    """
    directory = tempfile.mkdtemp(prefix=SuiteCtx.Directory_Prefix)
    environment = ZatoEnvironment(directory, password_prefix=SuiteCtx.Password_Prefix)
    partner_password = CryptoManager.generate_hex_string()

    # The streams of the scheduler and of the queue bridge have the same keys in every Redis,
    # so the server receives a Redis of its own that no other server on this machine uses
    redis = RedisProcess()

    try:
        redis.start()
        environment.create(redis_port=redis.port)

        _copy_module(environment, Module.Core, Source.Core)
        _copy_module(environment, Module.Fulfillment, Source.Fulfillment)
        _copy_module(environment, Module.Read_Trail, Source.Read_Trail)

        if is_receivables_deployed:
            _copy_module(environment, Module.Receivables, Source.Receivables)

        server_environment = redis.server_environment()
        server_environment.update({
            'Zato_Queue_Bridge_Redis_Host': RedisCtx.Host,
            'Zato_Queue_Bridge_Redis_Port': str(redis.port),
            'Zato_Queue_Bridge_Redis_Password': '',
            AuditLogCtx.Env_Enabled: 'True',
        })

        environment.start(server_environment)

        suite = Suite(environment, partner_password)

        def _is_ready() -> 'bool':
            out = suite.is_deployed(ServiceName.Read_Trail)
            return out

        wait_until(_is_ready, f'The deployment of service {ServiceName.Read_Trail}')

        definitions = render_definitions(partner_password, is_receivables_active=is_receivables_deployed)
        _ = environment.import_yaml(SuiteCtx.Definitions_File, definitions)

        yield suite

    finally:
        environment.stop()
        redis.cleanup()

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='module')
def suite() -> 'Generator[Suite, None, None]':
    """ The integration with all of its services deployed.
    """
    yield from _create_suite(is_receivables_deployed=True)

# ################################################################################################################################

@pytest.fixture(scope='module')
def late_suite() -> 'Generator[Suite, None, None]':
    """ The integration without the receivables, whose subscription holds the invoices and the rejections.
    """
    yield from _create_suite(is_receivables_deployed=False)

# ################################################################################################################################
# ################################################################################################################################
