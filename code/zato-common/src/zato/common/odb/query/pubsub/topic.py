# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# SQLAlchemy
from sqlalchemy import and_, func, select
from sqlalchemy.sql.expression import false as sa_false

# Zato
from zato.common.odb.model import PubSubMessage, PubSubTopic, PubSubSubscription
from zato.common.odb.query import count
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy import Column
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.typing_ import anylist, intlist, strlist
    Column = Column

# ################################################################################################################################
# ################################################################################################################################

MsgTable = PubSubMessage.__table__
SubTable = PubSubSubscription.__table__
TopicTable = PubSubTopic.__table__

# ################################################################################################################################
# ################################################################################################################################

def get_topics_basic_data(session:'SASession') -> 'anylist':
    """ Return basic information about a topic, its ID, name and opaque data. The result is sorted by name.
    """
    return session.query(
        PubSubTopic.id,
        PubSubTopic.name,
        PubSubTopic.opaque1,
        ).\
        order_by(PubSubTopic.name).\
        all()

# ################################################################################################################################

def get_topics_by_sub_keys(session:'SASession', cluster_id:'int', sub_keys:'strlist') -> 'anylist':
    """ Returns (topic_id, sub_key) for each input sub_key.
    """
    return session.query(
        PubSubTopic.id,
        PubSubSubscription.sub_key).\
        filter(PubSubSubscription.topic_id==PubSubTopic.id).\
        filter(cast_('Column', PubSubSubscription.sub_key).in_(sub_keys)).\
        all()

# ################################################################################################################################

def get_gd_depth_topic(session:'SASession', cluster_id:'int', topic_id:'int') -> 'int':
    """ Returns current depth of input topic by its ID.
    """
    q = session.query(MsgTable.c.id).\
        filter(MsgTable.c.topic_id==topic_id).\
        filter(MsgTable.c.cluster_id==cluster_id).\
        filter(~MsgTable.c.is_in_sub_queue)

    return count(session, q)

# ################################################################################################################################

def get_gd_depth_topic_list(session:'SASession', cluster_id:'int', topic_id_list:'intlist') -> 'anylist':
    """ Returns topics matching the input list as long as they have any messages undelivered to their queues.
    """

    q = select([
        MsgTable.c.topic_id,
        func.count(MsgTable.c.topic_id).label('depth')
        ]).\
        where(and_(
            MsgTable.c.cluster_id == cluster_id,
            MsgTable.c.is_in_sub_queue == sa_false(),
            MsgTable.c.topic_id.in_(topic_id_list),
        )).\
        group_by('topic_id')

    return session.execute(q).fetchall()

# ################################################################################################################################

def get_topic_sub_count_list(session:'SASession', cluster_id:'int', topic_id_list:'intlist') -> 'anylist':
    """ Returns the number of subscriptions for each topic from the input list.
    """

    q = select([
        SubTable.c.topic_id,
        func.count(SubTable.c.topic_id).label('sub_count')
        ]).\
        where(and_(
            SubTable.c.cluster_id == cluster_id,
            SubTable.c.topic_id.in_(topic_id_list),
        )).\
        group_by('topic_id')

    return session.execute(q).fetchall()

# ################################################################################################################################
