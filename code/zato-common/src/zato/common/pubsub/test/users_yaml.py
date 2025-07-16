# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# PyYAML
from yaml import safe_load as yaml_load

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from typing import Dict, List, Set, Tuple

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class UsersYAMLParser:
    """ Parser for users.yaml PubSub configuration.
    """
    def __init__(self, users_yaml_path):
        self.users_yaml_path = users_yaml_path
        self.data = None
        self._load_yaml()

    def _load_yaml(self) -> 'None':
        """ Load the YAML file from disk.
        """
        with open(self.users_yaml_path, 'r') as f:
            self.data = yaml_load(f)

    def get_users(self) -> 'list':
        """ Get list of all users.
        """
        return list(self.data.get('users', {}))

    def get_topics(self) -> 'list':
        """ Get list of all topics.
        """
        return list(self.data.get('topics', {}))

    def get_subscribers_for_topic(self, topic_name:'str') -> 'set':
        """ Get set of users subscribed to a given topic.
        """
        topic_subscriptions = self.data.get('subscriptions', {}).get(topic_name, {})
        return set(topic_subscriptions.keys())

    def get_subscriptions(self) -> 'dict':
        """ Get all subscriptions.
        """
        return self.data.get('subscriptions', {})

# ################################################################################################################################
# ################################################################################################################################

def calculate_expected_messages(users_yaml_path:'str', messages_per_topic_per_user:'int') -> 'int':
    """ Calculate the expected number of messages based on the users.yaml configuration.

    For each topic, count (number of users publishing) * (messages per topic per user) * (number of subscribers)
    """
    parser = UsersYAMLParser(users_yaml_path)

    # All users can publish to all topics
    all_users = parser.get_users()
    all_topics = parser.get_topics()

    # Calculate expected messages
    total_expected_messages = 0

    for topic_name in all_topics:
        # All users publish to each topic
        number_of_publishers = len(all_users)

        # Get subscribers for this topic
        subscribers = parser.get_subscribers_for_topic(topic_name)
        number_of_subscribers = len(subscribers)

        # Calculate messages for this topic
        topic_messages = number_of_publishers * messages_per_topic_per_user * number_of_subscribers

        total_expected_messages += topic_messages

    return total_expected_messages

# ################################################################################################################################
# ################################################################################################################################

def calculate_message_distribution(users_yaml_path:'str', messages_per_topic_per_user:'int') -> 'dict':
    """ Calculate the distribution of messages across topics and subscribers.
    """
    parser = UsersYAMLParser(users_yaml_path)

    all_users = parser.get_users()
    all_topics = parser.get_topics()

    # Structure to hold distribution information
    distribution = {
        'total_expected': 0,
        'by_topic': {},
        'by_subscription': {},
    }

    for topic_name in all_topics:
        # All users publish to each topic
        publishers = all_users

        # Get subscribers for this topic
        subscribers = parser.get_subscribers_for_topic(topic_name)

        # Calculate messages for this topic
        topic_messages = len(publishers) * messages_per_topic_per_user * len(subscribers)

        # Store in distribution
        distribution['total_expected'] += topic_messages
        distribution['by_topic'][topic_name] = {
            'publishers': len(publishers),
            'subscribers': len(subscribers),
            'expected_messages': topic_messages
        }

        # Store per-subscription details
        for subscriber in subscribers:
            sub_key = parser.get_subscriptions()[topic_name][subscriber]['sub_key']
            expected_sub_messages = len(publishers) * messages_per_topic_per_user

            if sub_key not in distribution['by_subscription']:
                distribution['by_subscription'][sub_key] = {
                    'expected_messages': 0,
                    'topics': {}
                }

            distribution['by_subscription'][sub_key]['expected_messages'] += expected_sub_messages
            distribution['by_subscription'][sub_key]['topics'][topic_name] = {
                'subscriber': subscriber,
                'expected_messages': expected_sub_messages
            }

    return distribution

# ################################################################################################################################
# ################################################################################################################################
