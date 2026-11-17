# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import shutil
import tempfile

# pytest
import pytest

# Zato
from zato.common.audit_log.api import ModuleCtx as AuditLogCtx
from zato.common.crypto.api import CryptoManager
from zato.common.db_env.database_env import DatabaseEnv
from zato.common.test.client import AdminClient
from zato.common.test.conftest_base_pubsub import find_free_port, run_quickstart_and_enmasse, SessionState, \
    start_server_process
from zato.common.test.perf_report import Measurement, PerfSettingsError, report_result, start_measurement

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strstrdict

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The environment variable with the base directory of the repository
    Env_Base_Dir = 'ZATO_TEST_BASE_DIR'

    # The address that each server listens on
    Host = '127.0.0.1'

    # The name of the figures that the server with production settings records
    Result_Name = 'perf-gate'

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.durability.perf_gate')

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='module')
def parent_dir() -> 'any_':
    out = tempfile.mkdtemp(prefix='zato_perf_gate_', dir=os.environ['TMPDIR'])

    try:
        yield out
    finally:
        shutil.rmtree(out, ignore_errors=True)

# ################################################################################################################################

def _start_server(parent_dir:'str', name:'str', server_env:'strstrdict') -> 'tuple[SessionState, AdminClient]':
    """ Starts a server with a SQLite Zato database of its own and the given variables,
    and returns its state and a client of its services.
    """
    state = SessionState(f'zato.test.durability.perf_gate.{name}', f'server-logs-perf-gate-{name}.txt')
    zato_bin = os.path.join(os.environ[ModuleCtx.Env_Base_Dir], 'code', 'bin', 'zato')
    invoke_password = 'test.invoke.' + CryptoManager.generate_hex_string()
    server_port = find_free_port()

    server_directory = run_quickstart_and_enmasse(
        state=state,
        logger=logger,
        zato_bin=zato_bin,
        invoke_password=invoke_password,
        rendered_yaml='',
        quickstart_prefix=f'zato_perf_gate_{name}_',
        quickstart_parent_dir=parent_dir,
    )

    env = dict(server_env)
    env[DatabaseEnv.Env_Type] = DatabaseEnv.Type_SQLite
    env[DatabaseEnv.Env_Path] = os.path.join(server_directory, DatabaseEnv.File_Name)

    try:
        _ = start_server_process(
            state=state,
            logger=logger,
            zato_bin=zato_bin,
            server_directory=server_directory,
            server_port=server_port,
            broker_port=find_free_port(),
            extra_server_env=env,
            patch_server_conf_bind=True,
        )
    except Exception:
        state.cleanup()
        raise

    client = AdminClient(f'http://{ModuleCtx.Host}:{server_port}', invoke_password)

    out = (state, client)
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_audit_log_turned_off_is_refused(parent_dir:'str') -> 'None':
    """ A server whose audit log is turned off records no figure, neither when a measurement begins
    nor when its figures are reported.
    """
    state, client = _start_server(parent_dir, 'relaxed', {AuditLogCtx.Env_Enabled: 'false'})

    try:
        with pytest.raises(PerfSettingsError, match='is_audit_log_enabled'):
            _ = start_measurement(client, None)

        measurement = Measurement()
        measurement.client = client
        measurement.database = None
        measurement.settings_before = {}

        with pytest.raises(PerfSettingsError, match='is_audit_log_enabled'):
            _ = report_result(measurement, ModuleCtx.Result_Name, {'messages_per_second': 1})

    finally:
        state.cleanup()

# ################################################################################################################################

def test_production_settings_are_recorded(parent_dir:'str') -> 'None':
    """ A server with the settings of a production installation records its figures with those settings.
    """
    state, client = _start_server(parent_dir, 'production', {})

    try:
        measurement = start_measurement(client, None)
        record = report_result(measurement, ModuleCtx.Result_Name, {'messages_per_second': 1})

        assert record['figures'] == {'messages_per_second': 1}
        assert record['settings_before']['is_audit_log_enabled']
        assert record['settings_after']['pid'] != os.getpid()

    finally:
        state.cleanup()

# ################################################################################################################################
# ################################################################################################################################
