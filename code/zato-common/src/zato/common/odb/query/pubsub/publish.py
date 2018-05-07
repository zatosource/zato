# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# SQLAlchemy
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError

# Zato
from zato.common import PUBSUB
from zato.common.exception import BadRequest
from zato.common.odb.model import PubSubEndpoint, PubSubEndpointEnqueuedMessage, PubSubEndpointTopic, PubSubMessage, PubSubTopic

# ################################################################################################################################

MsgInsert = PubSubMessage.__table__.insert
EndpointTopicInsert = PubSubEndpointTopic.__table__.insert
EnqueuedMsgInsert = PubSubEndpointEnqueuedMessage.__table__.insert

MsgTable = PubSubMessage.__table__
TopicTable = PubSubTopic.__table__
EndpointTable = PubSubEndpoint.__table__
EndpointTopicTable = PubSubEndpointTopic.__table__

# ################################################################################################################################

_initialized=PUBSUB.DELIVERY_STATUS.INITIALIZED

# ################################################################################################################################

def insert_topic_messages(session, cid, msg_list):
    """ Publishes messages to a topic, i.e. runs an INSERT that inserts rows, one for each message.
    """
    try:
        # Insert all messages
        session.execute(MsgInsert().values(msg_list))

    except IntegrityError, e:
        if 'pubsb_msg_pubmsg_id_idx' in e.message:
            raise BadRequest(cid, 'Duplicate msg_id:`{}`'.format(e.message))
        else:
            raise

# ################################################################################################################################

def insert_queue_messages(session, cluster_id, subscriptions_by_topic, msg_list, topic_id, now, _initialized=_initialized):
    """ Moves messages to each subscriber's queue, i.e. runs an INSERT that adds relevant references to the topic message.
    Also, updates each message's is_in_sub_queue flag to indicate that it is no longer available for other subscribers.
    """
    queue_msgs = []
    for sub in subscriptions_by_topic:
        for msg in msg_list:

            # Enqueues the message for each subscriber
            queue_msgs.append({
                'creation_time': now,
                'pub_msg_id': msg['pub_msg_id'],
                'endpoint_id': sub.endpoint_id,
                'topic_id': topic_id,
                'sub_key': sub.sub_key,
                'cluster_id': cluster_id,
            })

    # Move the message to endpoint queues
    session.execute(EnqueuedMsgInsert().values(queue_msgs))

# ################################################################################################################################

def update_publish_metadata(session, cluster_id, topic_id, endpoint_id, now, pattern_matched,
    last_pub_msg_id, last_pub_correl_id, last_ext_client_id, last_in_reply_to):

    # Update information when this endpoint last published to the topic
    endpoint_topic = session.execute(
        select([EndpointTopicTable.c.id]).\
        where(EndpointTopicTable.c.topic_id==topic_id).\
        where(EndpointTopicTable.c.endpoint_id==endpoint_id).\
        where(EndpointTopicTable.c.cluster_id==cluster_id)
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
            update(EndpointTopicTable).\
            values({
                'last_pub_time': now,
                'pub_msg_id': last_pub_msg_id,
                'pub_correl_id': last_pub_correl_id,
                'in_reply_to': last_in_reply_to,
                'pattern_matched': pattern_matched,
                'ext_client_id': last_ext_client_id,
                }).\
            where(EndpointTopicTable.c.topic_id==topic_id).\
            where(EndpointTopicTable.c.endpoint_id==endpoint_id).\
            where(EndpointTopicTable.c.cluster_id==cluster_id)
        )

    # Update metatadata for endpoint
    session.execute(
        update(EndpointTable).\
        values({
            'last_seen': now,
            'last_pub_time': now,
            }).\
        where(EndpointTable.c.id==endpoint_id).\
        where(EndpointTable.c.cluster_id==cluster_id)
    )

# ################################################################################################################################
