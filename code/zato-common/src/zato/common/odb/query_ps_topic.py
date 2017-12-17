# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.common.odb.model import PubSubTopic, PubSubSubscription

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
