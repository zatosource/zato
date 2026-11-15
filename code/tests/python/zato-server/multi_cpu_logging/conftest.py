# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# Zato
from zato.common.test.conftest_base_multi_cpu import create_multi_cpu_server_fixture, get_worker_count, \
    ModuleCtx as MultiCPUCtx, MultiCPUTestConfig, remove_interrupted_run_state
from zato.common.test.resume import pytest_runtest_protocol as pytest_runtest_protocol
from zato.common.test.resume import pytest_runtest_teardown as pytest_runtest_teardown

# ################################################################################################################################
# ################################################################################################################################

if 0:
    import logging
    from zato.common.test.conftest_base_pubsub import SessionState
    from zato.common.typing_ import anydict

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

    # The logging configuration that quickstart writes gives the server log a limit low enough for a test
    # to exceed it several times, and enough backups to keep every record that the test writes
    os.environ[MultiCPUCtx.Log_Max_Size_Env] = str(MultiCPUCtx.Log_Max_Size)
    os.environ[MultiCPUCtx.Log_Backup_Count_Env] = str(MultiCPUCtx.Log_Backup_Count)

    out:'anydict' = {
        'placeholders': {},
        'populate_callback': MultiCPUTestConfig.populate,
        'hot_deploy_sources': [MultiCPUCtx.Worker_Slot_Service_Path],
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

remove_interrupted_run_state()

zato_server = create_multi_cpu_server_fixture(
    logger_name='zato.test.multi_cpu_logging.conftest',
    server_log_copy_name='server-logs-multi-cpu-logging.txt',
    template_path=_template_path,
    quickstart_prefix='zato_multi_cpu_logging_qs_',
    worker_count=get_worker_count(),
    build_config_callback=_build_config,
)

# ################################################################################################################################
# ################################################################################################################################
