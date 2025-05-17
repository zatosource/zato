# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# ################################################################################################################################

if 0:
    from zato.common.odb.model import Cluster
    Cluster = Cluster

# ################################################################################################################################
# ################################################################################################################################

class ODBPostProcess:
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
        self.session.commit()

# ################################################################################################################################
# ################################################################################################################################
