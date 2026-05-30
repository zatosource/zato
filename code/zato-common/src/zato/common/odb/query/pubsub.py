# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.odb.model import Cluster, PubSubTopic

# ################################################################################################################################
# ################################################################################################################################

def pubsub_topic_by_name(session, cluster_id, name):
    """ Returns a single pub/sub topic by name, or None if not found.
    """
    out = session.query(PubSubTopic).\
        filter(Cluster.id==cluster_id).\
        filter(Cluster.id==PubSubTopic.cluster_id).\
        filter(PubSubTopic.name==name).\
        first()

    return out

# ################################################################################################################################
# ################################################################################################################################
