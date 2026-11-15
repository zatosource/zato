# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import tempfile

# pytest
import pytest

# Zato
from zato.common.test.conftest_base_multi_cpu import create_multi_cpu_server_fixture, get_worker_count, \
    ModuleCtx as MultiCPUCtx, MultiCPUTestConfig, remove_interrupted_run_state
from zato.common.test.config_multi_cpu_pubsub import PubSubConfig
from zato.common.test.conftest_base_pubsub import find_free_port
from zato.common.test.receiver import WebhookReceiver
from zato.common.test.resume import pytest_runtest_protocol as pytest_runtest_protocol
from zato.common.test.resume import pytest_runtest_teardown as pytest_runtest_teardown

# ################################################################################################################################
# ################################################################################################################################

if 0:
    import logging
    from zato.common.test.conftest_base_pubsub import SessionState
    from zato.common.typing_ import any_, anydict, strlist, strstrdict

# ################################################################################################################################
# ################################################################################################################################

def _subscriber_name(index:'int') -> 'str':
    out = f'test.multi-cpu.sub.{index:02d}'
    return out

# ################################################################################################################################

def _build_template() -> 'str':
    """ Writes the enmasse template of the suite, with one security definition, outgoing connection and push
    subscription per subscriber, and returns its path.
    """
    lines:'strlist' = []

    # .. the security definitions ..
    lines.append('security:')

    for name in (PubSubConfig.Publisher_Name, PubSubConfig.Puller_Name, PubSubConfig.Waiter_Name, PubSubConfig.Joiner_Name):
        lines.append(f'  - name: {name}')
        lines.append('    type: basic_auth')
        lines.append(f'    username: {name}')
        lines.append('    password: "{{sec_password}}"')

    for index in range(PubSubConfig.Subscriber_Count):
        name = _subscriber_name(index)
        lines.append(f'  - name: {name}')
        lines.append('    type: basic_auth')
        lines.append(f'    username: {name}')
        lines.append('    password: "{{sec_password}}"')

    # .. the channels of the test services ..
    lines.append('channel_rest:')

    for service, path in (
        ('test.multi-cpu.worker-slot', '/test/multi-cpu/worker-slot'),
        ('test.multi-cpu.publish', '/test/multi-cpu/publish'),
        ('test.multi-cpu.blocking-pull', '/test/multi-cpu/blocking-pull'),
    ):
        lines.append(f'  - name: {service}')
        lines.append(f'    service: {service}')
        lines.append(f'    url_path: {path}')
        lines.append('    data_format: json')

    # .. one outgoing connection per receiver ..
    lines.append('outgoing_rest:')

    for index in range(PubSubConfig.Subscriber_Count):
        lines.append(f'  - name: {_subscriber_name(index)}.out')
        lines.append(f'    host: "http://127.0.0.1:{{{{port_{index:02d}}}}}"')
        lines.append(f'    url_path: /webhook/{index:02d}')
        lines.append('    data_format: json')
        lines.append('    timeout: 30')

    # .. the topics ..
    lines.append('pubsub_topic:')

    topic_names = (PubSubConfig.Push_Topic, PubSubConfig.Pull_Topic, PubSubConfig.Wake_Topic, PubSubConfig.Join_Topic,
        PubSubConfig.Lock_Topic)

    for topic_name in topic_names:
        lines.append(f'  - name: {topic_name}')

    # .. the permissions ..
    lines.append('pubsub_permission:')
    lines.append(f'  - security: {PubSubConfig.Publisher_Name}')
    lines.append('    pub:')
    lines.append('      - multi.cpu.**')
    lines.append(f'  - security: {PubSubConfig.Puller_Name}')
    lines.append('    sub:')
    lines.append(f'      - {PubSubConfig.Pull_Topic}')
    lines.append(f'  - security: {PubSubConfig.Waiter_Name}')
    lines.append('    sub:')
    lines.append(f'      - {PubSubConfig.Wake_Topic}')
    lines.append(f'  - security: {PubSubConfig.Joiner_Name}')
    lines.append('    sub:')
    lines.append(f'      - {PubSubConfig.Join_Topic}')

    for index in range(PubSubConfig.Subscriber_Count):
        lines.append(f'  - security: {_subscriber_name(index)}')
        lines.append('    sub:')
        lines.append(f'      - {PubSubConfig.Push_Topic}')

    # .. and the subscriptions.
    lines.append('pubsub_subscription:')

    for index in range(PubSubConfig.Subscriber_Count):
        name = _subscriber_name(index)
        lines.append(f'  - security: {name}')
        lines.append('    delivery_type: push')
        lines.append(f'    push_rest_endpoint: {name}.out')
        lines.append('    topic_list:')
        lines.append(f'      - {PubSubConfig.Push_Topic}')

    for name, topic_name in ((PubSubConfig.Puller_Name, PubSubConfig.Pull_Topic), (PubSubConfig.Waiter_Name, PubSubConfig.Wake_Topic)):
        lines.append(f'  - security: {name}')
        lines.append('    delivery_type: pull')
        lines.append('    topic_list:')
        lines.append(f'      - {topic_name}')

    directory = tempfile.mkdtemp(prefix='zato_multi_cpu_pubsub_template_')
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

    # .. one receiver per subscriber, each with a port and an output directory of its own ..
    state.test_data_directory = tempfile.mkdtemp(prefix='zato_multi_cpu_pubsub_data_')

    for index in range(PubSubConfig.Subscriber_Count):
        port = find_free_port()
        placeholders[f'port_{index:02d}'] = str(port)

        output_directory = os.path.join(state.test_data_directory, 'receivers', f'{index:02d}')
        os.makedirs(output_directory)

        receiver = WebhookReceiver(port, output_directory)
        receiver.start()

        state.receivers.append(receiver)
        PubSubConfig.receivers.append(receiver)

    logger.info('Receivers started: %d', PubSubConfig.Subscriber_Count)

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
    logger_name='zato.test.multi_cpu_pubsub.conftest',
    server_log_copy_name='server-logs-multi-cpu-pubsub.txt',
    template_path=_build_template(),
    quickstart_prefix='zato_multi_cpu_pubsub_qs_',
    worker_count=get_worker_count(),
    build_config_callback=_build_config,
)

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(autouse=True)
def clear_receivers() -> 'any_':
    """ Removes the deliveries of the previous test from every receiver.
    """
    for receiver in PubSubConfig.receivers:
        receiver.clear_output()

    yield

# ################################################################################################################################
# ################################################################################################################################
