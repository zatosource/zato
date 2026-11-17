# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys

_here = os.path.dirname(os.path.abspath(__file__))
_lib_dir = os.path.abspath(os.path.join(_here, '..', '..', '..', 'zato-common', 'lib'))

sys.path.insert(0, _lib_dir)

# pytest
import pytest

# Zato
from pubsub_rest.capture import limit_captured_logs
from pubsub_rest.definition import Delivery_Pull
from pubsub_rest.runner import get_duration
from pubsub_rest.server import get_fixture_arguments, PubSubServer
from pubsub_rest.suite import define_traffic
from zato.common.test.conftest_base_pubsub import create_zato_server_fixture
from zato.common.test.direct_sql.pubsub_seed import get_seeded_sub_key, seed_queues, SeededQueue
from zato.common.test.pubsub_database import get_runtime_dir

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Generator
    from pubsub_rest.definition import Definition
    from zato.common.typing_ import anydict

    from zato.common.test.direct_sql.pubsub_seed import seeded_queue_list

    nonegen = Generator[None, None, None]

# ################################################################################################################################
# ################################################################################################################################

_server = PubSubServer('pubsub-admin-load')

# How many messages each of the topics that the administration works on holds,
# unless Zato_Test_Admin_Messages says otherwise.
_messages_per_topic = 250_000

# The topics that the administration works on, each with a pull subscriber of the same name.
_admin_topic_prefix = 'stability.admin'
_admin_topic_count = 4

# ################################################################################################################################
# ################################################################################################################################

def _setup(server:'PubSubServer', definition:'Definition') -> 'None':

    _ = define_traffic(server, definition)

    messages_per_topic = get_duration('Zato_Test_Admin_Messages', _messages_per_topic)

    queues:'seeded_queue_list' = []
    admin_topics:'anydict' = {}

    for topic_index in range(_admin_topic_count):
        topic_name = f'{_admin_topic_prefix}.{topic_index:04d}'
        _ = definition.add_pull_subscriber(topic_name, [topic_name])

        queue = SeededQueue(topic_name, Delivery_Pull, topic_name, messages_per_topic)
        queues.append(queue)

        admin_topics[topic_name] = get_seeded_sub_key(queue)

    # The topics hold their messages before the server starts.
    def seed_admin_topics(server_directory:'str') -> 'None':
        server.properties['seed_seconds'] = seed_queues(queues)

    server.pre_server_callback = seed_admin_topics
    server.properties['messages_per_topic'] = messages_per_topic
    server.properties['admin_topics'] = admin_topics

# ################################################################################################################################
# ################################################################################################################################

zato_server = create_zato_server_fixture(**get_fixture_arguments(_server, _setup, scope='module',
    quickstart_parent_dir=get_runtime_dir()))

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture
def server() -> 'PubSubServer':
    return _server

# ################################################################################################################################

@pytest.fixture(autouse=True)
def captured_log_level(request:'pytest.FixtureRequest', caplog:'pytest.LogCaptureFixture') -> 'nonegen':
    """ Keeps the warnings and errors only in the logs that pytest captures for the report of each test.
    """
    yield from limit_captured_logs(request, caplog)

# ################################################################################################################################
# ################################################################################################################################
