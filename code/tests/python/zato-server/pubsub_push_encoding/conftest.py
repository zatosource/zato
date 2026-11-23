# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import re
import sys
import tempfile

# The definition of the suite and the test endpoint are shared with other suites
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'zato-common', 'lib')))

# pytest
import pytest # noqa: E402

# Zato
from zato.common.crypto.api import CryptoManager # noqa: E402
from zato.common.test.conftest_base_pubsub import create_zato_server_fixture, find_free_port # noqa: E402

# Test support
from encoding_support import Broadcast_Topic, Edit_Topic, EncodingConfig, get_broadcast_subscribers, Held_Subscriber, \
    Retried_Subscriber, Retry_Subscriber, Retry_Topic, Sizes_Subscriber, Sizes_Topic # noqa: E402
from http_endpoint.endpoint import TestEndpoint # noqa: E402
from pubsub_rest.definition import Definition # noqa: E402

# ################################################################################################################################
# ################################################################################################################################

if 0:
    import logging
    from collections.abc import Iterator
    from zato.common.test.conftest_base_pubsub import SessionState
    from zato.common.test.receiver import WebhookReceiver
    from zato.common.typing_ import any_, anydict, strlist

    endpointgen   = Iterator[TestEndpoint]
    receiver_list = list[WebhookReceiver]
    strtuplelist  = list[tuple[str, str]]

# ################################################################################################################################
# ################################################################################################################################

_publisher_username = 'test.encoding.publisher'

# A request of the publisher carries a payload of several MiB, escaped as JSON, so the server accepts requests of up to 64 MiB
_server_env = {
    'Zato_TCP_Max_Msg_Size': '64',
}

# What a test name is reduced to before it becomes a part of a path
_path_unsafe = re.compile(r'[^a-zA-Z0-9]+')

# ################################################################################################################################
# ################################################################################################################################

def _get_subscribers() -> 'strtuplelist':
    """ Returns each subscriber of the suite with the topic it subscribes to.
    """
    out:'strtuplelist' = []

    for name in get_broadcast_subscribers():
        out.append((name, Broadcast_Topic))

    out.append((Sizes_Subscriber, Sizes_Topic))
    out.append((Held_Subscriber, Edit_Topic))
    out.append((Retried_Subscriber, Edit_Topic))
    out.append((Retry_Subscriber, Retry_Topic))

    return out

# ################################################################################################################################

def _get_receivers() -> 'receiver_list':
    out:'receiver_list' = []

    for receivers in EncodingConfig.receivers.values():
        for receiver in receivers:
            out.append(receiver)

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

    state.test_data_directory = tempfile.mkdtemp(prefix='zato_pubsub_push_encoding_data_')

    definition = Definition()

    # Each subscriber has a receiver of its own, on a port of its own ..
    for name, topic_name in _get_subscribers():

        port = find_free_port()
        output_directory = os.path.join(state.test_data_directory, 'receivers', name)
        os.makedirs(output_directory, exist_ok=True)

        receiver = WebhookReceiver(port, output_directory)
        receiver.start()
        state.receivers.append(receiver)

        topic_receivers = EncodingConfig.receivers.setdefault(topic_name, [])
        topic_receivers.append(receiver)
        EncodingConfig.receiver_by_subscriber[name] = receiver

        url_path = f'/webhook/{name}'
        _ = definition.add_push_subscriber(name, [topic_name], port, url_path)

    receiver_count = len(state.receivers)
    logger.info('Receivers started: %d', receiver_count)

    # .. and the publisher may publish to every topic of the suite.
    topic_names:'strlist' = [Broadcast_Topic, Sizes_Topic, Edit_Topic, Retry_Topic]
    publisher = definition.add_publisher(_publisher_username, topic_names)

    def _populate(
        host:'str',
        server_port:'int',
        invoke_password:'str',
        server_directory:'str',
        zato_bin:'str',
    ) -> 'None':
        EncodingConfig.base_url           = f'http://{host}:{server_port}'
        EncodingConfig.invoke_password    = invoke_password
        EncodingConfig.publisher_username = publisher.username
        EncodingConfig.publisher_password = publisher.password

    enmasse_yaml = definition.to_yaml()

    out:'anydict' = {
        'placeholders': {},
        'enmasse_yaml': enmasse_yaml,
        'populate_callback': _populate,
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

zato_server = create_zato_server_fixture(
    logger_name='zato.test.pubsub_push_encoding.conftest',
    server_log_copy_name='server-logs.txt',
    template_path='',
    quickstart_prefix='zato_pubsub_push_encoding_qs_',
    extra_server_env=_server_env,
    patch_server_conf_bind=False,
    build_config_callback=_build_config,
)

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(autouse=True)
def clear_all_outputs() -> 'any_':
    """ Clears the pub/sub database, the behavior of each receiver and every delivered message before each test.
    """
    from zato.common.test import pubsub_db
    from zato.common.test.receiver import wait_until_receivers_quiet

    # Nothing that a previous test published is in flight when a test starts ..
    pubsub_db.delete_all_messages()

    receivers = _get_receivers()
    wait_until_receivers_quiet(receivers)

    # .. and every receiver accepts each request with no output from a previous test.
    for receiver in receivers:
        receiver.behavior.reset()
        receiver.clear_output()

    yield

# ################################################################################################################################

@pytest.fixture(scope='session')
def endpoint() -> 'endpointgen':
    """ The local endpoint that the transport tests send to, with its certificates in a directory of their own.
    """
    directory = tempfile.mkdtemp(prefix='zato-pubsub-push-encoding-')
    certificates_directory = os.path.join(directory, 'certificates')

    out = TestEndpoint(certificates_directory)
    out.start()

    yield out

    out.stop()
    os.rmdir(directory)

# ################################################################################################################################

@pytest.fixture
def path(request:'pytest.FixtureRequest') -> 'str':
    """ A path that no other test uses, so that each test reads only the requests that it sent.
    """
    name = _path_unsafe.sub('-', request.node.name)
    suffix = CryptoManager.generate_hex_string(32)

    out = f'/test/{name}/{suffix}'
    return out

# ################################################################################################################################
# ################################################################################################################################
