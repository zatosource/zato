# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist, callable_, intdict, intlist, intlistnone, strlist

    # Dummy assignments to satisfy type checkers
    anydict = anydict
    anylist = anylist
    callable_ = callable_
    intdict = intdict
    intlist = intlist
    intlistnone = intlistnone
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

# Type aliases
pending_publication_list = list['PendingPublication']
pending_ack_list         = list['PendingAck']
pending_atomic_list      = list['PendingAtomic']
pending_lease_list       = list['PendingLease']
pending_attempts_list    = list['PendingAttempts']

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class PendingPublication:
    """ One message to publish, with the subscribers it was published to once it is written.
    """

    # The values of the message row
    message_values: 'anydict'

    # The subscribers of the topic as of the commit that wrote the message
    subscriber_keys: 'strlist'

    # Why the message could not be written, while the other items of its commit could
    exception: 'BaseException | None'

    # Whether the message ID existed already with the same topic and payload, so that nothing was written
    is_repeat: 'bool'

    # The audit events that commit with the message, and only if the message is written
    audit_events: 'anylist'

# ################################################################################################################################

@dataclass(init=False)
class PendingAck:
    """ The acknowledgement of messages by one subscriber, with what it removed once it is written.
    """

    # Who acknowledges the messages and which ones, by their public identifiers and, when known, by their primary keys
    sub_key: 'str'
    msg_ids: 'strlist'
    sequence_ids: 'intlistnone'

    # How many of the subscriber's delivery rows it removed and how many of the messages became fully delivered
    removed_count: 'int'
    fully_delivered_count: 'int'

    # Why the acknowledgement could not be written, while the other items of its commit could
    exception: 'BaseException | None'

    # Whether the delivery rows are removed under the fence of fenced_ack.py, and with what delivery attempt
    # of each message, in the order of the messages, or with any attempt, which is the case of a push batch
    is_fenced: 'bool'
    expected_attempts: 'intlistnone'

    # The messages of a fenced acknowledgement that an earlier delivery concluded, which it removes nothing of
    concluded_msg_ids: 'strlist'

# ################################################################################################################################

@dataclass(init=False)
class PendingAtomic:
    """ A fenced acknowledgement with the publications that commit together with it or not at all,
    sharing a commit with other items without sharing its outcome with them.
    """

    # The publications and the acknowledgement, written in this order
    publications: 'pending_publication_list'
    ack: 'PendingAck'

    # Whether a publication whose message ID stands for a different message fails the whole item,
    # rather than the publication alone not being written
    is_strict: 'bool'

    # Why nothing of the item was written, while the other items of its commit could be
    exception: 'BaseException | None'

    # The audit events of the deliveries that the item concludes, which commit with the item whatever its outcome
    audit_events: 'anylist'

# ################################################################################################################################

@dataclass(init=False)
class PendingLease:
    """ A pull of one subscriber's deliverable messages, with the rows of the messages it leased once it is written.
    """

    # Who pulls, how much and until when the messages are leased
    sub_key: 'str'
    max_messages: 'int'
    max_len: 'int'
    now_ms: 'int'
    leased_until_ms: 'int'

    # The rows of the leased messages and the attempt number of each, by message ID
    rows: 'anylist'
    attempts: 'intdict'

    # What builds the messages and the audit events of the leased rows in the transaction that leases them,
    # with the messages handed to the client and the audit events that commit with the lease
    on_leased: 'callable_'
    messages: 'anylist'
    audit_events: 'anylist'

    # Why the lease could not be written, while the other items of its commit could
    exception: 'BaseException | None'

# ################################################################################################################################

@dataclass(init=False)
class PendingAttempts:
    """ The next push attempt of each delivery of a batch, with the attempt number of each delivery
    that is still in its subscriber's queue once it is written.
    """

    # The deliveries whose attempts are recorded
    delivery_ids: 'intlist'

    # The attempt number of each delivery still in its subscriber's queue, by delivery ID
    attempts: 'intdict'

    # Why the attempts could not be written, while the other items of its commit could
    exception: 'BaseException | None'

# ################################################################################################################################
# ################################################################################################################################

def new_pending_publication(message_values:'anydict') -> 'PendingPublication':
    """ Returns a publication that is yet to be written.
    """
    out = PendingPublication()
    out.message_values = message_values
    out.subscriber_keys = []
    out.exception = None
    out.is_repeat = False
    out.audit_events = []

    return out

# ################################################################################################################################

def new_pending_ack(sub_key:'str', msg_ids:'strlist', sequence_ids:'intlistnone') -> 'PendingAck':
    """ Returns an acknowledgement that is yet to be written.
    """
    out = PendingAck()
    out.sub_key = sub_key
    out.msg_ids = msg_ids
    out.sequence_ids = sequence_ids
    out.removed_count = 0
    out.fully_delivered_count = 0
    out.exception = None
    out.is_fenced = False
    out.expected_attempts = None
    out.concluded_msg_ids = []

    return out

# ################################################################################################################################

def new_fenced_ack(sub_key:'str', msg_ids:'strlist', expected_attempts:'intlistnone') -> 'PendingAck':
    """ Returns an acknowledgement that is yet to be written under the fence, with the delivery attempt of each message
    that it expects, or None to accept any attempt.
    """
    out = new_pending_ack(sub_key, msg_ids, None)
    out.is_fenced = True
    out.expected_attempts = expected_attempts

    return out

# ################################################################################################################################

def new_pending_atomic(publications:'pending_publication_list', ack:'PendingAck', is_strict:'bool') -> 'PendingAtomic':
    """ Returns a fenced acknowledgement with its publications that is yet to be written.
    """
    out = PendingAtomic()
    out.publications = publications
    out.ack = ack
    out.is_strict = is_strict
    out.exception = None
    out.audit_events = []

    return out

# ################################################################################################################################

def new_pending_lease(
    sub_key:'str',
    max_messages:'int',
    max_len:'int',
    now_ms:'int',
    leased_until_ms:'int',
    on_leased:'callable_',
    ) -> 'PendingLease':
    """ Returns a pull that is yet to be written.
    """
    out = PendingLease()
    out.sub_key = sub_key
    out.max_messages = max_messages
    out.max_len = max_len
    out.now_ms = now_ms
    out.leased_until_ms = leased_until_ms
    out.rows = []
    out.attempts = {}
    out.on_leased = on_leased
    out.messages = []
    out.audit_events = []
    out.exception = None

    return out

# ################################################################################################################################

def new_pending_attempts(delivery_ids:'intlist') -> 'PendingAttempts':
    """ Returns the push attempts of a batch of deliveries that are yet to be written.
    """
    out = PendingAttempts()
    out.delivery_ids = delivery_ids
    out.attempts = {}
    out.exception = None

    return out

# ################################################################################################################################

def reset_item(item:'PendingPublication | PendingAck | PendingAtomic | PendingLease | PendingAttempts') -> 'None':
    """ Clears what a commit that was rolled back stored in one of its items.
    """
    if isinstance(item, PendingPublication):
        item.subscriber_keys = []
        item.exception = None
        item.is_repeat = False

    elif isinstance(item, PendingAck):
        item.removed_count = 0
        item.fully_delivered_count = 0
        item.exception = None
        item.concluded_msg_ids = []

    elif isinstance(item, PendingAtomic):
        for pending in item.publications:
            reset_item(pending)
        reset_item(item.ack)
        item.exception = None

    elif isinstance(item, PendingAttempts):
        item.attempts = {}
        item.exception = None

    else:
        item.rows = []
        item.attempts = {}
        item.messages = []
        item.audit_events = []
        item.exception = None

# ################################################################################################################################
# ################################################################################################################################
