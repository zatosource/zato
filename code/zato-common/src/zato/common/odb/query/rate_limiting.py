# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.common.odb.model import RateLimitState

# ################################################################################################################################

def current_state(session, cluster_id, object_type, object_id, period, network):
    """ Rate limiting state for input network in the given period.
    """
    return session.query(RateLimitState).\
        filter(RateLimitState.cluster_id==cluster_id).\
        filter(RateLimitState.object_type==object_type).\
        filter(RateLimitState.object_id==object_id).\
        filter(RateLimitState.period==period).\
        filter(RateLimitState.last_network==network)

# ################################################################################################################################

def current_period_list(session, cluster_id):
    """ Returns all periods stored in ODB, no matter their object type, ID or similar.
    """
    return session.query(RateLimitState.period)

# ################################################################################################################################
