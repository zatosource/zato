# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The statements by which messages are read for delivery and handed out to pulling clients. A pull leases
# the delivery rows it hands out in the same transaction that reads them, and the rows its update returns
# are the only ones it hands out, so each message goes to exactly one of any number of concurrent pulls
# until its lease runs out. The subscriber's acknowledgement removes the rows.

# SQLAlchemy
from sqlalchemy import and_, bindparam, Boolean, or_, select

# Zato
from zato.common.api import HTTP_SOAP
from zato.common.pubsub.sql.schema import delivery_table, message_retry_columns, message_table

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Connection, Engine
    from sqlalchemy.sql.elements import ColumnElement
    from zato.common.typing_ import anydict, anylist, intdict, intlist
    from zato_common_core.zato_common_core import SubscriptionList

    # Dummy assignments to satisfy type checkers
    anylist = anylist
    ColumnElement = ColumnElement
    Connection = Connection
    Engine = Engine
    SubscriptionList = SubscriptionList

# ################################################################################################################################
# ################################################################################################################################

_retry = HTTP_SOAP.Retry

# ################################################################################################################################
# ################################################################################################################################

def _delivered_topics_filter(prefix:'str') -> 'ColumnElement[bool]':
    """ Returns the condition that keeps the delivery rows of the topics that the subscription list hands out
    to a subscriber, which holds for every row when the list restricts none.
    """
    is_unrestricted = bindparam(f'{prefix}_is_unrestricted', type_=Boolean())
    delivered_topics = bindparam(f'{prefix}_delivered_topics', expanding=True)

    out = or_(is_unrestricted, delivery_table.c.topic_name.in_(delivered_topics))
    return out

# ################################################################################################################################

def delivered_topics_parameters(subscription_list:'SubscriptionList', sub_key:'str', prefix:'str') -> 'anydict':
    """ Returns the parameters of the condition of _delivered_topics_filter for one subscriber.
    """
    delivered_topics = subscription_list.delivered_topics(sub_key)

    if delivered_topics is None:
        out = {
            f'{prefix}_is_unrestricted': True,
            f'{prefix}_delivered_topics': [],
        }
    else:
        out = {
            f'{prefix}_is_unrestricted': False,
            f'{prefix}_delivered_topics': delivered_topics,
        }

    return out

# ################################################################################################################################
# ################################################################################################################################

# The message columns that the conversion of rows into message dicts consumes.
message_columns = [
    message_table.c.id,
    message_table.c.msg_id,
    message_table.c.topic_name,
    message_table.c.payload,
    message_table.c.payload_encrypted,
    message_table.c.data_class,
    message_table.c.data_size,
    message_table.c.data_preview,
    message_table.c.priority,
    message_table.c.expiration,
    message_table.c.pub_time_iso,
    message_table.c.recv_time_iso,
    message_table.c.expiration_time_iso,
    message_table.c.publisher,
    message_table.c.cid,
    message_table.c.correl_id,
    message_table.c.in_reply_to,
    message_table.c.ext_client_id,
]
message_columns.extend(message_retry_columns)

# A fetch for push delivery reads the payloads apart from the other columns, because the server keeps the payloads
# of the messages that many subscribers receive, and it also reads its delivery row, whose attempts the delivery records.
_payload_columns = {message_table.c.payload.name, message_table.c.payload_encrypted.name}

_fetch_columns:'anylist' = [column for column in message_columns if column.name not in _payload_columns]
_fetch_columns.append(delivery_table.c.id.label('delivery_id'))
_fetch_columns.append(delivery_table.c.attempt)

# The fetch statement runs on every delivery, so it is built once here, not per call.
_fetch_join = delivery_table.join(message_table, message_table.c.id == delivery_table.c.message_id)

_order_by = [delivery_table.c.priority.desc(), delivery_table.c.message_id.asc()]

fetch_query = select(*_fetch_columns)
fetch_query = fetch_query.select_from(_fetch_join)
fetch_query = fetch_query.where(and_(
    delivery_table.c.sub_key == bindparam('fetch_sub_key'),
    delivery_table.c.expiration_ms > bindparam('fetch_now_ms'),
    _delivered_topics_filter('fetch'),
))
fetch_query = fetch_query.order_by(*_order_by)
fetch_query = fetch_query.limit(bindparam('fetch_max_messages'))

# The queue of an outgoing connection is fetched with its expired messages, which the delivery concludes in their turn
outgoing_fetch_query = select(*_fetch_columns)
outgoing_fetch_query = outgoing_fetch_query.select_from(_fetch_join)
outgoing_fetch_query = outgoing_fetch_query.where(delivery_table.c.sub_key == bindparam('fetch_sub_key'))
outgoing_fetch_query = outgoing_fetch_query.order_by(*_order_by)
outgoing_fetch_query = outgoing_fetch_query.limit(bindparam('fetch_max_messages'))

# The payloads of the fetched messages that the server does not keep yet.
payload_query = select(message_table.c.id, message_table.c.payload, message_table.c.payload_encrypted)
payload_query = payload_query.where(message_table.c.id.in_(bindparam('payload_message_ids', expanding=True)))

# ################################################################################################################################

# A pull first locks the deliverable rows it may hand out - those that no pull holds a lease on, or whose lease
# has run out - skipping those that a concurrent pull holds, without reading their payloads. The lock is
# FOR NO KEY UPDATE, which the key share locks that acknowledgements of other subscribers take on live delivery rows
# do not conflict with, so a pull never skips its own rows only because another subscriber acknowledged the same message ..
_lease_candidates_query = select(delivery_table.c.id, message_table.c.data_size)
_lease_candidates_query = _lease_candidates_query.select_from(_fetch_join)
_lease_candidates_query = _lease_candidates_query.where(and_(
    delivery_table.c.sub_key == bindparam('lease_sub_key'),
    delivery_table.c.expiration_ms > bindparam('lease_now_ms'),
    delivery_table.c.leased_until_ms < bindparam('lease_now_ms'),
    _delivered_topics_filter('lease'),
))
_lease_candidates_query = _lease_candidates_query.order_by(*_order_by)
_lease_candidates_query = _lease_candidates_query.limit(bindparam('lease_max_messages'))
_lease_candidates_query = _lease_candidates_query.with_for_update(skip_locked=True, key_share=True, of=delivery_table)

# Whether a pull would find anything to hand out, read before the pull waits for a commit to lease it in.
_lease_probe_query = select(delivery_table.c.id)
_lease_probe_query = _lease_probe_query.where(and_(
    delivery_table.c.sub_key == bindparam('probe_sub_key'),
    delivery_table.c.expiration_ms > bindparam('probe_now_ms'),
    delivery_table.c.leased_until_ms < bindparam('probe_now_ms'),
    _delivered_topics_filter('probe'),
))
_lease_probe_query = _lease_probe_query.limit(1)

# .. then leases those within its size budget, learning which of them it leased itself - a row that another pull
# .. leased in the meantime no longer matches ..
_lease_update = delivery_table.update()
_lease_update = _lease_update.where(and_(
    delivery_table.c.id.in_(bindparam('lease_delivery_ids', expanding=True)),
    delivery_table.c.leased_until_ms < bindparam('lease_now_ms'),
))
_lease_update = _lease_update.values(
    leased_until_ms=bindparam('lease_leased_until_ms'),
    attempt=delivery_table.c.attempt + 1,
)
_lease_update = _lease_update.returning(delivery_table.c.message_id, delivery_table.c.attempt)

# .. and reads the messages of the rows it leased.
_leased_messages_query = select(*message_columns)
_leased_messages_query = _leased_messages_query.where(
    message_table.c.id.in_(bindparam('lease_message_ids', expanding=True)))
_leased_messages_query = _leased_messages_query.order_by(message_table.c.priority.desc(), message_table.c.id.asc())

# ################################################################################################################################
# ################################################################################################################################

def has_lease_candidates(engine:'Engine', subscription_list:'SubscriptionList', sub_key:'str', now_ms:'int') -> 'bool':
    """ Whether one subscriber has a deliverable row that no pull holds a lease on, read without a lock and without
    a write, so that a pull that would hand out nothing does not wait for a commit.
    """
    parameters = delivered_topics_parameters(subscription_list, sub_key, 'probe')
    parameters['probe_sub_key'] = sub_key
    parameters['probe_now_ms'] = now_ms

    with engine.connect() as connection:
        row = connection.execute(_lease_probe_query, parameters).first()

    out = row is not None
    return out

# ################################################################################################################################

def lease_messages(
    connection:'Connection',
    subscription_list:'SubscriptionList',
    sub_key:'str',
    max_messages:'int',
    max_len:'int',
    now_ms:'int',
    leased_until_ms:'int',
) -> 'tuple[anylist, intdict]':
    """ Leases up to max_messages deliverable rows of one subscriber, whose payloads add up to at most max_len,
    until leased_until_ms, in the caller's transaction, and returns the rows of their messages with the attempt number
    of each, by message ID. The rows stay in the queue until the subscriber acknowledges them, so a pull whose response
    never reaches the subscriber loses nothing.
    """
    attempts:'intdict' = {}

    # The topics handed out are those of the subscription list as of the moment the candidates are locked ..
    parameters = delivered_topics_parameters(subscription_list, sub_key, 'lease')
    parameters['lease_sub_key'] = sub_key
    parameters['lease_now_ms'] = now_ms
    parameters['lease_max_messages'] = max_messages

    # .. lock the candidates ..
    candidates = connection.execute(_lease_candidates_query, parameters).fetchall()

    if not candidates:
        return [], attempts

    # .. keep those within the size budget, in the order of the queue, except that a message larger than the budget
    # .. is handed out by the pull that reaches it, after the messages ahead of it, and ends that pull,
    # .. so that it never holds up the queue ..
    delivery_ids:'intlist' = []
    total_len = 0

    for row in candidates:

        is_oversized = row.data_size > max_len

        if delivery_ids and total_len + row.data_size > max_len and not is_oversized:
            break

        total_len += row.data_size
        delivery_ids.append(row.id)

        if is_oversized:
            break

    # .. lease them, which only the first of two concurrent pulls succeeds in for any one row ..
    lease_parameters:'anydict' = {
        'lease_delivery_ids': delivery_ids,
        'lease_now_ms': now_ms,
        'lease_leased_until_ms': leased_until_ms,
    }

    message_ids:'intlist' = []

    for row in connection.execute(_lease_update, lease_parameters):
        message_ids.append(row.message_id)
        attempts[row.message_id] = row.attempt

    if not message_ids:
        return [], attempts

    # .. and read what is to be handed out.
    rows = connection.execute(_leased_messages_query, {'lease_message_ids': message_ids}).fetchall()

    out = (rows, attempts)
    return out

# ################################################################################################################################
# ################################################################################################################################
