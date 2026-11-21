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
sys.path.insert(0, os.path.dirname(__file__))

# pytest
import pytest

# Zato
from zato.common.audit_log.api import ModuleCtx as AuditLogCtx
from zato.common.db_env.database_env import DatabaseEnv
from zato.common.test.pubsub_database import get_db_mode, is_postgresql_mode, start_pubsub_database, stop_pubsub_database

# Live environment
from live_containers.ready import wait_until
from live_environment.parts import Parts, tear_down
from live_environment.quickstart import ZatoEnvironment

# Local
from _support import ModuleCtx as SupportCtx, Names, Pickup, Runtime, render_template

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

zato_gen = Generator[ZatoEnvironment, None, None]

_template_path = os.path.join(os.path.dirname(__file__), '_enmasse_template.yaml')
_runtime_source = os.path.join(os.path.dirname(__file__), '_runtime_service.py')

# ################################################################################################################################
# ################################################################################################################################

class SuiteCtx:

    Directory_Prefix = 'zato_ha_pubsub_subscription_'
    Password_Prefix = 'test.ha.pubsub.subscription'
    Database_Label = 'ha-pubsub-subscription'

# ################################################################################################################################
# ################################################################################################################################

def server_environment(database:'PubSubDatabase | None') -> 'strstrdict':
    """ Returns the environment variables of the live server of the suite.
    """
    out = {
        AuditLogCtx.Env_Enabled: 'True',
    }

    if database is None:
        out[DatabaseEnv.Env_Type] = DatabaseEnv.Type_SQLite
    else:
        out.update(database.env)

    return out

# ################################################################################################################################

def wait_for_runtime_service(client:'AdminClient') -> 'None':
    """ Waits until the runtime service is deployed.
    """
    def _is_deployed() -> 'bool':
        request = {'name': SupportCtx.Runtime_Service}
        response = client.invoke('zato.service.get-by-name', request)
        out = response['name'] == SupportCtx.Runtime_Service
        return out

    wait_until(_is_deployed, f'service {SupportCtx.Runtime_Service}')

# ################################################################################################################################

def start_environment(parts:'Parts', extra_environment:'strstrdict', names:'Names') -> 'ZatoEnvironment':
    """ Starts a live server with the initial subscriptions and the runtime service.
    """
    directory = tempfile.mkdtemp(prefix=SuiteCtx.Directory_Prefix)

    out = ZatoEnvironment(directory, password_prefix=SuiteCtx.Password_Prefix)
    parts.add('zato environment', out.stop)

    out.create()
    out.start(extra_environment)

    with open(_runtime_source) as source_file:
        source = source_file.read()

    out.deploy(SupportCtx.Runtime_Service_File, source)
    wait_for_runtime_service(out.client())

    yaml = render_template(_template_path, names.placeholders())
    _ = out.import_yaml('initial.yaml', yaml)

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
def environment(names:'Names') -> 'zato_gen':
    """ A live server on SQLite or on PostgreSQL with the initial subscriptions of the suite.
    """
    parts = Parts()
    database = None
    mode = get_db_mode()

    try:
        if is_postgresql_mode(mode):
            database = start_pubsub_database(SuiteCtx.Database_Label, mode)
            parts.add('pubsub database', lambda: stop_pubsub_database(database))

        yield start_environment(parts, server_environment(database), names)

    finally:
        tear_down(parts)

# ################################################################################################################################

@pytest.fixture(scope='module')
def client(environment:'ZatoEnvironment') -> 'AdminClient':
    """ A client of the module's live server.
    """
    out = environment.client()
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
    """ The runtime service of the live server.
    """
    out = Runtime(client)
    return out

# ################################################################################################################################
# ################################################################################################################################
