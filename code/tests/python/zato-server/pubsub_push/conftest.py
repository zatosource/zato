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
from zato.common.crypto.api import CryptoManager
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

_topic_names = [
    'iam.user.created',
    'iam.user.deleted',
    'iam.role.assigned',
    'iam.password.changed',
    'iam.login.failed',
    'customer.registered',
    'customer.updated',
    'customer.deactivated',
    'order.placed',
    'order.shipped',
]

# ################################################################################################################################
# ################################################################################################################################

def _topic_to_key(topic_name:'str') -> 'str':
    """ Converts a topic name like 'iam.user.created' to a placeholder key like 'iam_user_created'.
    """
    out = topic_name.replace('.', '_')
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

    from zato.common.test.receiver import WebhookReceiver
    from zato.common.test.config_pubsub_push import EndpointConfig

    publisher_password = 'test.pub.' + CryptoManager.generate_hex_string()
    puller_password    = 'test.pull.' + CryptoManager.generate_hex_string()

    subscriber_passwords:'strstrdict' = {}

    for topic_name in _topic_names:
        key = _topic_to_key(topic_name)
        subscriber_passwords[key] = 'test.sub.' + CryptoManager.generate_hex_string()

    # .. allocate ports and start receivers ..
    state.test_data_directory = tempfile.mkdtemp(prefix='zato_pubsub_push_data_')

    from zato.common.test.config_pubsub_push import endpoint_config_dict as endpoint_config_dict_type
    endpoints:'endpoint_config_dict_type' = {}
    placeholders:'strstrdict' = {}

    placeholders['publisher_password'] = publisher_password
    placeholders['puller_password'] = puller_password

    for topic_name in _topic_names:
        key = _topic_to_key(topic_name)

        # .. password placeholder ..
        placeholders[f'sub_{key}_password'] = subscriber_passwords[key]

        # .. port placeholder ..
        port = find_free_port()
        placeholders[f'port_{key}'] = str(port)

        # .. output directory ..
        output_directory = os.path.join(state.test_data_directory, 'receivers', key)
        os.makedirs(output_directory, exist_ok=True)

        # .. start the receiver ..
        receiver = WebhookReceiver(port, output_directory)
        receiver.start()
        state.receivers.append(receiver)

        endpoint_config = EndpointConfig(
            port=port,
            output_directory=output_directory,
            receiver=receiver,
        )
        endpoints[topic_name] = endpoint_config

    logger.info('Receivers started: %d', len(_topic_names))

    def _populate(
        host:'str',
        server_port:'int',
        invoke_password:'str',
        server_directory:'str',
        zato_bin:'str',
    ) -> 'None':
        from zato.common.test.config_pubsub_push import TestConfig

        TestConfig.base_url             = f'http://{host}:{server_port}'
        TestConfig.password             = invoke_password
        TestConfig.publisher_username   = 'test.pubsub.publisher'
        TestConfig.publisher_password   = publisher_password
        TestConfig.puller_username      = 'test.pubsub.puller'
        TestConfig.puller_password      = puller_password
        TestConfig.server_directory     = server_directory
        TestConfig.endpoints            = endpoints

    out:'anydict' = {
        'placeholders': placeholders,
        'populate_callback': _populate,
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

zato_server = create_zato_server_fixture(
    logger_name='zato.test.pubsub_push.conftest',
    server_log_copy_name='server-logs.txt',
    template_path=_template_path,
    quickstart_prefix='zato_pubsub_push_qs_',
    extra_server_env={},
    patch_server_conf_bind=False,
    build_config_callback=_build_config,
)

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(autouse=True)
def clear_all_outputs() -> 'any_':
    """ Trims Redis pub/sub streams and clears all delivered message files before each test.
    """
    # redis
    from redis import Redis

    # Zato
    from zato.common.api import PubSub
    from zato.common.test.config_pubsub_push import TestConfig

    # .. trim all pub/sub streams to 0 so no in-flight deliveries leak across tests ..
    redis_client = Redis(host='localhost', port=6379, db=PubSub.Test_Redis_DB, decode_responses=True)

    for key in redis_client.scan_iter('zato:pubsub:stream:*'):
        _ = redis_client.xtrim(key, maxlen=0)

    redis_client.close()

    # .. then clear receiver output directories ..
    for endpoint_config in TestConfig.endpoints.values():
        endpoint_config.receiver.clear_output()

    yield

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture()
def reset_receivers() -> 'any_':
    """ Resets all receivers to accept mode before the test, then clears output.
    """
    from zato.common.test.config_pubsub_push import TestConfig

    for endpoint_config in TestConfig.endpoints.values():
        endpoint_config.receiver.behavior.reset()
        endpoint_config.receiver.clear_output()

    yield

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture()
def drain_pull_queue() -> 'any_':
    """ Drains the pull queue so the test starts with zero pending messages.
    """
    from zato.common.test.client import PullClient
    from zato.common.test.config_pubsub_push import TestConfig

    client = PullClient(TestConfig.base_url, TestConfig.puller_username, TestConfig.puller_password)
    client.drain()

    yield

# ################################################################################################################################
# ################################################################################################################################
