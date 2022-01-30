# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# SQLAlchemy
from sqlalchemy import or_

# Zato
from zato.common.odb.model import PubSubEndpoint, PubSubSubscription

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.typing_ import anylist

# ################################################################################################################################
# ################################################################################################################################

def get_subscriptions(session:'SASession', max_last_interaction_time:'float') -> 'anylist':
    return session.query(
        PubSubSubscription.id,
        PubSubSubscription.sub_key,
        PubSubSubscription.ext_client_id,
        PubSubSubscription.last_interaction_time,
        PubSubEndpoint.name.label('endpoint_name'),
        PubSubEndpoint.id.label('endpoint_id'),
        ).\
        filter(PubSubEndpoint.id == PubSubSubscription.endpoint_id).\
        filter(PubSubEndpoint.is_internal.is_(False)).\
        filter(or_(
            PubSubSubscription.last_interaction_time < max_last_interaction_time,
            PubSubSubscription.last_interaction_time.is_(None),
        )).\
        order_by(PubSubSubscription.last_interaction_time.asc()).\
        all()

# ################################################################################################################################
# ################################################################################################################################
