# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The message partition channel store - the responder half of One-Way/Pull. A message queued here
# waits on its channel until a pull request asks for it, at which point it is handed over on the
# response of that very request and stays in flight until the receipt for it arrives. A message
# handed over but never acknowledged goes back to waiting, so a pull answered into a partner that
# never processed it is not a message lost.

from __future__ import annotations

# stdlib
from copy import copy
from dataclasses import dataclass
from datetime import timedelta

# SQLAlchemy
from sqlalchemy import func, select, update

# Zato
from zato.common.as4.audit import decode_payload_documents, encode_payloads
from zato.common.as4.ebms import new_message_id
from zato.common.as4.outbound import build_push_message, new_part
from zato.common.audit_log.api import get_audit_engine
from zato.common.audit_log.common import as4_pull_queue_table
from zato.common.json_internal import dumps, loads
from zato.common.typing_ import list_field
from zato.common.util.api import utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from zato.common.as4.pmode import PMode
    from zato.common.typing_ import any_, anylist, anytuple, strnone
    from zato.common.util.xml_.keystore import Keystore
    from zato.common.util.xml_.mime_ import part_list
    any_ = any_
    anylist = anylist
    anytuple = anytuple
    datetime = datetime
    Keystore = Keystore
    part_list = part_list
    PMode = PMode
    strnone = strnone

# ################################################################################################################################
# ################################################################################################################################

class PullState:
    """ What one queued message is doing - waiting for a pull request, handed over to one and
    awaiting its receipt, or acknowledged and done with.
    """
    Waiting   = 'waiting'
    In_Flight = 'in-flight'
    Done      = 'done'

# ################################################################################################################################

# How many rows one claim attempt walks through before giving up. A claim loses its row only to
# another server claiming the same one at the same time, so this is about concurrent pulls of one
# channel rather than about the length of the queue.
_max_claim_attempts = 20

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class QueuedMessage:
    """ One message waiting on a channel, as the pull that claims it receives it.
    """
    row_id: int = 0
    mpc:    str = ''

    from_party: str = ''
    to_party:   str = ''

    message_id:      str = ''
    conversation_id: str = ''

    service: str = ''
    action:  str = ''

    # How many pull requests this message has been handed over to, the one claiming it included.
    pull_count: int = 0

    # The payloads of the message, each as a (bytes, content type, content id) tuple.
    documents: 'anylist' = list_field()

# ################################################################################################################################
# ################################################################################################################################

def queue_message(
    mpc:'str',
    from_party:'str',
    to_party:'str',
    service:'str',
    action:'str',
    payloads:'part_list',
    conversation_id:'strnone' = None,
    ) -> 'str':
    """ Puts one message on a message partition channel for the partner to pull, and returns the
    eb:MessageId it will be handed over under. The id is assigned here rather than at hand-over
    time, so the receipt that eventually answers it has something to refer to from the moment
    the message exists.
    """
    message_id = new_message_id()

    if not conversation_id:
        conversation_id = message_id

    now = utcnow()
    now_iso = now.isoformat()

    details = {'payloads': encode_payloads(payloads)}

    values = {
        'mpc': mpc,
        'from_party': from_party,
        'to_party': to_party,
        'message_id': message_id,
        'conversation_id': conversation_id,
        'service': service,
        'action': action,
        'state': PullState.Waiting,
        'pull_count': 0,
        'queued_iso': now_iso,
        'claimed_iso': '',
        'data': dumps(details),
    }

    statement = as4_pull_queue_table.insert()
    statement = statement.values(**values)

    engine = get_audit_engine()

    with engine.begin() as connection:
        _ = connection.execute(statement)

    out = message_id
    return out

# ################################################################################################################################

def _new_queued_message(row:'any_') -> 'QueuedMessage':
    """ Turns one queue row into the message a pull hands over.
    """
    details = loads(row.data)

    # Our response to produce
    out = QueuedMessage()

    out.row_id = row.id
    out.mpc = row.mpc
    out.from_party = row.from_party
    out.to_party = row.to_party
    out.message_id = row.message_id
    out.conversation_id = row.conversation_id
    out.service = row.service
    out.action = row.action
    out.pull_count = row.pull_count + 1
    out.documents = decode_payload_documents(details)

    return out

# ################################################################################################################################

def _candidate_rows(engine:'any_', mpc:'str') -> 'anylist':
    """ Returns the rows waiting on one channel, oldest first - which is the order they were queued
    in and the order they are handed over in.
    """
    statement = select(
        as4_pull_queue_table.c.id,
        as4_pull_queue_table.c.mpc,
        as4_pull_queue_table.c.from_party,
        as4_pull_queue_table.c.to_party,
        as4_pull_queue_table.c.message_id,
        as4_pull_queue_table.c.conversation_id,
        as4_pull_queue_table.c.service,
        as4_pull_queue_table.c.action,
        as4_pull_queue_table.c.pull_count,
        as4_pull_queue_table.c.data,
    )
    statement = statement.where(as4_pull_queue_table.c.mpc == mpc)
    statement = statement.where(as4_pull_queue_table.c.state == PullState.Waiting)
    statement = statement.order_by(as4_pull_queue_table.c.id)
    statement = statement.limit(_max_claim_attempts)

    # Our response to produce
    out:'anylist' = []

    with engine.connect() as connection:
        for row in connection.execute(statement):
            out.append(row)

    return out

# ################################################################################################################################

def _claim_row(engine:'any_', row_id:'int', pull_count:'int') -> 'bool':
    """ Takes one waiting row for the pull request being served. The state the update requires is
    what makes the claim exclusive - two servers answering a pull of the same channel at the same
    moment cannot both hand over the same message, because only one of them changes the row.
    """
    now = utcnow()
    now_iso = now.isoformat()

    statement = update(as4_pull_queue_table)
    statement = statement.where(as4_pull_queue_table.c.id == row_id)
    statement = statement.where(as4_pull_queue_table.c.state == PullState.Waiting)
    statement = statement.values(state=PullState.In_Flight, claimed_iso=now_iso, pull_count=pull_count)

    with engine.begin() as connection:
        result = connection.execute(statement)
        claimed = result.rowcount

    out = claimed == 1
    return out

# ################################################################################################################################

def claim_next(mpc:'str') -> 'QueuedMessage | None':
    """ Takes the message that has waited longest on one channel and hands it to the pull request
    being served. A channel with nothing waiting on it hands over nothing, which is what the empty
    channel warning of a pull response says.
    """
    engine = get_audit_engine()

    for row in _candidate_rows(engine, mpc):

        out = _new_queued_message(row)

        # Another server may have taken this row a moment ago, in which case the next one is tried.
        if _claim_row(engine, out.row_id, out.pull_count):
            return out

    return None

# ################################################################################################################################

def complete(message_id:'str') -> 'bool':
    """ Closes the queue row of one message, which is what its receipt does - the message was pulled
    and acknowledged, so it is not to be handed over again. Returns whether a row was closed at all,
    because a receipt may answer a message that was pushed rather than pulled.
    """
    statement = update(as4_pull_queue_table)
    statement = statement.where(as4_pull_queue_table.c.message_id == message_id)
    statement = statement.where(as4_pull_queue_table.c.state == PullState.In_Flight)
    statement = statement.values(state=PullState.Done)

    engine = get_audit_engine()

    with engine.begin() as connection:
        result = connection.execute(statement)
        closed = result.rowcount

    out = closed > 0
    return out

# ################################################################################################################################

def requeue_stale(now:'datetime', timeout_seconds:'int') -> 'int':
    """ Puts back on their channels the messages that were handed over to a pull request whose
    receipt never arrived, and returns how many there were. The message goes out again under the
    eb:MessageId it was handed over under, so a partner that did process it the first time
    recognizes the second hand-over for what it is.
    """
    cutoff = now - timedelta(seconds=timeout_seconds)
    cutoff_iso = cutoff.isoformat()

    statement = update(as4_pull_queue_table)
    statement = statement.where(as4_pull_queue_table.c.state == PullState.In_Flight)
    statement = statement.where(as4_pull_queue_table.c.claimed_iso < cutoff_iso)
    statement = statement.values(state=PullState.Waiting, claimed_iso='')

    engine = get_audit_engine()

    with engine.begin() as connection:
        result = connection.execute(statement)
        out = result.rowcount

    return out

# ################################################################################################################################

def count_waiting(mpc:'str') -> 'int':
    """ Returns how many messages wait on one channel - what a partner would receive if it kept
    pulling, and what an operator reads the depth of a channel from.
    """
    statement = select(func.count()).select_from(as4_pull_queue_table)
    statement = statement.where(as4_pull_queue_table.c.mpc == mpc)
    statement = statement.where(as4_pull_queue_table.c.state == PullState.Waiting)

    engine = get_audit_engine()

    with engine.connect() as connection:
        result = connection.execute(statement)
        out = result.scalar()

    if out is None:
        out = 0

    return out

# ################################################################################################################################
# ################################################################################################################################

def build_parts(documents:'anylist') -> 'part_list':
    """ Wraps the payloads of a queued message in MIME parts again, each keeping the content type
    and the Content-ID it was queued with, so the message that is handed over is the one that was
    submitted for pulling.
    """

    # Our response to produce
    out:'part_list' = []

    for data, content_type, content_id in documents:
        part = new_part(data, content_type)
        part.content_id = content_id
        out.append(part)

    return out

# ################################################################################################################################

def build_response(pmode:'PMode', keystore:'Keystore', queued:'QueuedMessage') -> 'anytuple':
    """ Builds the user message one pull request is answered with - the same signed and optionally
    encrypted message a push would send, only travelling on the response of the request that asked
    for it.

    Returns the wire body, its content type and the payloads as they were submitted, because
    building the message compresses and encrypts them in place and the evidence of a hand-over
    is what was submitted rather than what the wire carried.
    """
    parts = build_parts(queued.documents)

    # The copies are shallow because the bytes they point at are never mutated, only replaced.
    submitted:'part_list' = []

    for part in parts:
        submitted.append(copy(part))

    body, content_type, _, _ = build_push_message(
        pmode, keystore, parts, queued.conversation_id, queued.message_id)

    out = body, content_type, submitted
    return out

# ################################################################################################################################
# ################################################################################################################################
