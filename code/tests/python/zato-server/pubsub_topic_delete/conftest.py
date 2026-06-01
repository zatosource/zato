# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import tempfile

# Zato
from zato.common.test.conftest_base_pubsub import create_zato_server_fixture, find_free_port

# ################################################################################################################################
# ################################################################################################################################

if 0:
    import logging
    from zato.common.test.conftest_base_pubsub import SessionState
    from zato.common.typing_ import anydict, strstrdict

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

    from zato.common.test.receiver import WebhookReceiver

    publisher_password       = 'test.pub.' + os.urandom(8).hex()
    subscriber_password      = 'test.sub.' + os.urandom(8).hex()
    push_subscriber_password = 'test.push.' + os.urandom(8).hex()

    # .. start the webhook receiver ..
    state.test_data_directory = tempfile.mkdtemp(prefix='zato_pubsub_topic_delete_data_')
    push_output_dir = os.path.join(state.test_data_directory, 'receivers', 'push')
    os.makedirs(push_output_dir, exist_ok=True)

    push_receiver_port = find_free_port()
    push_receiver = WebhookReceiver(push_receiver_port, push_output_dir)
    push_receiver.start()
    state.receivers.append(push_receiver)

    placeholders:'strstrdict' = {
        'publisher_password': publisher_password,
        'subscriber_password': subscriber_password,
        'push_subscriber_password': push_subscriber_password,
        'push_receiver_port': str(push_receiver_port),
    }

    def _populate(
        host:'str',
        server_port:'int',
        invoke_password:'str',
        server_directory:'str',
        zato_bin:'str',
    ) -> 'None':
        from zato.common.test.config_pubsub_topic_delete import TestConfig
        from zato.common.test.client import AdminClient

        TestConfig.base_url               = f'http://{host}:{server_port}'
        TestConfig.invoke_password        = invoke_password
        TestConfig.publisher_username     = 'test.td.publisher'
        TestConfig.publisher_password     = publisher_password
        TestConfig.subscriber_username    = 'test.td.subscriber'
        TestConfig.subscriber_password    = subscriber_password
        TestConfig.server_directory       = server_directory
        TestConfig.zato_bin               = zato_bin
        TestConfig.push_receiver          = push_receiver
        TestConfig.push_receiver_port     = push_receiver_port

        # .. look up the subscriber sec_base_id for use in tests ..
        admin = AdminClient(TestConfig.base_url, invoke_password)

        sec_list = admin.invoke('zato.security.get-list', {'cluster_id': 1})

        if isinstance(sec_list, list):
            sec_items = sec_list
        else:
            sec_items = sec_list['zato_security_get_list_response']

        for sec_item in sec_items:
            if sec_item['name'] == 'test.td.subscriber':
                TestConfig.subscriber_sec_base_id = sec_item['id']
                break

    out:'anydict' = {
        'placeholders': placeholders,
        'populate_callback': _populate,
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

zato_server = create_zato_server_fixture(
    logger_name='zato.test.pubsub_topic_delete.conftest',
    server_log_copy_name='server-logs-pubsub-topic-delete.txt',
    template_path=_template_path,
    quickstart_prefix='zato_pubsub_topic_delete_qs_',
    extra_server_env={},
    patch_server_conf_bind=True,
    build_config_callback=_build_config,
)

# ################################################################################################################################
# ################################################################################################################################
