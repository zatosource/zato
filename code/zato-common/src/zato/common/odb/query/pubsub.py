# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.odb.model import Cluster, PubSubSubscription, PubSubSubscriptionTopic, PubSubTopic, SecurityBase

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.typing_ import anylist

# ################################################################################################################################
# ################################################################################################################################

def pubsub_topic_by_name(session:'SASession', cluster_id:'int', name:'str') -> 'PubSubTopic | None':
    """ Returns a single pub/sub topic by name, or None if not found.
    """
    out = session.query(PubSubTopic).\
        filter(Cluster.id==cluster_id).\
        filter(Cluster.id==PubSubTopic.cluster_id).\
        filter(PubSubTopic.name==name).\
        first()

    return out

# ################################################################################################################################

def pubsub_subscriptions_by_topic_id(session:'SASession', topic_id:'int') -> 'anylist':
    """ Returns all PubSubSubscription rows linked to a topic through PubSubSubscriptionTopic.
    Must be called before the topic row is deleted (FK cascade removes junction rows).
    """
    out = session.query(PubSubSubscription).\
        join(PubSubSubscriptionTopic, PubSubSubscription.id == PubSubSubscriptionTopic.subscription_id).\
        filter(PubSubSubscriptionTopic.topic_id == topic_id).\
        all()

    return out

# ################################################################################################################################

def pubsub_subscription_topic_pairs(session:'SASession', cluster_id:'int') -> 'anylist':
    """ Returns one row per subscription-topic pair in the cluster, each with the subscriber's security definition.
    """
    out = session.query(
        PubSubSubscription.sub_key,
        PubSubSubscription.delivery_type,
        PubSubSubscription.push_type,
        PubSubSubscription.push_service_name,
        PubSubSubscription.rest_push_endpoint_id,
        PubSubTopic.name,
        SecurityBase.username,
        SecurityBase.name.label('sec_name'),
    ).\
        join(PubSubSubscriptionTopic, PubSubSubscriptionTopic.subscription_id == PubSubSubscription.id).\
        join(PubSubTopic, PubSubTopic.id == PubSubSubscriptionTopic.topic_id).\
        join(SecurityBase, SecurityBase.id == PubSubSubscription.sec_base_id).\
        filter(PubSubSubscription.cluster_id == cluster_id).\
        all()

    return out

# ################################################################################################################################
# ################################################################################################################################
