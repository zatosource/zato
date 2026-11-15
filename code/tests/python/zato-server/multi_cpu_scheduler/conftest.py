# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import atexit
import os
import sys
from tempfile import mkdtemp

# The shared libraries of the live suites
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'zato-common', 'lib'))

# Zato
from live_environment.scheduler import SchedulerProcess
from zato.common.test.conftest_base_multi_cpu import create_multi_cpu_server_fixture, get_worker_count, \
    ModuleCtx as MultiCPUCtx, MultiCPUTestConfig, remove_interrupted_run_state
from zato.common.test.config_multi_cpu_scheduler import SchedulerConfig
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

    # Every worker of the server appends the runs of the scheduled jobs to the file of this variable ..
    fire_log_path = os.path.join(mkdtemp(prefix='zato_multi_cpu_scheduler_'), 'fires.txt')
    os.environ[SchedulerConfig.Fire_Log_Env] = fire_log_path

    # .. and the scheduler runs on Redis streams of its own, which the server inherits the names of.
    scheduler = SchedulerProcess()
    scheduler.start()
    _ = atexit.register(scheduler.cleanup)

    os.environ.update(scheduler.server_environment())

    placeholders = {
        'interval_seconds': SchedulerConfig.Interval_Seconds,
        'slow_run_seconds': SchedulerConfig.Slow_Run_Seconds,
    }

    out:'anydict' = {
        'placeholders': placeholders,
        'populate_callback': MultiCPUTestConfig.populate,
        'hot_deploy_sources': [MultiCPUCtx.Worker_Slot_Service_Path],
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

remove_interrupted_run_state()

zato_server = create_multi_cpu_server_fixture(
    logger_name='zato.test.multi_cpu_scheduler.conftest',
    server_log_copy_name='server-logs-multi-cpu-scheduler.txt',
    template_path=_template_path,
    quickstart_prefix='zato_multi_cpu_scheduler_qs_',
    worker_count=get_worker_count(),
    build_config_callback=_build_config,
)

# ################################################################################################################################
# ################################################################################################################################
