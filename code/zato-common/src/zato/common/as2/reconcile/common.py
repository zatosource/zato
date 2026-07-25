# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

What reconciliation keeps of a sent message - the searchable attributes it is described by,
the open message they are read back into, and the outcome of matching one receipt against it.
"""

# stdlib
from dataclasses import dataclass

# Zato
from zato.common.as2.common import DeliveryKind

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.as2.mdn import MDNDetails
    from zato.common.typing_ import strstrdict
    strstrdict = strstrdict
    MDNDetails = MDNDetails

# ################################################################################################################################
# ################################################################################################################################

#  Type aliases
pending_mdn_list = list['PendingMDN']

# ################################################################################################################################
# ################################################################################################################################

# The server name reconciliation events are recorded under when none is given.
Default_Server_Name = 'as2-reconciler'

# How many open messages one call to outstanding may return. The alerting job and the automatic
# resend both run on it, and a partner outage over a weekend would otherwise have them read every
# unanswered message at once - a bounded batch keeps a long outage from turning either job into
# a memory event, with the next run picking up where this one stopped.
Max_Outstanding = 5_000

# ################################################################################################################################
# ################################################################################################################################

class ReconcileAttr:
    """ The searchable attributes a message-sent event carries. They are what reconciliation reads,
    which is why they are columns of their own rather than fields inside the event data - the data
    of a message-sent event also holds every document that went out, and reading a digest is not
    a reason to pull a whole interchange out of the database.
    """
    MIC           = 'mic'
    Async_MDN_URL = 'async_mdn_url'
    Delivery_Kind = 'delivery_kind'
    HTTP_Status   = 'http_status'

# ################################################################################################################################

# Everything one open message is described by, in the order the two queries fill it in.
reconcile_attr_names = (
    ReconcileAttr.MIC,
    ReconcileAttr.Async_MDN_URL,
    ReconcileAttr.Delivery_Kind,
    ReconcileAttr.HTTP_Status,
)

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class PendingMDN:
    """ One sent message whose MDN has not arrived.
    """
    as2_from:      str = ''
    as2_to:        str = ''
    message_id:    str = ''
    mic:           str = ''
    async_mdn_url: str = ''
    sent_time_iso: str = ''
    cid:           str = ''

    # Which of the reliability taxonomy this attempt was, and what the partner's HTTP layer
    # answered it with - the automatic resend reads both to decide what to do next.
    delivery_kind: str = ''
    http_status:   int = 0

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class MDNMatchResult:
    """ The outcome of matching one incoming MDN against the reconciliation store.
    """
    # Whether the body parsed and verified as an MDN at all.
    is_parsed: bool = False

    # Whether the MDN answered a message the store was waiting for.
    is_matched: bool = False

    # Whether the matched MDN reports clean processing and its MIC agrees
    # with the one computed at send time.
    is_ok: bool = False

    # The parsed MDN, when the body parsed at all.
    mdn: 'MDNDetails | None' = None

    # The sent message the MDN answered, when one matched.
    pending: 'PendingMDN | None' = None

# ################################################################################################################################
# ################################################################################################################################

def pair_key(as2_from:'str', as2_to:'str') -> 'str':
    """ Builds the storage key of one AS2 identity pair.
    """
    as2_from = as2_from.strip()
    as2_to = as2_to.strip()

    out = f'{as2_from}:{as2_to}'
    return out

# ################################################################################################################################

def new_empty_attrs() -> 'strstrdict':
    """ The attribute set of one event before the database has said anything about it, so that
    an event recorded without an attribute reads the same as one whose attribute is empty.
    """
    out:'strstrdict' = {}

    for name in reconcile_attr_names:
        out[name] = ''

    return out

# ################################################################################################################################

def new_pending(object_name:'str', msg_id:'str', event_time_iso:'str', cid:'str', attrs:'strstrdict') -> 'PendingMDN':
    """ Turns one message-sent event and its attributes into the pending message they describe.
    An attribute an older event was recorded without reads as its own default - no digest to
    reconcile against, no asynchronous destination, and an original attempt whose transport
    outcome is not known.
    """
    as2_from, as2_to = object_name.split(':', 1)

    out = PendingMDN()

    out.as2_from = as2_from
    out.as2_to = as2_to
    out.message_id = msg_id
    out.sent_time_iso = event_time_iso
    out.cid = cid

    out.mic = attrs[ReconcileAttr.MIC]
    out.async_mdn_url = attrs[ReconcileAttr.Async_MDN_URL]

    delivery_kind = attrs[ReconcileAttr.Delivery_Kind]

    if delivery_kind:
        out.delivery_kind = delivery_kind
    else:
        out.delivery_kind = DeliveryKind.Original

    if http_status := attrs[ReconcileAttr.HTTP_Status]:
        out.http_status = int(http_status)

    return out

# ################################################################################################################################
# ################################################################################################################################
