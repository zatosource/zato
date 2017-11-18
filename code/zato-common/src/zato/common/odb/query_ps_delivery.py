# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# SQLAlchemy
from sqlalchemy import update

# Zato
from zato.common.odb.model import PubSubMessage, PubSubEndpointEnqueuedMessage, PubSubSubscription

# ################################################################################################################################

def get_sql_messages_by_sub_key(session, cluster_id, sub_key, last_sql_run, now):
    """ Returns all SQL messages queued up for a given sub_key.
    """
    query = session.query(
        PubSubMessage.id,
        PubSubMessage.pub_msg_id,
        PubSubMessage.pub_correl_id,
        PubSubMessage.in_reply_to,
        PubSubMessage.ext_client_id,
        PubSubMessage.group_id,
        PubSubMessage.position_in_group,
        PubSubMessage.pub_time,
        PubSubMessage.ext_pub_time,
        PubSubMessage.data,
        PubSubMessage.mime_type,
        PubSubMessage.priority,
        PubSubMessage.expiration,
        PubSubMessage.expiration_time,
    ).\
    filter(PubSubEndpointEnqueuedMessage.pub_msg_id==PubSubMessage.pub_msg_id).\
    filter(PubSubEndpointEnqueuedMessage.subscription_id==PubSubSubscription.id).\
    filter(PubSubEndpointEnqueuedMessage.is_delivered==False).\
    filter(PubSubSubscription.sub_key==sub_key).\
    filter(PubSubMessage.expiration_time > now).\
    filter(PubSubMessage.cluster_id==cluster_id)

    if last_sql_run:
        query = query.\
            filter(PubSubMessage.pub_time > last_sql_run)

    query = query.\
        order_by(PubSubMessage.priority.desc()).\
        order_by(PubSubMessage.ext_pub_time).\
        order_by(PubSubMessage.pub_time)

    return query.all()

# ################################################################################################################################

def confirm_pubsub_msg_delivered(session, cluster_id, sub_key, pub_msg_id, now):
    """ Returns all SQL messages queued up for a given sub_key.
    """
    session.execute(
        update(PubSubEndpointEnqueuedMessage).\
        values({
            'is_delivered': True,
            'delivery_time': now
            }).\
        where(PubSubEndpointEnqueuedMessage.pub_msg_id==pub_msg_id).\
        where(PubSubEndpointEnqueuedMessage.subscription_id==PubSubSubscription.id).\
        where(PubSubSubscription.sub_key==sub_key)
    )

# ################################################################################################################################
