# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# SQLAlchemy
from sqlalchemy import or_
from sqlalchemy.sql.functions import coalesce

# Zato
from zato.common.odb.model import PubSubSubscription

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
        PubSubSubscription.last_interaction_time,
        ).\
        filter(or_(
            PubSubSubscription.last_interaction_time < max_last_interaction_time,
            PubSubSubscription.last_interaction_time.is_(None),
        )).\
        all()

# ################################################################################################################################
