# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys
import tempfile

# The state that the tests of the suite share
_suite_dir = os.path.dirname(__file__)
sys.path.insert(0, _suite_dir)

# pytest
import pytest

# Zato
from zato.common.test.conftest_base_multi_cpu import create_multi_cpu_server_fixture, get_worker_count, \
    ModuleCtx as MultiCPUCtx, MultiCPUTestConfig, remove_interrupted_run_state
from zato.common.test.conftest_base_pubsub import find_free_port
from zato.common.test.receiver import WebhookReceiver
from zato.common.test.resume import pytest_runtest_protocol as pytest_runtest_protocol
from zato.common.test.resume import pytest_runtest_teardown as pytest_runtest_teardown
from zato.common.worker_count import ServerWorkers

# Test helpers
from _suite import get_endpoint_name, get_subscriber_name, MigrationConfig

# ################################################################################################################################
# ################################################################################################################################

if 0:
    import logging
    from zato.common.test.conftest_base_pubsub import SessionState
    from zato.common.typing_ import any_, anydict, strlist, strstrdict

# ################################################################################################################################
# ################################################################################################################################

def _build_template() -> 'str':
    """ Writes the enmasse template of the suite, with one security definition, outgoing connection and push
    subscription per subscriber, each subscription with its delivery off, and returns its path.
    """
    lines:'strlist' = []

    # .. the security definitions ..
    lines.append('security:')
    lines.append(f'  - name: {MigrationConfig.Publisher_Name}')
    lines.append('    type: basic_auth')
    lines.append(f'    username: {MigrationConfig.Publisher_Name}')
    lines.append('    password: "{{sec_password}}"')

    for index in range(MigrationConfig.Subscriber_Count):
        name = get_subscriber_name(index)
        lines.append(f'  - name: {name}')
        lines.append('    type: basic_auth')
        lines.append(f'    username: {name}')
        lines.append('    password: "{{sec_password}}"')

    # .. the channel of the service that returns the slot of the worker that served the request ..
    lines.append('channel_rest:')
    lines.append('  - name: test.multi-cpu.migration.worker-slot')
    lines.append(f'    service: {MultiCPUCtx.Worker_Slot_Service}')
    lines.append(f'    url_path: {MultiCPUCtx.Worker_Slot_Path}')
    lines.append('    data_format: json')

    # .. one outgoing connection per receiver ..
    lines.append('outgoing_rest:')

    for index in range(MigrationConfig.Subscriber_Count):
        lines.append(f'  - name: {get_endpoint_name(index)}')
        lines.append(f'    host: "http://127.0.0.1:{{{{port_{index:02d}}}}}"')
        lines.append(f'    url_path: /webhook/{index:02d}')
        lines.append('    data_format: json')
        lines.append('    timeout: 30')

    # .. the topic ..
    lines.append('pubsub_topic:')
    lines.append(f'  - name: {MigrationConfig.Topic_Name}')

    # .. the permissions ..
    lines.append('pubsub_permission:')
    lines.append(f'  - security: {MigrationConfig.Publisher_Name}')
    lines.append('    pub:')
    lines.append(f'      - {MigrationConfig.Topic_Name}')

    for index in range(MigrationConfig.Subscriber_Count):
        lines.append(f'  - security: {get_subscriber_name(index)}')
        lines.append('    sub:')
        lines.append(f'      - {MigrationConfig.Topic_Name}')

    # .. and the subscriptions.
    lines.append('pubsub_subscription:')

    for index in range(MigrationConfig.Subscriber_Count):
        lines.append(f'  - security: {get_subscriber_name(index)}')
        lines.append('    delivery_type: push')
        lines.append(f'    push_rest_endpoint: {get_endpoint_name(index)}')
        lines.append('    is_delivery_active: false')
        lines.append('    topic_list:')
        lines.append(f'      - {MigrationConfig.Topic_Name}')

    directory = tempfile.mkdtemp(prefix='zato_multi_cpu_migration_template_')
    out = os.path.join(directory, '_enmasse_template.yaml')

    with open(out, 'w') as template_file:
        _ = template_file.write('\n'.join(lines) + '\n')

    return out

# ################################################################################################################################
# ################################################################################################################################

def _build_config(
    state:'SessionState',
    logger:'logging.Logger',
    zato_bin:'str',
    server_port:'int',
    invoke_password:'str',
) -> 'anydict':

    placeholders:'strstrdict' = {
        'sec_password': MultiCPUTestConfig.sec_password,
    }

    # .. the tests start the server again, so they keep its session ..
    MigrationConfig.state = state

    # .. one receiver per subscriber, each with a port and an output directory of its own ..
    state.test_data_directory = tempfile.mkdtemp(prefix='zato_multi_cpu_migration_data_')

    for index in range(MigrationConfig.Subscriber_Count):
        port = find_free_port()
        placeholders[f'port_{index:02d}'] = str(port)

        output_directory = os.path.join(state.test_data_directory, 'receivers', f'{index:02d}')
        os.makedirs(output_directory)

        receiver = WebhookReceiver(port, output_directory)
        receiver.start()

        state.receivers.append(receiver)
        MigrationConfig.receivers.append(receiver)

    logger.info('Receivers started: %d', MigrationConfig.Subscriber_Count)

    out:'anydict' = {
        'placeholders': placeholders,
        'populate_callback': MultiCPUTestConfig.populate,
        'hot_deploy_sources': [MultiCPUCtx.Worker_Slot_Service_Path],
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

remove_interrupted_run_state()

# The server of the suite starts as a server of one process, and the server inherits the environment of the test process
os.environ[ServerWorkers.Env_Key] = str(MigrationConfig.Single_Worker_Count)

zato_server = create_multi_cpu_server_fixture(
    logger_name='zato.test.multi_cpu_migration.conftest',
    server_log_copy_name='server-logs-multi-cpu-migration.txt',
    template_path=_build_template(),
    quickstart_prefix='zato_multi_cpu_migration_qs_',
    worker_count=get_worker_count(),
    build_config_callback=_build_config,
)

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(autouse=True)
def reset_receivers() -> 'any_':
    """ Removes the deliveries of the previous test from every receiver and makes every receiver accept again.
    """
    for receiver in MigrationConfig.receivers:
        receiver.clear_output()
        receiver.behavior.reset()

    yield

# ################################################################################################################################
# ################################################################################################################################
