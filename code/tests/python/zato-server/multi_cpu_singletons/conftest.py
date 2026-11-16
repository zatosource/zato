# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import atexit
import os
from tempfile import mkdtemp

# PyYAML
import yaml

# Zato
from zato.common.audit_log.common import AuditSource, Env_Retention_Days_Prefix, get_source_env_suffix
from zato.common.audit_log.retention import Env_Archive_Dir
from zato.common.test.conftest_base_multi_cpu import create_multi_cpu_server_fixture, get_worker_count, \
    ModuleCtx as MultiCPUCtx, MultiCPUTestConfig, remove_interrupted_run_state
from zato.common.test.config_multi_cpu_singletons import SingletonsConfig
from zato.common.test.queue_bridge_stand_in import QueueBridgeStandIn
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

    # The enmasse file that the server imports at startup defines one channel ..
    startup_config = {
        'channel_rest': [{
            'name': SingletonsConfig.Startup_Channel_Name,
            'service': MultiCPUCtx.Worker_Slot_Service,
            'url_path': SingletonsConfig.Startup_Channel_Path,
            'data_format': 'json',
        }],
    }

    SingletonsConfig.deploy_root = mkdtemp(prefix='zato_multi_cpu_singletons_deploy_')

    enmasse_dir = os.path.join(SingletonsConfig.deploy_root, SingletonsConfig.Enmasse_Dir)
    os.mkdir(enmasse_dir)

    with open(os.path.join(enmasse_dir, SingletonsConfig.Startup_File_Name), 'w') as startup_file:
        _ = startup_file.write(yaml.safe_dump(startup_config, sort_keys=False))

    # .. and the start command reads the directory of the file from the environment that the server inherits.
    os.environ[SingletonsConfig.Deploy_From_Env] = SingletonsConfig.deploy_root

    # Audit log retention deletes every event of the REST channels written before it runs,
    # and archives each event it deletes into a directory of the suite.
    SingletonsConfig.archive_dir = mkdtemp(prefix='zato_multi_cpu_singletons_archive_')

    rest_channel_suffix = get_source_env_suffix(AuditSource.REST_Channel)
    os.environ[f'{Env_Retention_Days_Prefix}{rest_channel_suffix}'] = SingletonsConfig.Retention_Days
    os.environ[Env_Archive_Dir] = SingletonsConfig.archive_dir

    # The queue bridge client of every worker connects to the Redis server of a stand-in for the queue bridge,
    # and the service of the Kafka channel records each message in a file of the suite.
    stand_in = QueueBridgeStandIn()
    stand_in.start()
    _ = atexit.register(stand_in.stop)

    SingletonsConfig.bridge_stand_in = stand_in
    os.environ.update(stand_in.server_environment())
    os.environ[SingletonsConfig.Bridge_Record_Env] = os.path.join(stand_in.directory, SingletonsConfig.Bridge_Record_File)

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
    logger_name='zato.test.multi_cpu_singletons.conftest',
    server_log_copy_name='server-logs-multi-cpu-singletons.txt',
    template_path=_template_path,
    quickstart_prefix='zato_multi_cpu_singletons_qs_',
    worker_count=get_worker_count(),
    build_config_callback=_build_config,
)

# ################################################################################################################################
# ################################################################################################################################
