# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# SQLAlchemy
from sqlalchemy import and_, func, select
from sqlalchemy.sql.expression import false as sa_false

# Zato
from zato.common.odb.model import PubSubMessage, PubSubTopic, PubSubSubscription
from zato.common.odb.query import count

# ################################################################################################################################

MsgTable = PubSubMessage.__table__

# ################################################################################################################################

def get_topics_by_sub_keys(session, cluster_id, sub_keys):
    """ Returns (topic_id, sub_key) for each input sub_key.
    """
    return session.query(
        PubSubTopic.id,
        PubSubSubscription.sub_key).\
        filter(PubSubSubscription.topic_id==PubSubTopic.id).\
        filter(PubSubSubscription.sub_key.in_(sub_keys)).\
        all()

# ################################################################################################################################

def get_gd_depth_topic(session, cluster_id, topic_id):
    """ Returns current depth of input topic by its ID.
    """
    q = session.query(MsgTable.c.id).\
        filter(MsgTable.c.topic_id==topic_id).\
        filter(MsgTable.c.cluster_id==cluster_id).\
        filter(~MsgTable.c.is_in_sub_queue)

    return count(session, q)

# ################################################################################################################################

def get_gd_depth_topic_list(session, cluster_id, topic_id_list):
    """ Returns topics matching the input list as long as they have any messages undelivered to their queues.
    """

    q = select([
        MsgTable.c.topic_id,
        func.count(MsgTable.c.topic_id).label('depth')]).\
        where(and_(
            MsgTable.c.cluster_id == cluster_id,
            MsgTable.c.is_in_sub_queue == sa_false(),
            MsgTable.c.topic_id.in_(topic_id_list),
        )).\
        group_by('topic_id')

    return session.execute(q).fetchall()

# ################################################################################################################################
