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
from sqlalchemy import and_, bindparam, select

# Zato
from zato.common.api import HTTP_SOAP
from zato.common.pubsub.sql.schema import delivery_table, message_retry_columns, message_table

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Engine
    from zato.common.typing_ import anydict, anylist, intlist

    # Dummy assignments to satisfy type checkers
    anylist = anylist
    Engine = Engine

# ################################################################################################################################
# ################################################################################################################################

_retry = HTTP_SOAP.Retry

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

# A fetch for push delivery also reads its delivery row, whose attempts the delivery records.
_fetch_columns:'anylist' = list(message_columns)
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
))
fetch_query = fetch_query.order_by(*_order_by)
fetch_query = fetch_query.limit(bindparam('fetch_max_messages'))

# The queue of an outgoing connection is fetched with its expired messages, which the delivery concludes in their turn
outgoing_fetch_query = select(*_fetch_columns)
outgoing_fetch_query = outgoing_fetch_query.select_from(_fetch_join)
outgoing_fetch_query = outgoing_fetch_query.where(delivery_table.c.sub_key == bindparam('fetch_sub_key'))
outgoing_fetch_query = outgoing_fetch_query.order_by(*_order_by)
outgoing_fetch_query = outgoing_fetch_query.limit(bindparam('fetch_max_messages'))

# ################################################################################################################################

# A pull first locks the deliverable rows it may hand out - those that no pull holds a lease on, or whose lease
# has run out - skipping those that a concurrent pull holds, without reading their payloads ..
_claim_candidates_query = select(delivery_table.c.id, message_table.c.data_size)
_claim_candidates_query = _claim_candidates_query.select_from(_fetch_join)
_claim_candidates_query = _claim_candidates_query.where(and_(
    delivery_table.c.sub_key == bindparam('claim_sub_key'),
    delivery_table.c.expiration_ms > bindparam('claim_now_ms'),
    delivery_table.c.leased_until_ms < bindparam('claim_now_ms'),
))
_claim_candidates_query = _claim_candidates_query.order_by(*_order_by)
_claim_candidates_query = _claim_candidates_query.limit(bindparam('claim_max_messages'))
_claim_candidates_query = _claim_candidates_query.with_for_update(skip_locked=True, of=delivery_table)

# .. then leases those within its size budget, learning which of them it leased itself - a row that another pull
# .. leased in the meantime no longer matches ..
_claim_lease = delivery_table.update()
_claim_lease = _claim_lease.where(and_(
    delivery_table.c.id.in_(bindparam('claim_delivery_ids', expanding=True)),
    delivery_table.c.leased_until_ms < bindparam('claim_now_ms'),
))
_claim_lease = _claim_lease.values(
    leased_until_ms=bindparam('claim_leased_until_ms'),
    attempt=delivery_table.c.attempt + 1,
)
_claim_lease = _claim_lease.returning(delivery_table.c.message_id)

# .. and reads the messages of the rows it leased.
_claimed_messages_query = select(*message_columns)
_claimed_messages_query = _claimed_messages_query.where(
    message_table.c.id.in_(bindparam('claim_message_ids', expanding=True)))
_claimed_messages_query = _claimed_messages_query.order_by(message_table.c.priority.desc(), message_table.c.id.asc())

# ################################################################################################################################
# ################################################################################################################################

def claim_messages(
    engine:'Engine',
    sub_key:'str',
    max_messages:'int',
    max_len:'int',
    now_ms:'int',
    leased_until_ms:'int',
) -> 'anylist':
    """ Leases up to max_messages deliverable rows of one subscriber, whose payloads add up to at most max_len,
    until leased_until_ms, and returns the rows of their messages. The rows stay in the queue until the subscriber
    acknowledges them, so a pull whose response never reaches the subscriber loses nothing.
    """
    parameters:'anydict' = {
        'claim_sub_key': sub_key,
        'claim_now_ms': now_ms,
        'claim_max_messages': max_messages,
    }

    with engine.begin() as connection:

        # Lock the candidates ..
        candidates = connection.execute(_claim_candidates_query, parameters).fetchall()

        if not candidates:
            return []

        # .. keep those within the size budget, except that a message larger than the budget
        # .. is handed out alone rather than holding up the queue ..
        delivery_ids:'intlist' = []
        total_len = 0

        for row in candidates:

            if delivery_ids and total_len + row.data_size > max_len:
                break

            total_len += row.data_size
            delivery_ids.append(row.id)

        # .. lease them, which only the first of two concurrent pulls succeeds in for any one row ..
        lease_parameters:'anydict' = {
            'claim_delivery_ids': delivery_ids,
            'claim_now_ms': now_ms,
            'claim_leased_until_ms': leased_until_ms,
        }

        message_ids:'intlist' = []

        for row in connection.execute(_claim_lease, lease_parameters):
            message_ids.append(row.message_id)

        if not message_ids:
            return []

        # .. and read what is to be handed out.
        out = connection.execute(_claimed_messages_query, {'claim_message_ids': message_ids}).fetchall()

    return out

# ################################################################################################################################
# ################################################################################################################################
