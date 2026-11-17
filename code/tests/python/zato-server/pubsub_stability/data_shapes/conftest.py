# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# Zato
from pubsub_rest.capture import limit_captured_logs
from pubsub_rest.server import get_fixture_arguments, PubSubServer
from zato.common.test.conftest_base_pubsub import create_zato_server_fixture
from zato.common.test.pubsub_database import get_runtime_dir

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Generator
    from pubsub_rest.definition import Definition
    from pubsub_rest.transport import Credentials
    from zato.common.typing_ import strlist

    nonegen = Generator[None, None, None]

# ################################################################################################################################
# ################################################################################################################################

_server = PubSubServer('pubsub-data-shapes')

# The permissions of every client of the suite.
_all_topics = ['shapes.**']

# The topics with one subscriber each.
_single_topics = ['shapes.large', 'shapes.binary', 'shapes.mixed']

# How many topics the topic scenario uses.
_topic_count = 10_000

# How many subscribers one topic fans out to.
_fan_out_subscriber_count = 1_000
_fan_out_topic = 'shapes.fan-out'

# ################################################################################################################################
# ################################################################################################################################

def _add_subscriber(definition:'Definition', username:'str', topic_names:'strlist') -> 'Credentials':
    out = definition.add_pattern_client(username, [], _all_topics)
    definition.add_pull_subscription(username, topic_names)
    return out

# ################################################################################################################################

def _setup(server:'PubSubServer', definition:'Definition') -> 'None':

    server.properties['publisher'] = definition.add_pattern_client('shapes.publisher', _all_topics, [])

    # One subscriber of each topic that one client receives everything of ..
    for topic_name in _single_topics:
        server.properties[topic_name] = _add_subscriber(definition, topic_name, [topic_name])

    # .. one subscriber of many topics ..
    topic_names:'strlist' = []

    for index in range(_topic_count):
        topic_names.append(f'shapes.topics.{index:05d}')

    server.properties['topic_names'] = topic_names
    server.properties['shapes.topics'] = _add_subscriber(definition, 'shapes.topics', topic_names)

    # .. and many subscribers of one topic.
    fan_out:'list[Credentials]' = []

    for index in range(_fan_out_subscriber_count):
        fan_out.append(_add_subscriber(definition, f'{_fan_out_topic}.{index:04d}', [_fan_out_topic]))

    server.properties['fan_out_topic'] = _fan_out_topic
    server.properties['fan_out'] = fan_out

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
