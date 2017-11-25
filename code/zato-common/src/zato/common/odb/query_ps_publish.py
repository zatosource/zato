# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# SQLAlchemy
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError

# Zato
from zato.common import PUBSUB
from zato.common.exception import BadRequest
from zato.common.odb.model import PubSubTopic, PubSubEndpoint, PubSubEndpointEnqueuedMessage, PubSubEndpointTopic, PubSubMessage

# ################################################################################################################################

MsgInsert = PubSubMessage.__table__.insert
EndpointTopicInsert = PubSubEndpointTopic.__table__.insert
EnqueuedMsgInsert = PubSubEndpointEnqueuedMessage.__table__.insert

Topic = PubSubTopic.__table__
Endpoint = PubSubEndpoint.__table__
EndpointTopic = PubSubEndpointTopic.__table__

# ################################################################################################################################

_initialized=PUBSUB.DELIVERY_STATUS.INITIALIZED

# ################################################################################################################################

def get_topic_depth(session, cluster_id, topic_id):
    """ Returns current depth of input topic by its ID.
    """
    return session.execute(
        select([Topic.c.current_depth_gd]).\
        where(Topic.c.id==topic_id).\
        where(Topic.c.cluster_id==cluster_id)
        ).\
        fetchone()[0]

# ################################################################################################################################

def incr_topic_depth(session, cluster_id, topic_id, now, incr_by):
    """ Increments current depth of input topic by incr_by.
    """
    session.execute(
        update(Topic).\
        values({
            'current_depth_gd': Topic.c.current_depth_gd + incr_by,
            'last_pub_time': now
            }).\
        where(Topic.c.id==topic_id).\
        where(Topic.c.cluster_id==cluster_id)
    )

# ################################################################################################################################

def insert_topic_messages(session, cid, msg_list):
    """ Publishes messages to a topic, i.e. runs an INSERT that inserts rows, one for each message.
    """
    try:
        session.execute(MsgInsert().values(msg_list))
    except IntegrityError, e:
        if 'pubsb_msg_pubmsg_id_idx' in e.message:
            raise BadRequest(cid, 'Duplicate msg_id:`{}`'.format(e.message))
        else:
            raise

# ################################################################################################################################

def insert_queue_messages(session, cluster_id, subscriptions_by_topic, msg_list, topic_id, now, _initialized=_initialized):
    """ Moves messages to each subscriber's queue, i.e. runs an INSERT that add relevant references
    to the topic message.
    """
    queue_msgs = []
    for sub in subscriptions_by_topic:
        for msg in msg_list:
            queue_msgs.append({
                'creation_time': now,
                'delivery_count': 0,
                'pub_msg_id': msg['pub_msg_id'],
                'endpoint_id': sub.endpoint_id,
                'topic_id': topic_id,
                'subscription_id': sub.id,
                'cluster_id': cluster_id,
                'has_gd': False,
                'is_in_staging': False,
                'delivery_status': _initialized,
            })

    # Move the message to endpoint queues
    session.execute(EnqueuedMsgInsert().values(queue_msgs))

# ################################################################################################################################

def update_publish_metadata(session, cluster_id, topic_id, endpoint_id, now, msg_list, pattern_matched,
    last_pub_msg_id, last_pub_correl_id, last_ext_client_id, last_in_reply_to):

    # Update information when this endpoint last published to the topic
    endpoint_topic = session.execute(
        select([EndpointTopic.c.id]).\
        where(EndpointTopic.c.topic_id==topic_id).\
        where(EndpointTopic.c.endpoint_id==endpoint_id).\
        where(EndpointTopic.c.cluster_id==cluster_id)
        ).\
        fetchone()

    # Never published before - add a new row then
    if not endpoint_topic:

        session.execute(
            EndpointTopicInsert(), [{
            'endpoint_id': endpoint_id,
            'topic_id': topic_id,
            'cluster_id': cluster_id,
            'last_pub_time': now,
            'pub_msg_id': last_pub_msg_id,
            'pub_correl_id': last_pub_correl_id,
            'in_reply_to': last_in_reply_to,
            'pattern_matched': pattern_matched,
            'ext_client_id': last_ext_client_id,
            }])

    # Already published before - update its metadata in that case.
    else:
        session.execute(
            update(EndpointTopic).\
            values({
                'last_pub_time': now,
                'pub_msg_id': last_pub_msg_id,
                'pub_correl_id': last_pub_correl_id,
                'in_reply_to': last_in_reply_to,
                'pattern_matched': pattern_matched,
                'ext_client_id': last_ext_client_id,
                }).\
            where(EndpointTopic.c.topic_id==topic_id).\
            where(EndpointTopic.c.endpoint_id==endpoint_id).\
            where(EndpointTopic.c.cluster_id==cluster_id)
        )

    # Update metatadata for endpoint
    session.execute(
        update(Endpoint).\
        values({
            'last_seen': now,
            'last_pub_time': now,
            }).\
        where(Endpoint.c.id==endpoint_id).\
        where(Endpoint.c.cluster_id==cluster_id)
    )

# ################################################################################################################################
