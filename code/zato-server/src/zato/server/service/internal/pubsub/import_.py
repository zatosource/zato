'''
# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing
from dataclasses import dataclass

# SQLAlchemy
from sqlalchemy import and_, delete, exists, insert, update

# Zato
from zato.common.odb.model import PubSubEndpoint, PubSubSubscription, PubSubTopic, SecurityBase
from zato.common.odb.query.common import get_object_list, get_object_list_by_columns
from zato.common.typing_ import dictlist
from zato.server.service import Model, Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.typing_ import any_, dictlist

# ################################################################################################################################
# ################################################################################################################################

SecurityBaseTable:'any_' = SecurityBase.__table__
PubSubEndpointTable:'any_' = PubSubEndpoint.__table__
PubSubSubscriptionTable:'any_' = PubSubSubscription.__table__
PubSubTopicTable:'any_' = PubSubTopic.__table__

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

class ImportObjects(Service):
    """ Imports multiple pub/sub objects en masse.
    """
    name = 'dev.zato.pubsub.import-objects'

    def handle(self):
        data = test_data #  self.request.raw_request

        # Data that we received on input
        input = PubSubContainer.from_dict(data)

        # Data that already exists
        with closing(self.odb.session()) as session:

            # All security definitions that currently exist
            sec_list = self._get_sec_list(session)

            # All pub/sub objects that currently exist
            existing = self._get_existing_data(session)

        # Make sure we always have lists of dicts
        input_topics = input.pubsub_topic or []
        existing_topics = existing.pubsub_topic or []

        input_endpoints = input.pubsub_endpoint or []
        existing_endpoints = existing.pubsub_endpoint or []

        new_topics = self._find_new_items(input_topics, existing_topics)
        new_endpoints = self._find_new_items(input_endpoints, existing_endpoints)

# ################################################################################################################################

    def _find_new_items(self, incoming:'dictlist', existing:'dictlist') -> 'dictlist':

        # Our response to produce
        out:'dictlist' = []

        # Go through each item that we potentially need to create and see if there is a match
        for new_item in incoming:
            for existing_item in existing:
                if new_item['name'] == existing_item['name']:
                    break
            # .. if we are here, it means that there was no match, which means that this item truly is new ..
            else:
                out.append(new_item)

        # .. now, we can return the response to our caller.
        return out

# ################################################################################################################################

    def _get_sec_list(self, session:'SASession') -> 'dictlist':

        out = get_object_list(session, SecurityBaseTable)
        return out

# ################################################################################################################################

    def _get_existing_topics(self, session:'SASession') -> 'dictlist':

        topics = get_object_list(session, PubSubTopicTable)
        return topics

# ################################################################################################################################

    def _get_existing_endpoints(self, session:'SASession') -> 'dictlist':

        topics = get_object_list(session, PubSubEndpointTable)
        return topics

# ################################################################################################################################

    def _get_existing_subscriptions(self, session:'SASession') -> 'dictlist':

        columns = [PubSubSubscriptionTable.c.topic_id, PubSubSubscriptionTable.c.endpoint_id]
        subscriptions = get_object_list_by_columns(session, columns)
        return subscriptions

# ################################################################################################################################

    def _get_existing_data(self, session:'SASession') -> 'PubSubContainer':

        # Our response to produce
        out = PubSubContainer()
        out.pubsub_topic = []
        out.pubsub_endpoint = []
        out.pubsub_subscription = []

        existing_topics = self._get_existing_topics(session)
        existing_endpoints = self._get_existing_endpoints(session)
        existing_subscriptions = self._get_existing_endpoints(session)

        out.pubsub_topic.extend(existing_topics)
        out.pubsub_endpoint.extend(existing_endpoints)
        out.pubsub_subscription.extend(existing_subscriptions)

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
