# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from tempfile import mkdtemp

# PyYAML
import yaml

# Zato
from zato.common.test.conftest_base_multi_cpu import create_multi_cpu_server_fixture, get_worker_count, \
    ModuleCtx as MultiCPUCtx, MultiCPUTestConfig, remove_interrupted_run_state
from zato.common.test.config_multi_cpu_singletons import SingletonsConfig
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
