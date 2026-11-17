# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import sys
import tempfile

# PyYAML
import yaml

_current_dir = os.path.dirname(os.path.abspath(__file__))
_server_tests_dir = os.path.dirname(_current_dir)

sys.path.insert(0, _server_tests_dir)

# Zato
from pubsub_perf.config import All_Scenarios, Credentials, credentialslist, PerfConfig, Receipts_Topic
from zato.common.crypto.api import CryptoManager
from zato.common.test.conftest_base_pubsub import create_zato_server_fixture
from zato.common.test.exactly_once.config import TestConfig

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.conftest_base_pubsub import SessionState
    from zato.common.typing_ import anydict, anylist, strlist, strstrdict

# ################################################################################################################################
# ################################################################################################################################

_logger_name = 'zato.test.pubsub_perf.conftest'

# The lease of a pulled message, in seconds
_lease_seconds = '5'

_extra_server_env:'strstrdict' = {
    'Zato_PubSub_Pull_Lease_Seconds': _lease_seconds,
}

# The output of the server is kept in the copy of its logs, the console of the run has the measurements only.
logging.getLogger(_logger_name).setLevel(logging.INFO)

# ################################################################################################################################
# ################################################################################################################################

def _new_credentials(role:'str', count:'int') -> 'credentialslist':
    """ Returns the given number of API clients of one role, each with a password of its own.
    """
    out:'credentialslist' = []

    for index in range(count):
        suffix = CryptoManager.generate_hex_string()
        username = f'test.perf.{role}.{index:02d}'
        password = f'{username}.{suffix}'

        credentials = Credentials(username, password)
        out.append(credentials)

    return out

# ################################################################################################################################

def _get_pool_sizes() -> 'tuple[int, int]':
    """ Returns how many publishers and how many subscribers the largest scenario needs.
    """
    publisher_count = 0
    subscriber_count = 0

    for scenario in All_Scenarios:
        publisher_count = max(publisher_count, scenario.publisher_count)
        subscriber_count = max(subscriber_count, scenario.subscriber_count)

    out = (publisher_count, subscriber_count)
    return out

# ################################################################################################################################

def _get_subscribed_topics(index:'int') -> 'strlist':
    """ Returns the topics of the scenarios that the subscriber of the given index takes part in.
    """
    out:'strlist' = []

    for scenario in All_Scenarios:
        if index < scenario.subscriber_count:
            out.append(scenario.topic_name)

    return out

# ################################################################################################################################

def _build_definition(publishers:'credentialslist', subscribers:'credentialslist') -> 'anydict':
    """ Returns the enmasse definition of the topics, the API clients, their permissions and their subscriptions.
    """
    security:'anylist' = []
    topics:'anylist' = []
    permissions:'anylist' = []
    subscriptions:'anylist' = []

    scenario_topics:'strlist' = []

    for scenario in All_Scenarios:
        scenario_topics.append(scenario.topic_name)
        topics.append({'name': scenario.topic_name})

    topics.append({'name': Receipts_Topic})

    # Each publisher may publish to the topic of every scenario ..
    for credentials in publishers:
        security.append({
            'name': credentials.username,
            'type': 'basic_auth',
            'username': credentials.username,
            'password': credentials.password,
        })
        permissions.append({
            'security': credentials.username,
            'pub': scenario_topics,
        })

    # .. and each subscriber has one subscription of its own to the topic of each scenario it takes part in,
    # .. publishing its receipts to a topic that nobody subscribes to.
    for index, credentials in enumerate(subscribers):

        subscribed_topics = _get_subscribed_topics(index)

        security.append({
            'name': credentials.username,
            'type': 'basic_auth',
            'username': credentials.username,
            'password': credentials.password,
        })
        permissions.append({
            'security': credentials.username,
            'pub': [Receipts_Topic],
            'sub': subscribed_topics,
        })
        subscriptions.append({
            'security': credentials.username,
            'delivery_type': 'pull',
            'topic_list': subscribed_topics,
        })

    out:'anydict' = {
        'security': security,
        'pubsub_topic': topics,
        'pubsub_permission': permissions,
        'pubsub_subscription': subscriptions,
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

_publisher_pool_size, _subscriber_pool_size = _get_pool_sizes()

_publishers  = _new_credentials('publisher', _publisher_pool_size)
_subscribers = _new_credentials('subscriber', _subscriber_pool_size)

_definition = _build_definition(_publishers, _subscribers)
_definition_yaml = yaml.safe_dump(_definition, sort_keys=False)

# The definition holds passwords, so it is kept in a directory that the session removes when it ends.
_data_dir = tempfile.mkdtemp(prefix='zato_pubsub_perf_')
_template_path = os.path.join(_data_dir, 'enmasse.yaml')

with open(_template_path, 'w') as _template_file:
    _ = _template_file.write(_definition_yaml)

# ################################################################################################################################
# ################################################################################################################################

def _build_config(
    state:'SessionState',
    logger:'logging.Logger',
    zato_bin:'str',
    server_port:'int',
    invoke_password:'str',
    ) -> 'anydict':

    state.test_data_directory = _data_dir

    # The test process reads the lease that the server uses.
    os.environ.update(_extra_server_env)

    def _populate(
        host:'str',
        server_port:'int',
        invoke_password:'str',
        server_directory:'str',
        zato_bin:'str',
        ) -> 'None':

        # The shared harness kills and restarts the worker of this server ..
        TestConfig.base_url         = f'http://{host}:{server_port}'
        TestConfig.password         = invoke_password
        TestConfig.server_directory = server_directory
        TestConfig.server_port      = server_port
        TestConfig.zato_bin         = zato_bin
        TestConfig.template_path    = _template_path
        TestConfig.placeholders     = {}
        TestConfig.extra_server_env = _extra_server_env
        TestConfig.session_state    = state
        TestConfig.logger           = logger

        # .. and the clients of the tests use these credentials.
        PerfConfig.publishers    = _publishers
        PerfConfig.subscribers   = _subscribers
        PerfConfig.lease_seconds = float(_lease_seconds)

    out:'anydict' = {
        'placeholders': {},
        'populate_callback': _populate,
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

zato_server = create_zato_server_fixture(
    logger_name=_logger_name,
    server_log_copy_name='server-logs-pubsub-perf.txt',
    template_path=_template_path,
    quickstart_prefix='zato_pubsub_perf_qs_',
    extra_server_env=_extra_server_env,
    patch_server_conf_bind=True,
    build_config_callback=_build_config,
)

# ################################################################################################################################
# ################################################################################################################################
