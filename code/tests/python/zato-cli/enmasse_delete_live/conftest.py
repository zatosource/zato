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
from zato.common.defaults import default_cluster_id

# Live environment
from live_containers.ready import wait_until
from live_environment.parts import Parts, tear_down
from live_environment.quickstart import ZatoEnvironment

# Zato - the suite's own parts
from _support import ModuleCtx as SupportCtx, Pickup, Runtime

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.client import AdminClient
    from zato.common.typing_ import strstrdict

# ################################################################################################################################
# ################################################################################################################################

zato_gen = Generator[ZatoEnvironment, None, None]

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The source of the service the suite deploys to read runtime state through
    Runtime_Service_Source = os.path.join(os.path.dirname(__file__), '_runtime_service.py')

    # The variable that keeps the enmasse process a pickup import spawns from reloading the server's configuration
    Reload_Variable = 'Zato_Needs_Config_Reload'
    Reload_Off      = 'False'

    # Where each environment of the suite is laid down
    Directory_Prefix = 'zato_enmasse_delete_live_'
    Password_Prefix  = 'test.enmasse.delete'

# ################################################################################################################################
# ################################################################################################################################

def server_environment() -> 'strstrdict':
    """ What the server of the suite runs with - the audit trail in SQLite, so that a configuration change is recorded.
    """
    out = {
        AuditLogCtx.Env_Enabled: 'True',
        AuditLogCtx.Env_Type:    AuditLogCtx.Type_SQLite,
    }
    return out

# ################################################################################################################################

def wait_for_runtime_service(client:'AdminClient') -> 'None':
    """ Waits until the server reports the runtime service as deployed.
    """
    def _is_deployed() -> 'bool':
        request = {'cluster_id': default_cluster_id, 'name': SupportCtx.Runtime_Service}
        response = client.invoke('zato.service.get-by-name', request)
        out = response['name'] == SupportCtx.Runtime_Service
        return out

    wait_until(_is_deployed, f'service {SupportCtx.Runtime_Service}')

# ################################################################################################################################

def start_environment(parts:'Parts', extra_environment:'strstrdict') -> 'ZatoEnvironment':
    """ Lays one quickstart environment down, starts its server with the pickup listener and deploys the runtime service.
    """
    directory = tempfile.mkdtemp(prefix=ModuleCtx.Directory_Prefix)

    out = ZatoEnvironment(directory, password_prefix=ModuleCtx.Password_Prefix)
    parts.add('zato environment', out.stop)

    out.create()
    out.start(extra_environment)

    with open(ModuleCtx.Runtime_Service_Source) as source_file:
        source = source_file.read()

    out.deploy(SupportCtx.Runtime_Service_File, source)
    wait_for_runtime_service(out.client())

    return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def environment() -> 'zato_gen':
    """ The one server of the session, its pickup listener and the runtime service.
    """
    parts = Parts()

    try:
        yield start_environment(parts, server_environment())
    finally:
        tear_down(parts)

# ################################################################################################################################

@pytest.fixture(scope='session')
def client(environment:'ZatoEnvironment') -> 'AdminClient':
    """ A client invoking services on the session's server.
    """
    out = environment.client()
    return out

# ################################################################################################################################

@pytest.fixture(scope='session')
def pickup(environment:'ZatoEnvironment') -> 'Pickup':
    """ Places enmasse files in the pickup directory of the session's server.
    """
    out = Pickup(environment)
    return out

# ################################################################################################################################

@pytest.fixture(scope='session')
def runtime(client:'AdminClient') -> 'Runtime':
    """ Reads runtime state of the session's server.
    """
    out = Runtime(client)
    return out

# ################################################################################################################################

@pytest.fixture(scope='module')
def reload_free_environment() -> 'zato_gen':
    """ A second server, which the enmasse process of a pickup import inherits Zato_Needs_Config_Reload=False from
    once the server has been restarted with it. It is created with the reload on, so that the objects a test creates
    through its pickup directory are at runtime before the restart.
    """
    parts = Parts()

    try:
        yield start_environment(parts, server_environment())
    finally:
        tear_down(parts)

# ################################################################################################################################

def reload_free_server_environment() -> 'strstrdict':
    """ What the second server is restarted with - the reload switched off for the enmasse processes it spawns.
    """
    out = server_environment()
    out[ModuleCtx.Reload_Variable] = ModuleCtx.Reload_Off
    return out

# ################################################################################################################################
# ################################################################################################################################
