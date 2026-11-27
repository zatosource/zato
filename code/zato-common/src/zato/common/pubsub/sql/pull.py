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
from sqlalchemy import and_, bindparam, Boolean, false, func, not_, or_, select

# Zato
from zato.common.api import HTTP_SOAP
from zato.common.db_env.any_of import any_of
from zato.common.db_env.plain_sql import PlainStatement
from zato.common.pubsub.sql.schema import delivery_table, message_retry_columns, message_table

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Connection, Engine
    from sqlalchemy.sql.elements import ColumnElement
    from zato.common.typing_ import anydict, anylist, intdict
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
    is_delivered = any_of(delivery_table.c.topic_name, f'{prefix}_delivered_topics')

    out = or_(is_unrestricted, is_delivered)
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
    message_table.c.payload_base64,
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
_payload_columns = {message_table.c.payload.name, message_table.c.payload_encrypted.name, message_table.c.payload_base64.name}

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
payload_query = select(message_table.c.id, message_table.c.payload, message_table.c.payload_encrypted,
    message_table.c.payload_base64)
payload_query = payload_query.where(any_of(message_table.c.id, 'payload_message_ids'))

# The statements above, executed as plain SQL
fetch_statement          = PlainStatement(fetch_query)
outgoing_fetch_statement = PlainStatement(outgoing_fetch_query)
payload_statement        = PlainStatement(payload_query)

# ################################################################################################################################

# A pull leases its messages in one statement. It first locks the deliverable rows it may hand out - those that no pull
# holds a lease on, or whose lease has run out - skipping those that a concurrent pull holds, without reading their
# payloads. The lock is FOR NO KEY UPDATE, which the key share locks that acknowledgements of other subscribers take
# on live delivery rows do not conflict with, so a pull never skips its own rows only because another subscriber
# acknowledged the same message ..
_lease_candidates = select(delivery_table.c.id, message_table.c.data_size, delivery_table.c.priority,
    delivery_table.c.message_id)
_lease_candidates = _lease_candidates.select_from(_fetch_join)
_lease_candidates = _lease_candidates.where(and_(
    delivery_table.c.sub_key == bindparam('lease_sub_key'),
    delivery_table.c.expiration_ms > bindparam('lease_now_ms'),
    delivery_table.c.leased_until_ms < bindparam('lease_now_ms'),
    _delivered_topics_filter('lease'),
))
_lease_candidates = _lease_candidates.order_by(*_order_by)
_lease_candidates = _lease_candidates.limit(bindparam('lease_max_messages'))
_lease_candidates = _lease_candidates.with_for_update(skip_locked=True, key_share=True, of=delivery_table)
_lease_candidates = _lease_candidates.cte('lease_candidates')
_lease_candidates = _lease_candidates.prefix_with('MATERIALIZED')

# .. then keeps those within the size budget, in the order of the queue, except that a message larger than the budget
# .. is handed out by the pull that reaches it, after the messages ahead of it, and ends that pull, so that it never
# .. holds up the queue. A row is kept when no row ahead of it is larger than the budget, the rows ahead of it are within
# .. the budget, and either the rows up to and including it are within the budget or it is larger than the budget alone.
# .. The window functions have a query level of their own, since they cannot share one with a row lock ..
_lease_queue_order = [_lease_candidates.c.priority.desc(), _lease_candidates.c.message_id.asc()]
_lease_rows_before = (None, -1)
_lease_rows_including = (None, 0)

_lease_is_oversized = _lease_candidates.c.data_size > bindparam('lease_max_len')

_lease_len_before = func.sum(_lease_candidates.c.data_size).over(order_by=_lease_queue_order, rows=_lease_rows_before)
_lease_len_including = func.sum(_lease_candidates.c.data_size).over(order_by=_lease_queue_order, rows=_lease_rows_including)
_lease_oversized_before = func.bool_or(_lease_is_oversized).over(order_by=_lease_queue_order, rows=_lease_rows_before)

_lease_budget = select(
    _lease_candidates.c.id,
    func.coalesce(_lease_len_before, 0).label('len_before'),
    _lease_len_including.label('len_including'),
    func.coalesce(_lease_oversized_before, false()).label('oversized_before'),
    _lease_is_oversized.label('is_oversized'),
)
_lease_budget = _lease_budget.cte('lease_budget')

# .. then leases the rows it kept, learning which of them it leased itself - a row that another pull leased
# .. in the meantime no longer matches ..
_lease_update = delivery_table.update()
_lease_update = _lease_update.where(and_(
    delivery_table.c.id == _lease_budget.c.id,
    not_(_lease_budget.c.oversized_before),
    _lease_budget.c.len_before <= bindparam('lease_max_len'),
    or_(_lease_budget.c.len_including <= bindparam('lease_max_len'), _lease_budget.c.is_oversized),
    delivery_table.c.leased_until_ms < bindparam('lease_now_ms'),
))
_lease_update = _lease_update.values(
    leased_until_ms=bindparam('lease_leased_until_ms'),
    attempt=delivery_table.c.attempt + 1,
)
_lease_update = _lease_update.returning(delivery_table.c.message_id, delivery_table.c.attempt)
_lease_leased = _lease_update.cte('lease_leased')

# .. and reads the messages of the rows it leased, each with the attempt number of its delivery after the columns
# .. of the message, which the builder of pulled messages reads by their positions.
_lease_query = select(*message_columns, _lease_leased.c.attempt.label('lease_attempt'))
_lease_query = _lease_query.select_from(_lease_leased.join(message_table, message_table.c.id == _lease_leased.c.message_id))
_lease_query = _lease_query.order_by(message_table.c.priority.desc(), message_table.c.id.asc())

_lease_statement = PlainStatement(_lease_query)

# Whether a pull would find anything to hand out, read before the pull waits for a commit to lease it in.
_lease_probe_query = select(delivery_table.c.id)
_lease_probe_query = _lease_probe_query.where(and_(
    delivery_table.c.sub_key == bindparam('probe_sub_key'),
    delivery_table.c.expiration_ms > bindparam('probe_now_ms'),
    delivery_table.c.leased_until_ms < bindparam('probe_now_ms'),
    _delivered_topics_filter('probe'),
))
_lease_probe_query = _lease_probe_query.limit(1)

_lease_probe_statement = PlainStatement(_lease_probe_query)

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
        row = _lease_probe_statement.execute(connection, parameters).first()

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
    parameters['lease_max_len'] = max_len
    parameters['lease_leased_until_ms'] = leased_until_ms

    # .. the statement locks, budgets and leases the rows and returns their messages ..
    rows:'anylist' = []
    rows.extend(_lease_statement.execute(connection, parameters))

    # .. each with the attempt number of its delivery.
    for row in rows:
        attempts[row.id] = row.lease_attempt

    out = (rows, attempts)
    return out

# ################################################################################################################################
# ################################################################################################################################
