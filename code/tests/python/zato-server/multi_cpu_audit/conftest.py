# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import atexit
import os
import sys

# The helpers that start the containers of the suite and the state that the tests of the suite share
_suite_dir = os.path.dirname(__file__)
_common_lib_dir = os.path.abspath(os.path.join(_suite_dir, '..', '..', 'zato-common', 'lib'))

sys.path.insert(0, _suite_dir)
sys.path.insert(0, _common_lib_dir)

# Zato
from zato.common.audit_log.common import AuditSource
from zato.common.audit_log.export.config import ModuleCtx as ExportCtx
from zato.common.test.conftest_base_multi_cpu import create_multi_cpu_server_fixture, get_worker_count, \
    ModuleCtx as MultiCPUCtx, MultiCPUTestConfig, remove_interrupted_run_state
from zato.common.test.conftest_base_pubsub import find_free_port
from zato.common.test.resume import pytest_runtest_protocol as pytest_runtest_protocol
from zato.common.test.resume import pytest_runtest_teardown as pytest_runtest_teardown

# Test helpers
from _suite import AuditSuite
from live_otel.containers import remove_container, start_collector
from live_sql.containers import start_postgresql, stop_container
from live_sql.env import build_env

# ################################################################################################################################
# ################################################################################################################################

if 0:
    import logging
    from zato.common.test.conftest_base_pubsub import SessionState
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The variable that selects the audit database of the run, SQLite unless it names PostgreSQL
    Audit_DB_Env = 'Zato_Test_Multi_CPU_Audit_DB'
    Audit_DB_PostgreSQL = 'postgresql'

    Env_Prefix = 'Zato_Audit_Log_DB_'

    PostgreSQL_Container = 'zato-multi-cpu-audit-postgresql'
    Collector_Container  = 'zato-multi-cpu-audit-otel'

    Username = 'zato_multi_cpu_audit'
    DB_Name  = 'zato_multi_cpu_audit'

# ################################################################################################################################
# ################################################################################################################################

_template_path = os.path.join(os.path.dirname(__file__), '_enmasse_template.yaml')

# ################################################################################################################################
# ################################################################################################################################

def _build_config(
    state:'SessionState',
    logger:'logging.Logger',
    zato_bin:'str',
    server_port:'int',
    invoke_password:'str',
) -> 'anydict':

    out:'anydict' = {
        'placeholders': {},
        'populate_callback': MultiCPUTestConfig.populate,
        'hot_deploy_sources': [MultiCPUCtx.Worker_Slot_Service_Path],
    }

    # Every worker exports the events of the REST channels to the collector of the suite ..
    collector = start_collector(ModuleCtx.Collector_Container)
    _ = atexit.register(remove_container, collector.container_name)

    AuditSuite.collector_output_path = collector.output_path

    os.environ.update({
        ExportCtx.Env_Endpoint: collector.http_endpoint,
        ExportCtx.Env_Protocol: ExportCtx.Protocol_HTTP,
        ExportCtx.Env_SSL_CA_File: collector.ca_file,
        ExportCtx.Env_Headers: f'Authorization=Bearer {collector.bearer_token}',
        ExportCtx.Env_Sources: AuditSource.REST_Channel,
    })

    # .. and a run on PostgreSQL writes the events of every worker to a database of its own, in memory, removed at exit
    if os.environ.get(ModuleCtx.Audit_DB_Env) == ModuleCtx.Audit_DB_PostgreSQL:

        server = start_postgresql(
            container_name=ModuleCtx.PostgreSQL_Container,
            port=find_free_port(),
            username=ModuleCtx.Username,
            password=MultiCPUTestConfig.sec_password,
            db_name=ModuleCtx.DB_Name,
            needs_ssl=False,
            is_in_memory=True,
        )
        _ = atexit.register(stop_container, server.container_name)

        out['audit_db_env'] = build_env(ModuleCtx.Env_Prefix, server.details)
        logger.info('Audit database container: %s', server.container_name)

    return out

# ################################################################################################################################
# ################################################################################################################################

remove_interrupted_run_state()

zato_server = create_multi_cpu_server_fixture(
    logger_name='zato.test.multi_cpu_audit.conftest',
    server_log_copy_name='server-logs-multi-cpu-audit.txt',
    template_path=_template_path,
    quickstart_prefix='zato_multi_cpu_audit_qs_',
    worker_count=get_worker_count(),
    build_config_callback=_build_config,
)

# ################################################################################################################################
# ################################################################################################################################
