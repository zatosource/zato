'''
# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass

# Zato
from zato.common.typing_ import dictlist
from zato.server.service import Model, Service

# Zato
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class PubSubContainer(Model):
    pubsub_topic: 'dictlist | None'
    pubsub_endpoint: 'dictlist | None'
    pubsub_subscription: 'dictlist | None'

    def has_topic(self, name:'str') -> 'bool':
        pass

    def has_endpoint(self, name:'str') -> 'bool':
        pass

    def has_subscription(self, topic_name:'str', endpoint_name:'str') -> 'bool':
        pass

# ################################################################################################################################
# ################################################################################################################################

class GetList(Service):
    """ Returns all groups matching the input criteria.
    """
    name = 'dev.zato.pubsub.import-objects'

    def handle(self):
        data = test_data #  self.request.raw_request

        # Data that we received on input
        input = PubSubContainer.from_dict(data)

        # Data that already exists
        existing = self._get_existing_data()

# ################################################################################################################################

    def _get_existing_data(self) -> 'PubSubContainer'

        # Our response to produce
        out = PubSubContainer()
        out.pubsub_topic = []
        out.pubsub_endpoint = []
        out.pubsub_subscription = []

        return out

# ################################################################################################################################
# ################################################################################################################################

test_data = {
    'pubsub_endpoint': [
        {
            'name': 'endpoint-test-cli-security-test-cli-/test-perf.1/sec/pub/0000',
            'endpoint_type': 'rest',
            'service_name': None,
            'topic_patterns': 'pub=/*',
            'sec_name': 'security-test-cli-/test-perf.1/sec/pub/0000',
            'is_active': True,
            'is_internal': False,
            'role': 'pub-sub',
            'service': None
        },
        {
            'name': 'endpoint-test-cli-security-test-cli-/test-perf.1/sec/sub/0000',
            'endpoint_type': 'rest',
            'service_name': None,
            'topic_patterns': 'sub=/*',
            'sec_name': 'security-test-cli-/test-perf.1/sec/sub/0000',
            'is_active': True,
            'is_internal': False,
            'role': 'pub-sub',
            'service': None
        }
    ],
    'pubsub_topic': [
        {
            'name': '/test-perf.1',
            'has_gd': True,
            'is_active': True,
            'is_api_sub_allowed': True,
            'max_depth_gd': 10000,
            'max_depth_non_gd': 1000,
            'depth_check_freq': 100,
            'pub_buffer_size_gd': 0,
            'task_sync_interval': 500,
            'task_delivery_interval': 2000
        }
    ],
    'pubsub_subscription': [
        {
            'name': 'Subscription.000000001',
            'endpoint_name': 'endpoint-test-cli-security-test-cli-/test-perf.1/sec/sub/0000',
            'endpoint_type': 'rest',
            'delivery_method': 'pull',
            'topic_list_json': ['/test-perf.1'],
            'is_active': True,
            'should_ignore_if_sub_exists': True,
            'should_delete_all': True
        }
    ]
}

# ################################################################################################################################
# ################################################################################################################################
'''
