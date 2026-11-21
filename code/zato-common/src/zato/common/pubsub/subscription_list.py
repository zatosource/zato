# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.typing_ import list_, tuple_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist, stranydict

# ################################################################################################################################
# ################################################################################################################################

pair     = tuple_[str, str]
pairlist = list_[pair]

# ################################################################################################################################
# ################################################################################################################################

# How often the reconciler commits the difference between the subscription list and the rows while any pair is unconfirmed, in seconds
Reconcile_Pending_Interval = 1.0

# How often the reconciler compares the subscription list with all the governed rows, in seconds
Reconcile_Full_Interval = 300.0

# How many pairs the reconciler and the startup synchronization commit in one transaction
Reconcile_Batch_Size = 500

# The format of the sub keys that the subscription list governs, as a pattern of LIKE and the length of a sub key
Governed_Sub_Key_Pattern = 'sk%'
Governed_Sub_Key_Length = 34

# How long a pub/sub transaction on PostgreSQL waits for a lock, equal to the busy timeout of SQLite writes, in milliseconds
Lock_Timeout_Ms = 5000

# ################################################################################################################################
# ################################################################################################################################

def new_topic_flags(is_pub_enabled:'bool', is_delivery_enabled:'bool') -> 'anydict':
    """ Returns the flags of one subscriber and topic pair in the form that the subscription list reads.
    """
    out = {
        'is_pub_enabled': is_pub_enabled,
        'is_delivery_enabled': is_delivery_enabled,
    }

    return out

# ################################################################################################################################

def build_subscribers(rows:'anylist') -> 'stranydict':
    """ Builds the subscriptions that the subscription list replaces itself with
    from the rows of pubsub_subscription_topic_pairs, one row per subscriber and topic pair.
    """
    out:'stranydict' = {}

    for row in rows:

        if not (subscriber := out.get(row.sub_key)):
            subscriber = {'is_pub_active': row.is_pub_active, 'topics': {}}
            out[row.sub_key] = subscriber

        subscriber['topics'][row.name] = new_topic_flags(row.is_pub_enabled, row.is_delivery_enabled)

    return out

# ################################################################################################################################
# ################################################################################################################################
