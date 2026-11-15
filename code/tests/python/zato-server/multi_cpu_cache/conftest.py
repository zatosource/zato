# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from tempfile import mkdtemp

# Zato
from zato.common.test.conftest_base_multi_cpu import create_multi_cpu_server_fixture, get_worker_count, \
     ModuleCtx as MultiCPUCtx, MultiCPUTestConfig
from zato.common.test.config_multi_cpu_cache import CacheConfig

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

    # Every worker of the server appends the invocations of the cached service to the file of this variable
    invocation_log_path = os.path.join(mkdtemp(prefix='zato_multi_cpu_cache_'), 'invocations.txt')
    os.environ[CacheConfig.Invocation_Log_Env] = invocation_log_path

    out:'anydict' = {
        'placeholders': {},
        'populate_callback': MultiCPUTestConfig.populate,
        'hot_deploy_sources': [MultiCPUCtx.Worker_Slot_Service_Path],
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

zato_server = create_multi_cpu_server_fixture(
    logger_name='zato.test.multi_cpu_cache.conftest',
    server_log_copy_name='server-logs-multi-cpu-cache.txt',
    template_path=_template_path,
    quickstart_prefix='zato_multi_cpu_cache_qs_',
    worker_count=get_worker_count(),
    build_config_callback=_build_config,
)

# ################################################################################################################################
# ################################################################################################################################
