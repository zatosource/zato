# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os

# Zato
from pubsub_rest.definition import Definition
from zato.common.test.client import AdminClient
from zato.common.test.conftest_base_pubsub import get_server_pids

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pubsub_rest.receiver import PushReceiver
    from pubsub_rest.traffic import Traffic
    from zato.common.test.conftest_base_pubsub import SessionState
    from zato.common.test.pubsub_database import PubSubDatabase
    from zato.common.typing_ import any_, anydict, callable_, intlist, strlist, strnone, strstrdict

    callable_list = list[callable_]

# ################################################################################################################################
# ################################################################################################################################

# The file of the services through which the tests read what the server keeps in its database.
Services_Path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_services.py')

# The services of that file.
_service_count_mismatches = 'test.pubsub-rest.get-count-mismatches'
_service_database_statistics = 'test.pubsub-rest.get-database-statistics'
_service_topic_rows = 'test.pubsub-rest.get-topic-rows'
_service_queue_depths = 'test.pubsub-rest.get-queue-depths'
_service_delivery_count = 'test.pubsub-rest.get-delivery-count'
_service_failed_messages = 'test.pubsub-rest.get-failed-messages'
_service_expirations = 'test.pubsub-rest.get-expirations'
_service_sub_keys = 'test.pubsub-rest.get-sub-keys'
_service_server_state = 'test.pubsub-rest.get-server-state'
_service_publish = 'test.pubsub-rest.publish'
_service_hold_locks = 'test.pubsub-rest.hold-locks'

# How long one invocation of an administrative or a test service may take, in seconds.
_admin_timeout = 600

# ################################################################################################################################
# ################################################################################################################################

class PubSubServer:
    """ The server of a pub/sub suite - what the suite defines before it starts, and how the tests reach it once it runs.
    """

    def __init__(self, label:'str') -> 'None':
        self.label = label
        self.logger = logging.getLogger(f'zato.test.{label}')

        self.state:'SessionState | None' = None
        self.base_url = ''
        self.server_directory = ''
        self.zato_bin = ''
        self.client:'AdminClient | None' = None
        self.traffic:'Traffic | None' = None

        # What the suite sets before the server starts - the seeding of its database, the variables added
        # to the environment of the server and the command that the command of the server is started through ..
        self.pre_server_callback:'callable_ | None' = None
        self.server_env:'strstrdict' = {}
        self.command_prefix:'strlist' = []

        # .. what runs once the server is ready ..
        self.ready_callbacks:'callable_list' = []

        # .. and the values that the setup of a suite gives its tests.
        self.properties:'anydict' = {}

# ################################################################################################################################

    def reset(self, state:'SessionState') -> 'None':
        """ Prepares the object for the next server of its fixture.
        """
        self.state = state
        self.base_url = ''
        self.server_directory = ''
        self.zato_bin = ''
        self.client = None
        self.traffic = None
        self.pre_server_callback = None
        self.server_env = {}
        self.command_prefix = []
        self.ready_callbacks = []
        self.properties = {}

# ################################################################################################################################

    def add_receiver(self, receiver:'PushReceiver') -> 'None':
        """ Starts an endpoint that the server pushes to, which the fixture stops together with the server.
        """
        receiver.start()

        state = self.get_state()
        state.receivers.append(receiver)

# ################################################################################################################################

    def get_state(self) -> 'SessionState':
        state = self.state
        assert state is not None, 'The server of the suite has not been started'
        return state

# ################################################################################################################################

    def get_client(self) -> 'AdminClient':
        client = self.client
        assert client is not None, 'The server of the suite is not ready'
        return client

# ################################################################################################################################

    def get_traffic(self) -> 'Traffic':
        traffic = self.traffic
        assert traffic is not None, 'The suite defines no traffic'
        return traffic

# ################################################################################################################################

    def get_database(self) -> 'PubSubDatabase | None':
        """ The PostgreSQL database that the fixture started for the server, or None for a database
        that the environment of the test selects.
        """
        state = self.get_state()

        out = state.pubsub_database
        return out

# ################################################################################################################################

    def get_pids(self) -> 'intlist':
        """ The processes of the server.
        """
        out = get_server_pids(self.get_state())
        return out

# ################################################################################################################################

    def invoke(self, service_name:'str', payload:'anydict | None'=None) -> 'anydict':
        client = self.get_client()

        out = client.invoke(service_name, payload)
        return out

# ################################################################################################################################

    def get_topic_id(self, topic_name:'str') -> 'int':
        """ The ID of a topic, which its administrative services address it by.
        """
        topics, _ = self.get_client().get_list('zato.pubsub.topic.get-list', query=topic_name)

        for topic in topics:
            if topic['name'] == topic_name:
                return topic['id']

        raise Exception(f'Topic not found: {topic_name}')

# ################################################################################################################################

    def get_subscription(self, sub_key:'str') -> 'anydict':
        """ A subscription as its administrative services return it.
        """
        subscriptions, _ = self.get_client().get_list('zato.pubsub.subscription.get-list', query=sub_key)

        for subscription in subscriptions:
            if subscription['sub_key'] == sub_key:
                return subscription

        raise Exception(f'Subscription not found: {sub_key}')

# ################################################################################################################################

    def set_delivery_active(self, sub_key:'str', is_delivery_active:'bool') -> 'None':
        """ Pauses or resumes the delivery of a subscription, keeping each of its other settings.
        """
        subscription = self.get_subscription(sub_key)

        _ = self.invoke('zato.pubsub.subscription.edit', {
            'sub_key': sub_key,
            'topic_name_list': subscription['topic_name_list'],
            'sec_base_id': subscription['sec_base_id'],
            'delivery_type': subscription['delivery_type'],
            'is_delivery_active': is_delivery_active,
            'is_pub_active': subscription['is_pub_active'],
            'push_type': subscription['push_type'],
            'rest_push_endpoint_id': subscription['rest_push_endpoint_id'],
        })

# ################################################################################################################################

    def hold_locks(self, topic_name:'str', row_count:'int', hold_seconds:'float') -> 'None':
        """ Holds the locks that a cleanup sweep meets for the given time and returns once they are released.
        """
        _ = self.invoke(_service_hold_locks, {'topic_name': topic_name, 'row_count': row_count, 'hold_seconds': hold_seconds})

# ################################################################################################################################

    def get_count_mismatches(self) -> 'strlist':
        """ Each key whose stored count differs from the number of its rows - queues, topics and publications.
        """
        response = self.invoke(_service_count_mismatches)

        out = response['mismatches']
        return out

# ################################################################################################################################

    def get_database_statistics(self) -> 'anydict':
        out = self.invoke(_service_database_statistics)
        return out

# ################################################################################################################################

    def get_topic_rows(self, topic_name:'str') -> 'anydict':
        """ The messages of a topic, those of them that keep their payload, its deliveries and its subscriptions.
        """
        out = self.invoke(_service_topic_rows, {'topic_name': topic_name})
        return out

# ################################################################################################################################

    def get_queue_depths(self, sub_keys:'strlist') -> 'anydict':
        response = self.invoke(_service_queue_depths, {'sub_keys': sub_keys})

        out = response['depths']
        return out

# ################################################################################################################################

    def get_delivery_count(self) -> 'int':
        """ How many deliveries all the queues hold, counted row by row.
        """
        response = self.invoke(_service_delivery_count)

        out = response['delivery_count']
        return out

# ################################################################################################################################

    def get_queue_depth(self, sub_key:'str') -> 'int':
        depths = self.get_queue_depths([sub_key])

        out = depths[sub_key]
        return out

# ################################################################################################################################

    def get_failed_msg_ids(self, sub_key:'str') -> 'strlist':
        """ The messages of a subscriber whose delivery the audit log records as given up.
        """
        response = self.invoke(_service_failed_messages, {'sub_key': sub_key})

        out = response['msg_ids']
        return out

# ################################################################################################################################

    def get_expirations(self, msg_ids:'strlist') -> 'anydict':
        """ The expiration that the server stored for each of the given messages, in milliseconds.
        """
        response = self.invoke(_service_expirations, {'msg_ids': msg_ids})

        out = response['expirations']
        return out

# ################################################################################################################################

    def get_sub_keys(self) -> 'anydict':
        """ The subscription key of each subscriber, by the name of its security definition.
        """
        response = self.invoke(_service_sub_keys)

        out = response['sub_keys']
        return out

# ################################################################################################################################

    def is_replaced(self) -> 'bool':
        """ Whether another server took over the pub/sub database of this one.
        """
        response = self.invoke(_service_server_state)

        out = response['is_replaced']
        return out

# ################################################################################################################################

    def publish_with_retries(self, topic_name:'str', data:'any_', max_retries:'int', retry_sleep_time:'int') -> 'str':
        """ Publishes a message with the retry settings of its push deliveries and returns its msg_id.
        """
        payload = {
            'topic_name': topic_name,
            'data': data,
            'max_retries': max_retries,
            'retry_sleep_time': retry_sleep_time,
        }

        response = self.invoke(_service_publish, payload)

        out = response['msg_id']
        return out

# ################################################################################################################################
# ################################################################################################################################

def get_fixture_arguments(
    server:'PubSubServer',
    setup:'callable_',
    *,
    scope:'str',
    autouse:'bool' = True,
    uses_environment_database:'bool' = False,
    quickstart_parent_dir:'strnone' = None,
    log_to_files:'bool' = True,
    ) -> 'anydict':
    """ Returns the arguments of create_zato_server_fixture that start the server of a suite. The setup function
    receives the server object and the enmasse definition, to which it adds what the suite needs, and it may set
    what the server object holds for the time before the server starts and once it is ready.
    """

    def _build_config(
        state:'SessionState',
        logger:'logging.Logger',
        zato_bin:'str',
        server_port:'int',
        invoke_password:'str',
        ) -> 'anydict':

        server.reset(state)

        definition = Definition()
        setup(server, definition)

        def _populate(
            host:'str',
            server_port:'int',
            invoke_password:'str',
            server_directory:'str',
            zato_bin:'str',
            ) -> 'None':

            server.base_url = f'http://{host}:{server_port}'
            server.server_directory = server_directory
            server.zato_bin = zato_bin
            server.client = AdminClient(server.base_url, invoke_password, timeout=_admin_timeout)

            for callback in server.ready_callbacks:
                callback()

        out:'anydict' = {
            'placeholders': {},
            'populate_callback': _populate,
            'enmasse_yaml': definition.to_yaml(),
            'hot_deploy_sources': [Services_Path],
            'server_env': server.server_env,
            'server_command_prefix': server.command_prefix,
        }

        if server.pre_server_callback:
            out['pre_server_callback'] = server.pre_server_callback

        return out

    out:'anydict' = {
        'logger_name': f'zato.test.{server.label}',
        'server_log_copy_name': f'server-logs-{server.label}.txt',
        'template_path': '',
        'quickstart_prefix': f'zato_{server.label}_',
        'extra_server_env': {},
        'patch_server_conf_bind': True,
        'build_config_callback': _build_config,
        'scope': scope,
        'autouse': autouse,
        'uses_environment_database': uses_environment_database,
        'quickstart_parent_dir': quickstart_parent_dir,
        'log_to_files': log_to_files,
    }

    return out

# ################################################################################################################################
# ################################################################################################################################
