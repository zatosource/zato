# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.common import PUBSUB
from zato.common.odb.model import PubSubEndpoint

# ################################################################################################################################

# Type checking
if 0:
    from zato.common.odb.model import Cluster

# ################################################################################################################################
# ################################################################################################################################

class ODBPostProcess(object):
    """ SQL post-processing functionality, e.g. creation of objects only after  aserver has started.
    """
    def __init__(self, session, cluster, cluster_id):
        # type: (object, Cluster, int)

        if not (cluster or cluster_id):
            raise ValueError('At least one of cluster or cluster_id is required in place of `{}` `{}`'.format(
                cluster, cluster_id))

        self.session = session
        self.cluster = cluster
        self.cluster_id = cluster_id

# ################################################################################################################################

    def run(self):
        self.add_pubsub_service_endpoint()

# ################################################################################################################################

    def add_pubsub_service_endpoint(self):

        endpoint_demo = PubSubEndpoint()
        endpoint_demo.name = PUBSUB.SERVICE_SUBSCRIBER.NAME
        endpoint_demo.is_internal = True
        endpoint_demo.role = PUBSUB.ROLE.SUBSCRIBER.id
        endpoint_demo.topic_patterns = PUBSUB.SERVICE_SUBSCRIBER.TOPICS_ALLOWED
        endpoint_demo.endpoint_type = PUBSUB.ENDPOINT_TYPE.REST.id

        if self.cluster:
            endpoint_demo.cluster = self.cluster
        else:
            endpoint_demo.cluster_id = self.cluster_id


# ################################################################################################################################
# ################################################################################################################################
