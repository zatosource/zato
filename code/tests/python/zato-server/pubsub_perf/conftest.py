# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import secrets
import sys
import tempfile

# pytest
import pytest

# PyYAML
import yaml

_current_dir = os.path.dirname(os.path.abspath(__file__))
_server_tests_dir = os.path.dirname(_current_dir)
_common_lib_dir = os.path.join(os.path.dirname(_server_tests_dir), 'zato-common', 'lib')

sys.path.insert(0, _server_tests_dir)
sys.path.insert(0, _common_lib_dir)

# Zato
from pubsub_perf.config import All_Scenarios, Credentials, credentialslist, PerfConfig, Receipts_Topic
from pubsub_perf.push import get_push_path, Push_Host, PushReceiver
from zato.common.test.client import AdminClient
from zato.common.test.conftest_base_pubsub import create_zato_server_fixture
from zato.common.typing_ import generator_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.conftest_base_pubsub import SessionState
    from zato.common.typing_ import anydict, anylist, intlist, strlist

# ################################################################################################################################
# ################################################################################################################################

nonegen         = generator_[None, None, None]
pushreceivergen = generator_[PushReceiver, None, None]

# ################################################################################################################################
# ################################################################################################################################

_logger_name = 'zato.test.pubsub_perf.conftest'

# How many random bytes each password has
_password_bytes = 16

# The type of the subscriptions of each kind of subscriber
_delivery_pull = 'pull'
_delivery_push = 'push'

# The output of the server is kept in the copy of its logs, the console of the run has the measurements only.
logging.getLogger(_logger_name).setLevel(logging.INFO)

# ################################################################################################################################
# ################################################################################################################################

def _new_credentials(role:'str', count:'int') -> 'credentialslist':
    """ Returns the given number of API clients of one role, each with a password of its own.
    """
    out:'credentialslist' = []

    for index in range(count):
        suffix = secrets.token_hex(_password_bytes)
        username = f'test.perf.{role}.{index:02d}'
        password = f'{username}.{suffix}'

        credentials = Credentials(username, password)
        out.append(credentials)

    return out

# ################################################################################################################################

def _get_pool_sizes() -> 'intlist':
    """ Returns how many publishers, how many pull subscribers and how many push subscribers the largest scenario needs.
    """
    publisher_count = 0
    pull_count = 0
    push_count = 0

    for scenario in All_Scenarios:
        publisher_count = max(publisher_count, scenario.publisher_count)
        pull_count = max(pull_count, scenario.pull_count)
        push_count = max(push_count, scenario.push_count)

    out = [publisher_count, pull_count, push_count]
    return out

# ################################################################################################################################

def _get_subscribed_topics(index:'int', delivery_type:'str') -> 'strlist':
    """ Returns the topics of the scenarios that the subscriber of the given index and delivery type takes part in.
    """
    out:'strlist' = []

    for scenario in All_Scenarios:

        if delivery_type == _delivery_pull:
            subscriber_count = scenario.pull_count
        else:
            subscriber_count = scenario.push_count

        if index < subscriber_count:
            out.append(scenario.topic_name)

    return out

# ################################################################################################################################

def _get_security(credentials:'Credentials') -> 'anydict':
    """ Returns the enmasse definition of the basic authentication of one API client.
    """
    out:'anydict' = {
        'name': credentials.username,
        'type': 'basic_auth',
        'username': credentials.username,
        'password': credentials.password,
    }

    return out

# ################################################################################################################################

def _build_definition(
    publishers:'credentialslist',
    subscribers:'credentialslist',
    push_subscribers:'credentialslist',
    receipt_reader:'Credentials',
    push_port:'int',
    ) -> 'anydict':
    """ Returns the enmasse definition of the topics, the API clients, their permissions, the outgoing REST connections
    of the push subscribers and the subscriptions.
    """
    security:'anylist' = []
    topics:'anylist' = []
    permissions:'anylist' = []
    outgoing_rest:'anylist' = []
    subscriptions:'anylist' = []

    push_host = f'http://{Push_Host}:{push_port}'

    scenario_topics:'strlist' = []

    for scenario in All_Scenarios:
        scenario_topics.append(scenario.topic_name)
        topics.append({'name': scenario.topic_name})

    topics.append({'name': Receipts_Topic})

    # Each publisher may publish to the topic of every scenario ..
    for credentials in publishers:
        security.append(_get_security(credentials))
        permissions.append({
            'security': credentials.username,
            'pub': scenario_topics,
        })

    # .. each pull subscriber has one subscription of its own to the topic of each scenario it takes part in,
    # publishing its receipts to a topic of their own ..
    for index, credentials in enumerate(subscribers):

        subscribed_topics = _get_subscribed_topics(index, _delivery_pull)

        security.append(_get_security(credentials))
        permissions.append({
            'security': credentials.username,
            'pub': [Receipts_Topic],
            'sub': subscribed_topics,
        })
        subscriptions.append({
            'security': credentials.username,
            'delivery_type': _delivery_pull,
            'topic_list': subscribed_topics,
        })

    # .. each push subscriber has one too, pushed through an outgoing REST connection of its own
    # to its own path of the receiver ..
    for index, credentials in enumerate(push_subscribers):

        subscribed_topics = _get_subscribed_topics(index, _delivery_push)

        security.append(_get_security(credentials))
        permissions.append({
            'security': credentials.username,
            'sub': subscribed_topics,
        })
        outgoing_rest.append({
            'name': credentials.username,
            'host': push_host,
            'url_path': get_push_path(index),
            'data_format': 'json',
        })
        subscriptions.append({
            'security': credentials.username,
            'delivery_type': _delivery_push,
            'push_rest_endpoint': credentials.username,
            'topic_list': subscribed_topics,
        })

    # .. and the reader of the receipts has the only subscription to that topic.
    security.append(_get_security(receipt_reader))
    permissions.append({
        'security': receipt_reader.username,
        'sub': [Receipts_Topic],
    })
    subscriptions.append({
        'security': receipt_reader.username,
        'delivery_type': _delivery_pull,
        'topic_list': [Receipts_Topic],
    })

    # The connections precede the subscriptions that name them.
    out:'anydict' = {
        'security': security,
        'outgoing_rest': outgoing_rest,
        'pubsub_topic': topics,
        'pubsub_permission': permissions,
        'pubsub_subscription': subscriptions,
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

_publisher_pool_size, _pull_pool_size, _push_pool_size = _get_pool_sizes()

_publishers       = _new_credentials('publisher', _publisher_pool_size)
_subscribers      = _new_credentials('subscriber', _pull_pool_size)
_push_subscribers = _new_credentials('push', _push_pool_size)
_receipt_reader   = _new_credentials('receipts', 1)[0]

# The receiver of the pushes listens before the definition names its port, and the session stops it when it ends.
_push_receiver = PushReceiver(_push_pool_size)
_push_receiver.start()

_definition = _build_definition(_publishers, _subscribers, _push_subscribers, _receipt_reader, _push_receiver.port)
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

    def _populate(
        host:'str',
        server_port:'int',
        invoke_password:'str',
        server_directory:'str',
        zato_bin:'str',
        ) -> 'None':

        base_url = f'http://{host}:{server_port}'

        # The tests invoke the services of this server and kill its worker ..
        PerfConfig.base_url      = base_url
        PerfConfig.server_port   = server_port
        PerfConfig.session_state = state
        PerfConfig.logger        = logger
        PerfConfig.client        = AdminClient(base_url, invoke_password)
        PerfConfig.database      = state.pubsub_database

        # .. and their clients use these credentials.
        PerfConfig.publishers       = _publishers
        PerfConfig.subscribers      = _subscribers
        PerfConfig.push_subscribers = _push_subscribers
        PerfConfig.receipt_reader   = _receipt_reader
        PerfConfig.push_receiver    = _push_receiver

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
    extra_server_env={},
    patch_server_conf_bind=True,
    build_config_callback=_build_config,
    log_to_files=False,
)

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session', autouse=True)
def push_receiver() -> 'pushreceivergen':
    """ Stops the receiver of the pushes at the end of the session.
    """
    yield _push_receiver

    _push_receiver.stop()

# ################################################################################################################################

@pytest.fixture(autouse=True)
def push_connections() -> 'nonegen':
    """ Closes the connections that the server keeps open to the receiver once each test ends.
    """
    yield

    _push_receiver.close_connections()

# ################################################################################################################################
# ################################################################################################################################
