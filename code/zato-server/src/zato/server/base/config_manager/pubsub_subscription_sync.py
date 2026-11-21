# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# gevent
from gevent import spawn

# Zato
from zato.common.pubsub.subscription_list import Reconcile_Batch_Size, build_subscribers, new_topic_flags
from zato.common.worker_slot import is_config_process

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.ext.bunch import Bunch
    from zato.common.pubsub.subscription_list import pairlist
    from zato.common.typing_ import any_, anydict, anylist, strlist
    from zato.server.base.config_manager import ConfigManager
    from zato_common_core.zato_common_core import SubscriptionList

    Bunch = Bunch
    ConfigManager = ConfigManager
    SubscriptionList = SubscriptionList
    any_ = any_
    anydict = anydict
    anylist = anylist
    pairlist = pairlist
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

def topic_name_of(topic_item:'any_') -> 'str':
    """ Returns the topic name of one item of a create or edit event.
    """
    if isinstance(topic_item, dict):
        out = topic_item['topic_name']
    else:
        out = topic_item.topic_name

    return out

# ################################################################################################################################

def topic_flags_of(topic_item:'any_') -> 'anydict':
    """ Returns the flags of one topic item of a create or edit event.
    """
    if isinstance(topic_item, dict):
        is_pub_enabled = topic_item['is_pub_enabled']
        is_delivery_enabled = topic_item['is_delivery_enabled']
    else:
        is_pub_enabled = topic_item.is_pub_enabled
        is_delivery_enabled = topic_item.is_delivery_enabled

    out = new_topic_flags(is_pub_enabled, is_delivery_enabled)
    return out

# ################################################################################################################################

def topics_from_event(msg:'Bunch') -> 'anydict':
    """ Builds the topics map of a subscription from a create or edit event.
    """
    out:'anydict' = {}

    for topic_item in msg.topic_name_list:
        topic_name = topic_name_of(topic_item)
        out[topic_name] = topic_flags_of(topic_item)

    return out

# ################################################################################################################################

def queue_pair_write(config_manager:'ConfigManager', added:'pairlist', removed:'pairlist') -> 'None':
    """ Hands the row write of the given pairs to a greenlet of its own, which logs a failure and leaves the status as it is.
    """
    if not added:
        if not removed:
            return

    _ = spawn(_write_pairs, config_manager, added, removed)

# ################################################################################################################################

def _write_pairs(config_manager:'ConfigManager', added:'pairlist', removed:'pairlist') -> 'None':
    """ Writes the rows of the given pairs and cleans up the deliveries of the ones that were removed.
    """
    backend = config_manager.server.pubsub_backend

    try:
        backend.sync_subscription_pairs(added, removed)
    except Exception:
        logger.warning('Pub/sub subscription row write failed -> added:%s, removed:%s', added, removed, exc_info=True)
        return

    if removed:
        backend.cleanup_pair_deliveries(removed)

# ################################################################################################################################

def sync_subscription_create(config_manager:'ConfigManager', msg:'Bunch') -> 'None':
    """ Updates the subscription list for a create event and queues the inserts of its pairs.
    """
    if is_config_process():
        return

    sub_key = msg.sub_key
    topics = topics_from_event(msg)
    subscription_list = config_manager.server.pubsub_subscription_list

    _ = subscription_list.set_topics(sub_key, msg.is_pub_active, topics)

    added:'pairlist' = []

    for topic_name in topics:
        added.append((sub_key, topic_name))

    queue_pair_write(config_manager, added, [])

# ################################################################################################################################

def sync_subscription_edit(config_manager:'ConfigManager', msg:'Bunch') -> 'None':
    """ Updates the subscription list for an edit event and queues the inserts and deletes of its pairs.
    """
    if is_config_process():
        return

    sub_key = msg.sub_key
    subscription_list = config_manager.server.pubsub_subscription_list
    previous_topics = subscription_list.topics_of(sub_key)
    topics = topics_from_event(msg)

    _ = subscription_list.set_topics(sub_key, msg.is_pub_active, topics)

    previous_set = set(previous_topics)
    new_set = set(topics)

    added:'pairlist' = []
    removed:'pairlist' = []

    for topic_name in new_set:
        if topic_name not in previous_set:
            added.append((sub_key, topic_name))

    for topic_name in previous_set:
        if topic_name not in new_set:
            removed.append((sub_key, topic_name))

    queue_pair_write(config_manager, added, removed)

# ################################################################################################################################

def sync_subscription_delete(config_manager:'ConfigManager', sub_key:'str') -> 'None':
    """ Updates the subscription list for a delete event and queues the deletes of its pairs.
    """
    if is_config_process():
        return

    subscription_list = config_manager.server.pubsub_subscription_list
    previous_topics = subscription_list.remove(sub_key)

    removed:'pairlist' = []

    for topic_name in previous_topics:
        removed.append((sub_key, topic_name))

    queue_pair_write(config_manager, [], removed)

# ################################################################################################################################

def sync_topic_rename(config_manager:'ConfigManager', old_name:'str', new_name:'str') -> 'None':
    """ Renames a topic in the subscription list. The rows are renamed by rename_topic of the backend.
    """
    if is_config_process():
        return

    config_manager.server.pubsub_subscription_list.rename_topic(old_name, new_name)

# ################################################################################################################################

def sync_topic_delete(config_manager:'ConfigManager', topic_name:'str') -> 'None':
    """ Removes a deleted topic from every subscription in the list. The rows are removed by delete_topic of the backend.
    """
    if is_config_process():
        return

    _ = config_manager.server.pubsub_subscription_list.remove_topic(topic_name)

# ################################################################################################################################

def replace_from_odb(config_manager:'ConfigManager') -> 'pairlist':
    """ Replaces the subscription list from config.db and the governed rows of the pub/sub database,
    writes the difference in one or more transactions, cleans up the deliveries of the removed pairs,
    and returns the pairs that were removed.
    """
    from contextlib import closing
    from zato.common.odb.query.pubsub import pubsub_subscription_topic_pairs

    if is_config_process():
        return []

    server = config_manager.server
    subscription_list = server.pubsub_subscription_list
    backend = server.pubsub_backend

    with closing(server.odb.session()) as session:
        rows = pubsub_subscription_topic_pairs(session)

    subscribers = build_subscribers(rows)

    # The subscriptions of config.db take effect whether or not the pub/sub database can be read. If it cannot,
    # the list keeps the rows that it considers committed and the reconciler writes the difference once it can.
    try:
        committed = backend.get_governed_pairs()
    except Exception:
        logger.warning('Pub/sub subscription rows could not be read, the subscription list is replaced from config.db alone',
            exc_info=True)
        subscription_list.replace_subscribers(subscribers)
        return []

    subscription_list.replace(subscribers, committed)

    pending, removals = subscription_list.differences()
    all_removed:'pairlist' = []

    # The inserts and deletes of the difference are written a bounded batch at a time
    while pending or removals:

        added_batch = pending[:Reconcile_Batch_Size]
        removed_batch = removals[:Reconcile_Batch_Size]

        pending = pending[Reconcile_Batch_Size:]
        removals = removals[Reconcile_Batch_Size:]

        try:
            backend.sync_subscription_pairs(added_batch, removed_batch)
        except Exception:
            logger.warning(
                'Pub/sub subscription bulk sync failed -> added:%s, removed:%s',
                added_batch, removed_batch, exc_info=True)
            break

        all_removed.extend(removed_batch)

    if all_removed:
        backend.cleanup_pair_deliveries(all_removed)

    return all_removed

# ################################################################################################################################

def reconcile_once(config_manager:'ConfigManager', *, full:'bool') -> 'None':
    """ Commits the difference between the subscription list and the rows, or compares them in full first.
    """
    if is_config_process():
        return

    server = config_manager.server
    subscription_list = server.pubsub_subscription_list
    backend = server.pubsub_backend

    if not subscription_list.is_loaded():
        return

    if full:
        committed = backend.get_governed_pairs()
        subscription_list.replace_committed(committed)

    pending, removals = subscription_list.differences()

    if not pending:
        if not removals:
            return

    added_batch = pending[:Reconcile_Batch_Size]
    removed_batch = removals[:Reconcile_Batch_Size]

    try:
        backend.sync_subscription_pairs(added_batch, removed_batch)
    except Exception:
        logger.warning(
            'Pub/sub subscription reconciliation failed -> added:%s, removed:%s',
            added_batch, removed_batch, exc_info=True)
        return

    if removed_batch:
        backend.cleanup_pair_deliveries(removed_batch)

# ################################################################################################################################
# ################################################################################################################################
