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
    from zato.common.typing_ import any_, anydict, strstrdict

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

    publisher_password  = 'test.pub.' + os.urandom(8).hex()
    subscriber_password = 'test.sub.' + os.urandom(8).hex()

    # .. allocate port and start the webhook receiver ..
    webhook_port = find_free_port()

    state.test_data_directory = tempfile.mkdtemp(prefix='zato_pubsub_sub_edit_data_')
    webhook_output_directory = os.path.join(state.test_data_directory, 'webhook')
    os.makedirs(webhook_output_directory, exist_ok=True)

    receiver = WebhookReceiver(webhook_port, webhook_output_directory)
    receiver.start()
    state.receivers.append(receiver)

    logger.info('Webhook receiver started on port %d', webhook_port)

    placeholders:'strstrdict' = {
        'publisher_password': publisher_password,
        'subscriber_password': subscriber_password,
        'webhook_port': str(webhook_port),
    }

    def _populate(
        host:'str',
        server_port:'int',
        invoke_password:'str',
        server_directory:'str',
        zato_bin:'str',
    ) -> 'None':
        from zato.common.test.config_pubsub_sub_edit import TestConfig
        from zato.common.test.client import AdminClient

        TestConfig.base_url                 = f'http://{host}:{server_port}'
        TestConfig.invoke_password          = invoke_password
        TestConfig.publisher_username       = 'test.sub.edit.publisher'
        TestConfig.publisher_password       = publisher_password
        TestConfig.subscriber_username      = 'test.sub.edit.subscriber'
        TestConfig.subscriber_password      = subscriber_password
        TestConfig.server_directory         = server_directory
        TestConfig.zato_bin                 = zato_bin
        TestConfig.webhook_port             = webhook_port
        TestConfig.webhook_output_directory = webhook_output_directory

        # .. look up the subscriber sec_base_id for use in tests ..
        admin = AdminClient(TestConfig.base_url, invoke_password)

        sec_list = admin.invoke('zato.security.get-list', {'cluster_id': 1})

        if isinstance(sec_list, list):
            sec_items = sec_list
        else:
            sec_items = sec_list['zato_security_get_list_response']

        for sec_item in sec_items:
            if sec_item['name'] == 'test.sub.edit.subscriber':
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
    logger_name='zato.test.pubsub_sub_edit.conftest',
    server_log_copy_name='server-logs-pubsub-sub-edit.txt',
    template_path=_template_path,
    quickstart_prefix='zato_pubsub_sub_edit_qs_',
    extra_server_env={},
    patch_server_conf_bind=True,
    build_config_callback=_build_config,
)

# ################################################################################################################################
# ################################################################################################################################
