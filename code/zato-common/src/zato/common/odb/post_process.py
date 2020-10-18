# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.common.api import PUBSUB
from zato.common.odb.model import PubSubEndpoint

# ################################################################################################################################

# Type checking
if 0:
    from zato.common.odb.model import Cluster

    Cluster = Cluster

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
        self.session.commit()

# ################################################################################################################################

    def add_pubsub_service_endpoint(self, _name=PUBSUB.SERVICE_SUBSCRIBER.NAME):

        existing = self.session.query(PubSubEndpoint.id).\
            filter(PubSubEndpoint.name==_name).\
            first()

        if not existing:

            endpoint = PubSubEndpoint()
            endpoint.name = _name
            endpoint.is_internal = True
            endpoint.role = PUBSUB.ROLE.SUBSCRIBER.id
            endpoint.topic_patterns = PUBSUB.SERVICE_SUBSCRIBER.TOPICS_ALLOWED
            endpoint.endpoint_type = PUBSUB.ENDPOINT_TYPE.SERVICE.id

            if self.cluster:
                endpoint.cluster = self.cluster
            else:
                endpoint.cluster_id = self.cluster_id

            self.session.add(endpoint)

# ################################################################################################################################
# ################################################################################################################################
