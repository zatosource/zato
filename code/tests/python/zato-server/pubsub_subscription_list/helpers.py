# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.db_env.database_env import DatabaseEnv
from zato.common.pubsub.subscription_list import new_topic_flags
from zato_common_core.zato_common_core import SubscriptionList

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.pubsub_in_process import InProcessServer
    from zato.common.typing_ import any_, anydict, pairlist, strlist

    InProcessServer = InProcessServer
    any_ = any_
    anydict = anydict
    pairlist = pairlist
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

def sqlite_db_path(server:'InProcessServer') -> 'str':
    """ Returns the path of the SQLite file of the in-process server.
    """
    out = server.db_env[DatabaseEnv.Env_Path]
    return out

# ################################################################################################################################

def sub_key_for_topic(subscription_list:'any_', topic_name:'str') -> 'str':
    """ Returns the governed sub key that has the given topic, lower-cased.
    """
    topic = topic_name.lower()

    for candidate, pair_topic, _status in subscription_list.statuses():
        if pair_topic == topic:
            if SubscriptionList.is_governed(candidate):
                return candidate

    raise Exception(f'No governed sub key for topic `{topic_name}`')

# ################################################################################################################################

def topic_flags_of(topics:'strlist', *, is_pub_enabled:'bool'=True, is_delivery_enabled:'bool'=True) -> 'anydict':
    """ Returns the flags dict of the given topic names for set_topics.
    """
    out:'anydict' = {}

    for topic_name in topics:
        out[topic_name.lower()] = new_topic_flags(is_pub_enabled, is_delivery_enabled)

    return out

# ################################################################################################################################

def add_topic_pending(subscription_list:'any_', sub_key:'str', topic_name:'str') -> 'None':
    """ Adds a topic to a subscriber in the list without writing its row, leaving the pair pending.
    """
    topics = topic_flags_of(subscription_list.topics_of(sub_key))
    topics[topic_name.lower()] = new_topic_flags(True, True)
    _ = subscription_list.set_topics(sub_key, True, topics)

# ################################################################################################################################

def remove_topic_pending(subscription_list:'any_', sub_key:'str', topic_name:'str') -> 'None':
    """ Removes a topic from a subscriber in the list without deleting its row, leaving the pair pending removal.
    """
    topics = topic_flags_of(subscription_list.topics_of(sub_key))
    del topics[topic_name.lower()]
    _ = subscription_list.set_topics(sub_key, True, topics)

# ################################################################################################################################

def set_delivery_enabled(
    subscription_list:'any_',
    sub_key:'str',
    topic_name:'str',
    is_delivery_enabled:'bool',
) -> 'None':
    """ Sets is_delivery_enabled of one pair of the subscriber in the list.
    """
    topics = topic_flags_of(subscription_list.topics_of(sub_key))
    topics[topic_name.lower()] = new_topic_flags(True, is_delivery_enabled)
    _ = subscription_list.set_topics(sub_key, True, topics)

# ################################################################################################################################

def set_pub_enabled(
    subscription_list:'any_',
    sub_key:'str',
    topic_name:'str',
    is_pub_enabled:'bool',
) -> 'None':
    """ Sets is_pub_enabled of one pair of the subscriber in the list.
    """
    topics = topic_flags_of(subscription_list.topics_of(sub_key))
    topics[topic_name.lower()] = new_topic_flags(is_pub_enabled, True)
    _ = subscription_list.set_topics(sub_key, True, topics)

# ################################################################################################################################

def status_of(subscription_list:'any_', sub_key:'str', topic_name:'str') -> 'str':
    """ Returns the status of one pair.
    """
    topic = topic_name.lower()

    for candidate, pair_topic, status in subscription_list.statuses():
        if candidate == sub_key:
            if pair_topic == topic:
                return status

    raise Exception(f'No status for `{sub_key}` / `{topic_name}`')

# ################################################################################################################################

def pair_in_rows(pairs:'pairlist', sub_key:'str', topic_name:'str') -> 'bool':
    """ Returns whether the governed pairs of the pub/sub database contain the given pair.
    """
    topic = topic_name.lower()

    for pair_sub_key, pair_topic in pairs:
        if pair_sub_key == sub_key:
            if pair_topic == topic:
                return True

    return False

# ################################################################################################################################
# ################################################################################################################################
