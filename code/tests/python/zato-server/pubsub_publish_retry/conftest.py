# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys
import tempfile

# The modules next to this one are imported by name, which is what puts them within reach
sys.path.insert(0, os.path.dirname(__file__))

# pytest
import pytest

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.test.conftest_base_pubsub import create_zato_server_fixture, find_free_port

# local
from _helpers import get_client, set_behaviour, TestConfig, Topic_REST, Topic_Service, wait_for_empty_queue

# ################################################################################################################################
# ################################################################################################################################

if 0:
    import logging
    from zato.common.test.conftest_base_pubsub import SessionState
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

_template_path = os.path.join(os.path.dirname(__file__), '_enmasse_template.yaml')
_services_source = os.path.join(os.path.dirname(__file__), '_services.py')

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

    publisher_password = 'test.pub.' + CryptoManager.generate_hex_string()
    subscriber_password = 'test.sub.' + CryptoManager.generate_hex_string()
    rest_subscriber_password = 'test.rest.' + CryptoManager.generate_hex_string()

    # The REST push subscription has a target of its own ..
    state.test_data_directory = tempfile.mkdtemp(prefix='zato_pubsub_publish_retry_data_')
    output_directory = os.path.join(state.test_data_directory, 'receiver')
    os.makedirs(output_directory, exist_ok=True)

    rest_port = find_free_port()

    receiver = WebhookReceiver(rest_port, output_directory)
    receiver.start()
    state.receivers.append(receiver)

    logger.info('Receiver started on port %d', rest_port)

    placeholders = {
        'publisher_password': publisher_password,
        'subscriber_password': subscriber_password,
        'rest_subscriber_password': rest_subscriber_password,
        'port_rest': str(rest_port),
    }

    def _populate(
        host:'str',
        server_port:'int',
        invoke_password:'str',
        server_directory:'str',
        zato_bin:'str',
    ) -> 'None':

        TestConfig.base_url = f'http://{host}:{server_port}'
        TestConfig.password = invoke_password
        TestConfig.server_directory = server_directory
        TestConfig.receiver = receiver

    out:'anydict' = {
        'placeholders': placeholders,
        'populate_callback': _populate,
        'hot_deploy_sources': [_services_source],
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

zato_server = create_zato_server_fixture(
    logger_name='zato.test.pubsub_publish_retry.conftest',
    server_log_copy_name='server-logs-pubsub-publish-retry.txt',
    template_path=_template_path,
    quickstart_prefix='zato_pubsub_publish_retry_qs_',
    extra_server_env={},
    patch_server_conf_bind=False,
    build_config_callback=_build_config,
)

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(autouse=True)
def reset_targets() -> 'any_':
    """ Every test starts with a target service that accepts everything and remembers nothing, a receiver
    that does the same, and nothing waiting in either topic's queue.
    """
    client = get_client()

    set_behaviour(client, 0)

    receiver = TestConfig.receiver
    receiver.behavior.reset()
    receiver.clear_output()

    # A previous test that left a message behind would have it delivered during this one
    pending_service = wait_for_empty_queue(client, Topic_Service)
    pending_rest = wait_for_empty_queue(client, Topic_REST)

    assert pending_service == 0, f'Messages still pending for {Topic_Service} -> {pending_service}'
    assert pending_rest == 0, f'Messages still pending for {Topic_REST} -> {pending_rest}'

    yield

# ################################################################################################################################
# ################################################################################################################################
