# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import shutil
import sys
import tempfile
from collections.abc import Generator

_here = os.path.dirname(__file__)
_tests_dir = os.path.join(_here, '..', '..', 'zato-common')

sys.path.insert(0, os.path.join(_tests_dir, 'pubsub_faults'))
sys.path.insert(0, os.path.join(_tests_dir, 'lib'))
sys.path.insert(0, _here)

# pytest
import pytest

# Zato
from zato.common.audit_log.api import ModuleCtx as AuditLogCtx
from zato.common.db_env.database_env import DatabaseEnv
from zato.common.db_env.fence import ModuleCtx as FenceCtx
from zato.common.test.pubsub_database import get_database_address, get_db_mode, get_runtime_dir, start_pubsub_database, \
    stop_pubsub_database
from zato.common.test.pubsub_profile import session_dns

# Live environment
from live_environment.quickstart import ZatoEnvironment

# Fault tools
from toxiproxy import Database_Proxy, Toxiproxy, Toxiproxy_Host

# Local
from _support import DatabaseProxy, ModuleCtx as SupportCtx, Names, Pickup, Runtime, WriteFault, is_postgresql, \
    render_template, wait_for

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.client import AdminClient
    from zato.common.test.pubsub_database import PubSubDatabase
    from zato.common.typing_ import strstrdict

    AdminClient = AdminClient
    PubSubDatabase = PubSubDatabase
    strstrdict = strstrdict

# ################################################################################################################################
# ################################################################################################################################

_template_path = os.path.join(_here, '_enmasse_template.yaml')
_runtime_source = os.path.join(_here, '_runtime_service.py')
_rest_services_source = os.path.join(_tests_dir, 'lib', 'pubsub_rest', '_services.py')

# ################################################################################################################################
# ################################################################################################################################

class SuiteCtx:

    Directory_Prefix = 'zato_ha_pubsub_subscription_'
    Work_Directory_Prefix = 'zato_ha_pubsub_subscription_work_'
    Password_Prefix = 'test.ha.pubsub.subscription'
    Database_Label = 'ha-pubsub-subscription'
    Toxiproxy_Label = 'ha-pubsub-subscription'
    Generation_File_Name = 'database-generation'

# ################################################################################################################################
# ################################################################################################################################

def wait_for_runtime_service(client:'AdminClient') -> 'None':
    """ Waits until the runtime service is deployed.
    """
    def _is_deployed() -> 'bool':
        request = {'name': SupportCtx.Runtime_Service}
        response = client.invoke('zato.service.get-by-name', request)
        out = response['name'] == SupportCtx.Runtime_Service
        return out

    wait_for(_is_deployed, f'The deployment of service {SupportCtx.Runtime_Service}')

# ################################################################################################################################

def _read_source(path:'str') -> 'str':
    with open(path) as source_file:
        out = source_file.read()

    return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='module')
def names() -> 'Names':
    """ The object names of the module's live environment.
    """
    out = Names()
    return out

# ################################################################################################################################

@pytest.fixture(scope='module')
def database() -> 'Generator[PubSubDatabase | None, None, None]':
    """ The PostgreSQL container of the module on PostgreSQL, and nothing on SQLite.
    """
    if not is_postgresql():
        yield None
        return

    out = start_pubsub_database(SuiteCtx.Database_Label, get_db_mode())

    try:
        yield out
    finally:
        stop_pubsub_database(out)

# ################################################################################################################################

@pytest.fixture(scope='module')
def database_proxy(database:'PubSubDatabase | None') -> 'Generator[DatabaseProxy | None, None, None]':
    """ The proxy of Toxiproxy through which the server reaches PostgreSQL, and nothing on SQLite.
    """
    if database is None:
        yield None
        return

    toxiproxy = Toxiproxy(SuiteCtx.Toxiproxy_Label)
    toxiproxy.start()

    try:
        upstream_host = get_database_address(database)
        listen_port = toxiproxy.add_proxy(Database_Proxy, database.port, upstream_host)

        # The endpoint name of a managed mode resolves to the proxy
        if database.profile_name:
            session_dns.register(get_runtime_dir(), database.endpoint, Toxiproxy_Host)

        yield DatabaseProxy(database, toxiproxy, listen_port)

    finally:
        toxiproxy.stop()

# ################################################################################################################################

@pytest.fixture(scope='module')
def server_env(database_proxy:'DatabaseProxy | None') -> 'Generator[strstrdict, None, None]':
    """ The environment variables of the live server of the module, which a restart of the server reuses.
    """
    work_dir = tempfile.mkdtemp(prefix=SuiteCtx.Work_Directory_Prefix)

    out = {
        AuditLogCtx.Env_Enabled: 'True',
        FenceCtx.Env_Generation_File: os.path.join(work_dir, SuiteCtx.Generation_File_Name),
    }

    if database_proxy is None:
        out[DatabaseEnv.Env_Type] = DatabaseEnv.Type_SQLite
    else:
        out.update(database_proxy.database.env)
        out['Zato_Database_Port'] = f'{database_proxy.listen_port}'

    try:
        yield out
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)

# ################################################################################################################################

@pytest.fixture(scope='module')
def environment(names:'Names', server_env:'strstrdict') -> 'Generator[ZatoEnvironment, None, None]':
    """ A live server on SQLite or on PostgreSQL with the services of the suite and its initial subscriptions.
    """
    directory = tempfile.mkdtemp(prefix=SuiteCtx.Directory_Prefix)
    out = ZatoEnvironment(directory, password_prefix=SuiteCtx.Password_Prefix)

    try:
        out.create()
        out.start(server_env)

        out.deploy(SupportCtx.Runtime_Service_File, _read_source(_runtime_source))
        out.deploy(SupportCtx.REST_Services_File, _read_source(_rest_services_source))
        wait_for_runtime_service(out.client())

        definitions = render_template(_template_path, names.placeholders())
        _ = out.import_yaml('initial.yaml', definitions)

        yield out

    finally:
        out.stop()

# ################################################################################################################################

@pytest.fixture(scope='module')
def client(environment:'ZatoEnvironment') -> 'AdminClient':
    """ A client of the module's live server.
    """
    out = environment.client(SupportCtx.Runtime_Client_Timeout)
    return out

# ################################################################################################################################

@pytest.fixture(scope='module')
def pickup(environment:'ZatoEnvironment') -> 'Pickup':
    """ Places enmasse files into the pickup directory of the live server.
    """
    out = Pickup(environment)
    return out

# ################################################################################################################################

@pytest.fixture(scope='module')
def runtime(client:'AdminClient') -> 'Runtime':
    """ The services that the suite deployed into the live server.
    """
    out = Runtime(client)
    return out

# ################################################################################################################################

@pytest.fixture
def write_fault(environment:'ZatoEnvironment', database_proxy:'DatabaseProxy | None') -> 'Generator[WriteFault, None, None]':
    """ Fails the writes of the server to the pub/sub database while a test applies it, and removes it at the end.
    """
    out = WriteFault(environment, database_proxy)

    try:
        yield out
    finally:
        out.remove()

# ################################################################################################################################
# ################################################################################################################################
