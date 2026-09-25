# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys
import tempfile
from collections.abc import Generator

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'zato-common', 'lib'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'project', 'impl', 'src'))
sys.path.insert(0, os.path.dirname(__file__))

# pytest
import pytest

# Zato
from zato.common.audit_log.api import ModuleCtx as AuditLogCtx
from zato.common.crypto.api import CryptoManager
from zato.common.defaults import default_cluster_id

# Live environment
from live_containers.ready import wait_until
from live_environment.parts import Parts, tear_down
from live_environment.quickstart import ZatoEnvironment
from live_environment.scheduler import SchedulerProcess
from live_sql.containers import start_oracle, stop_container

# Zato - the suite's own parts
from _schema import ModuleCtx as SchemaCtx, Schema
from _support import FacilityDatabase, FaultPlan, RecordsDatabase, SyncDatabase

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from live_sql.containers import DatabaseServer
    from zato.common.test.client import AdminClient
    from zato.common.typing_ import strstrdict

# ################################################################################################################################
# ################################################################################################################################

server_gen    = Generator['DatabaseServer', None, None]
schema_gen    = Generator[Schema, None, None]
zato_gen      = Generator[ZatoEnvironment, None, None]
scheduler_gen = Generator[SchedulerProcess, None, None]
facility_gen  = Generator[FacilityDatabase, None, None]
records_gen   = Generator[RecordsDatabase, None, None]
sync_gen      = Generator[SyncDatabase, None, None]
faults_gen    = Generator[FaultPlan, None, None]
variant_gen   = Generator[str, None, None]

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The container and the port enmasse.yaml points both connections at.
    Database_Container = 'zato-test-facility-sync'
    Database_Port      = 21522
    Database_Host      = 'localhost'

    # The application user the image creates.
    Database_Username = 'zato_facility_sync'

    # The license key variable and the value used when it is not already set.
    License_Key_Variable = 'Zato_License_Key'
    License_Key_Value    = 'test.license.key'

    # The variables enmasse.yaml takes the two passwords from.
    Standby_Password_Variable = 'Facility_Standby_Password'
    Writer_Password_Variable  = 'Records_Writer_Password'

    # Where the server finds the services.
    Project_Root_Variable = 'Zato_Project_Root'
    Project_Directory     = os.path.join(os.path.dirname(__file__), 'project')

    # The definitions the server is given.
    Enmasse_File = os.path.join(os.path.dirname(__file__), 'enmasse.yaml')

    # The service whose presence says the project was deployed.
    Deployed_Service = 'facility.sync.run'

# ################################################################################################################################
# ################################################################################################################################

# What the session brought up.
_parts = Parts()

# The scheduler the session's server listens to - started only by the tests that need it.
_scheduler = SchedulerProcess()

# ################################################################################################################################
# ################################################################################################################################

def _read_enmasse() -> 'str':
    with open(ModuleCtx.Enmasse_File) as enmasse_file:
        out = enmasse_file.read()

    return out

# ################################################################################################################################

def _server_environment() -> 'strstrdict':
    """ What the server starts with on top of what the environment gives it.
    """
    out:'strstrdict' = {
        ModuleCtx.Project_Root_Variable: ModuleCtx.Project_Directory,
        AuditLogCtx.Env_Enabled: 'True',
        AuditLogCtx.Env_Type:    AuditLogCtx.Type_SQLite,
    }

    if ModuleCtx.License_Key_Variable not in os.environ:
        out[ModuleCtx.License_Key_Variable] = ModuleCtx.License_Key_Value

    scheduler_environment = _scheduler.server_environment()
    out.update(scheduler_environment)

    return out

# ################################################################################################################################

def _wait_for_project(client:'AdminClient') -> 'None':
    """ Waits until the server reports the project's services as deployed.
    """
    def _is_deployed() -> 'bool':
        request = {'cluster_id': default_cluster_id, 'name': ModuleCtx.Deployed_Service}
        response = client.invoke('zato.service.get-by-name', request)
        out = response['name'] == ModuleCtx.Deployed_Service
        return out

    wait_until(_is_deployed, f'service {ModuleCtx.Deployed_Service}')

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def database_server() -> 'server_gen':
    """ The one database container of the session.
    """
    password = 'test.database.' + CryptoManager.generate_hex_string()

    server = start_oracle(
        container_name=ModuleCtx.Database_Container,
        port=ModuleCtx.Database_Port,
        username=ModuleCtx.Database_Username,
        password=password,
    )

    yield server

    stop_container(server.container_name)

# ################################################################################################################################

@pytest.fixture(scope='session')
def schema(database_server:'DatabaseServer') -> 'schema_gen':
    """ Every user, table, package and grant, built from scratch with the package that never commits.
    """
    details = database_server.details

    out = Schema(
        host=ModuleCtx.Database_Host,
        port=ModuleCtx.Database_Port,
        service_name=details['name'],
        system_password=details['password'],
    )

    out.install(SchemaCtx.Variant_No_Commit)

    yield out

# ################################################################################################################################

@pytest.fixture(scope='session')
def zato(schema:'Schema') -> 'zato_gen':
    """ The server with the project deployed and the connections and jobs from enmasse.yaml.
    """
    directory = tempfile.mkdtemp(prefix='zato_facility_sync_')

    environment = ZatoEnvironment(directory, password_prefix='test.facility')
    _parts.add('Zato', environment.stop)
    _parts.add('Scheduler', _scheduler.cleanup)

    try:
        environment.create(needs_scheduler=True)

        server_environment = _server_environment()
        environment.start(server_environment)

        # The passwords enmasse.yaml reads.
        os.environ[ModuleCtx.Standby_Password_Variable] = schema.password
        os.environ[ModuleCtx.Writer_Password_Variable]  = schema.password

        enmasse_contents = _read_enmasse()
        _ = environment.import_yaml('enmasse.yaml', enmasse_contents)

        client = environment.client()
        _wait_for_project(client)

    # A setup cut short tears down what it started.
    except BaseException:
        tear_down(_parts)
        raise

    yield environment

    tear_down(_parts)

# ################################################################################################################################

@pytest.fixture(scope='session')
def client(zato:'ZatoEnvironment') -> 'AdminClient':
    out = zato.client()
    return out

# ################################################################################################################################

@pytest.fixture(scope='session')
def scheduler(zato:'ZatoEnvironment') -> 'SchedulerProcess':
    """ The scheduler the server listens to - a test starts it once its jobs have what they need.
    """
    out = _scheduler
    return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(autouse=True)
def clean_state(schema:'Schema', zato:'ZatoEnvironment') -> 'None':
    """ Every test starts with empty tables and no faults planned.
    """
    schema.reset_data()

# ################################################################################################################################

@pytest.fixture(params=[SchemaCtx.Variant_No_Commit, SchemaCtx.Variant_Commit])
def records_api(request:'pytest.FixtureRequest', schema:'Schema') -> 'variant_gen':
    """ The package variant a test runs against - both, unless the test picks one.
    """
    variant = request.param
    schema.install_package(variant)

    yield variant

    schema.install_package(SchemaCtx.Variant_No_Commit)

# ################################################################################################################################

@pytest.fixture
def facility(schema:'Schema') -> 'facility_gen':
    """ The source database, as its owner.
    """
    database = FacilityDatabase(schema)

    yield database

    database.close()

# ################################################################################################################################

@pytest.fixture
def records(schema:'Schema') -> 'records_gen':
    """ The target database, as its owner.
    """
    database = RecordsDatabase(schema)

    yield database

    database.close()

# ################################################################################################################################

@pytest.fixture
def sync(schema:'Schema') -> 'sync_gen':
    """ The mapping and the checkpoint, as the user the writer connection has.
    """
    database = SyncDatabase(schema)

    yield database

    database.close()

# ################################################################################################################################

@pytest.fixture
def faults(schema:'Schema') -> 'faults_gen':
    """ The fault plan the package and the triggers consult.
    """
    plan = FaultPlan(schema)

    yield plan

    plan.close()

# ################################################################################################################################
# ################################################################################################################################
