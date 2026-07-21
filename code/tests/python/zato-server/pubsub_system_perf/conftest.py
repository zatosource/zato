# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys
import tempfile

# Make the shared perf floors and helpers importable, the same way
# the backend perf suites do it.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'zato-common', 'lib')))

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.test.config_pubsub_system_perf import Publisher_Username, Latency_Topic_Name, Service_Count, \
    Service_Name_Template, Sub_Count, Sub_Security_Template, Topic_Count, Topic_Name_Template
from zato.common.test.conftest_base_pubsub import create_zato_server_fixture

# ################################################################################################################################
# ################################################################################################################################

if 0:
    import logging
    from zato.common.test.conftest_base_pubsub import SessionState
    from zato.common.typing_ import anydict, strstrdict

# ################################################################################################################################
# ################################################################################################################################

_services_source = os.path.join(os.path.dirname(__file__), '_services.py')

# ################################################################################################################################
# ################################################################################################################################

def _build_enmasse_yaml() -> 'str':
    """ Builds the enmasse YAML for the whole topology - one publisher, 200 topics,
    1,000 subscriber security definitions and 1,000 push subscriptions whose
    targets rotate over the 500 receiver services.
    """
    lines = []

    # .. security definitions - the publisher and one per subscription ..
    lines.append('security:')
    lines.append('')
    lines.append(f'  - name: {Publisher_Username}')
    lines.append('    type: basic_auth')
    lines.append(f'    username: {Publisher_Username}')
    lines.append('    password: "{{publisher_password}}"')

    for index in range(1, Sub_Count + 1):
        security_name = Sub_Security_Template.format(index)
        lines.append('')
        lines.append(f'  - name: {security_name}')
        lines.append('    type: basic_auth')
        lines.append(f'    username: {security_name}')
        lines.append('    password: "{{sub_password}}"')

    # .. topics, including the no-subscriber latency topic ..
    lines.append('')
    lines.append('pubsub_topic:')
    lines.append('')

    for index in range(1, Topic_Count + 1):
        lines.append(f'  - name: {Topic_Name_Template.format(index)}')

    lines.append(f'  - name: {Latency_Topic_Name}')

    # .. permissions - the publisher publishes anywhere under the prefix,
    # .. each subscriber may subscribe anywhere under it ..
    lines.append('')
    lines.append('pubsub_permission:')
    lines.append('')
    lines.append(f'  - security: {Publisher_Username}')
    lines.append('    pub:')
    lines.append('      - system.perf.**')

    for index in range(1, Sub_Count + 1):
        security_name = Sub_Security_Template.format(index)
        lines.append('')
        lines.append(f'  - security: {security_name}')
        lines.append('    sub:')
        lines.append('      - system.perf.**')

    # .. subscriptions - subscription i sits on topic ((i-1) % 200) + 1
    # .. and pushes into service ((i-1) % 500) + 1 ..
    lines.append('')
    lines.append('pubsub_subscription:')

    for index in range(1, Sub_Count + 1):
        security_name = Sub_Security_Template.format(index)
        topic_name = Topic_Name_Template.format(((index - 1) % Topic_Count) + 1)
        service_name = Service_Name_Template.format(((index - 1) % Service_Count) + 1)

        lines.append('')
        lines.append(f'  - security: {security_name}')
        lines.append('    delivery_type: push')
        lines.append('    push_type: service')
        lines.append(f'    push_service_name: {service_name}')
        lines.append('    topic_list:')
        lines.append(f'      - {topic_name}')

    lines.append('')
    return '\n'.join(lines)

# ################################################################################################################################

def _write_template() -> 'str':
    """ Writes the generated enmasse YAML to a temporary file and returns its path.
    """
    template_dir = tempfile.mkdtemp(prefix='zato_system_perf_template_')
    template_path = os.path.join(template_dir, 'enmasse.yaml')

    with open(template_path, 'w') as template_file:
        _ = template_file.write(_build_enmasse_yaml())

    return template_path

# ################################################################################################################################
# ################################################################################################################################

_template_path = _write_template()

# ################################################################################################################################
# ################################################################################################################################

def _build_config(
    state:'SessionState',
    logger:'logging.Logger',
    zato_bin:'str',
    server_port:'int',
    invoke_password:'str',
) -> 'anydict':

    publisher_password = 'test.pub.' + CryptoManager.generate_hex_string()
    sub_password = 'test.sub.' + CryptoManager.generate_hex_string()

    placeholders:'strstrdict' = {
        'publisher_password': publisher_password,
        'sub_password': sub_password,
    }

    def _populate(
        host:'str',
        server_port:'int',
        invoke_password:'str',
        server_directory:'str',
        zato_bin:'str',
    ) -> 'None':
        from zato.common.test.config_pubsub_system_perf import TestConfig

        TestConfig.base_url           = f'http://{host}:{server_port}'
        TestConfig.invoke_password    = invoke_password
        TestConfig.publisher_username = Publisher_Username
        TestConfig.publisher_password = publisher_password
        TestConfig.server_directory   = server_directory

    out:'anydict' = {
        'placeholders': placeholders,
        'populate_callback': _populate,
        'hot_deploy_sources': [_services_source],
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

zato_server = create_zato_server_fixture(
    logger_name='zato.test.pubsub_system_perf.conftest',
    server_log_copy_name='server-logs-pubsub-system-perf.txt',
    template_path=_template_path,
    quickstart_prefix='zato_pubsub_system_perf_qs_',
    extra_server_env={},
    patch_server_conf_bind=False,
    build_config_callback=_build_config,
)

# ################################################################################################################################
# ################################################################################################################################
