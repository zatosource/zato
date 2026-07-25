# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The outgoing queue of asynchronous MDNs. A receipt the sender asked to have delivered to a
# separate URL cannot ride on the HTTP response, so it goes out afterwards - and a receipt held
# only in a greenlet is lost the moment the process stops, which leaves the sender waiting for
# a receipt that will never arrive. The queue persists each one in the audit database before the
# inbound POST is answered, so a restart resumes delivery instead of dropping the evidence.
#
# The row is the queue: it is written when the message is accepted, it is deleted when the peer
# accepts the receipt, and until then it carries when the next attempt is due. That makes the
# scheduler-driven drain and the immediate attempt after the POST the same operation.

from __future__ import annotations

# stdlib
from dataclasses import dataclass
from datetime import datetime, timedelta
from logging import getLogger

# httpx
import httpx

# SQLAlchemy
from sqlalchemy import BigInteger, Column, Index, Integer, LargeBinary, MetaData, select, String, Table, Text, \
    UniqueConstraint
from sqlalchemy.exc import IntegrityError

# Zato
from zato.common.api import AS2
from zato.common.audit_log.api import get_audit_engine
from zato.common.db_env import ensure_column_types
from zato.common.json_internal import dumps, loads
from zato.common.util.api import utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Engine
    from zato.common.as2.inbound import PendingAsyncMDN
    from zato.common.typing_ import any_, callable_, strstrdict
    any_ = any_
    callable_ = callable_
    Engine = Engine
    PendingAsyncMDN = PendingAsyncMDN
    strstrdict = strstrdict

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

#  Type aliases
queued_async_mdn_list = list['QueuedAsyncMDN']

# ################################################################################################################################
# ################################################################################################################################

# Maximum length of the identifier columns.
_short_column_len = 255

# Maximum length of the destination URL column.
_url_column_len = 2048

# ################################################################################################################################
# ################################################################################################################################

# The queue lives in the same database the audit log uses, with a unique constraint on the
# identity triple - a replayed message must not enqueue its receipt a second time, because the
# receipt of the first delivery is the one the peer is owed.
metadata = MetaData()

# Row identifiers are 64-bit, except under SQLite where the autoincrement
# primary key must be a plain INTEGER to become an alias of the built-in rowid.
_id_column_type = BigInteger().with_variant(Integer(), 'sqlite')

async_mdn_table = Table('as2_async_mdn', metadata,
    Column('id', _id_column_type, primary_key=True, autoincrement=True),
    Column('as2_from', String(_short_column_len)),
    Column('as2_to', String(_short_column_len)),
    Column('message_id', String(_short_column_len)),
    Column('channel_name', String(_short_column_len)),
    Column('cid', String(_short_column_len)),
    Column('url', String(_url_column_len)),
    Column('body', LargeBinary),
    Column('headers', Text),

    # How the delivery is to be made - the partnership is not consulted again, because the
    # attempt that resumes after a restart runs with no channel of its own.
    Column('verify_tls', Integer),
    Column('timeout_seconds', Integer),

    # How many attempts were already made and when the next one is due, which is what
    # turns the table into a queue.
    Column('attempt_count', Integer),
    Column('next_attempt_iso', String(_short_column_len)),
    Column('created_iso', String(_short_column_len)),

    UniqueConstraint('as2_from', 'as2_to', 'message_id', name='uq_as2_async_mdn_message'),

    # The drain reads by due time and retention deletes by creation time, both of which
    # would otherwise read the whole table on every run.
    Index('idx_as2_async_mdn_next_attempt', 'next_attempt_iso'),
    Index('idx_as2_async_mdn_created', 'created_iso'),
)

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class QueuedAsyncMDN:
    """ One asynchronous MDN waiting to be delivered, as the queue stores it.
    """
    id: int = 0

    as2_from:     str = ''
    as2_to:       str = ''
    message_id:   str = ''
    channel_name: str = ''
    cid:          str = ''

    url:     str = ''
    body:    bytes = b''
    headers: 'strstrdict'

    verify_tls:      bool = True
    timeout_seconds: int = 0

    # How many attempts have already been made against this receipt.
    attempt_count: int = 0

# ################################################################################################################################
# ################################################################################################################################

def get_retry_delay(attempt_count:'int') -> 'timedelta':
    """ Returns how long to wait before the attempt that follows the given number of failures.

    The wait doubles per failure so that a destination which is down does not get hammered, and
    it stops doubling at the ceiling so that a receipt still goes out once an hour for as long as
    the queue keeps it - a partner whose endpoint returns in the morning gets its receipt then.
    """
    delay_seconds = AS2.Async_MDN.First_Retry_Seconds * 2 ** (attempt_count - 1)

    if delay_seconds > AS2.Async_MDN.Max_Retry_Seconds:
        delay_seconds = AS2.Async_MDN.Max_Retry_Seconds

    out = timedelta(seconds=delay_seconds)
    return out

# ################################################################################################################################
# ################################################################################################################################

class AsyncMDNQueue:
    """ The persisted queue of asynchronous MDNs awaiting delivery.
    """

    def __init__(self, engine:'Engine | None'=None) -> 'None':

        # The queue shares the audit log's database unless the caller brought its own engine.
        if engine is None:
            engine = get_audit_engine()

        self.engine:'Engine' = engine

        # The schema creation is idempotent, the same way the audit log's is,
        # and databases created by older releases may still hold the id as 32-bit.
        metadata.create_all(self.engine)
        ensure_column_types(self.engine, async_mdn_table)

# ################################################################################################################################

    def enqueue(
        self,
        as2_from:'str',
        as2_to:'str',
        message_id:'str',
        pending:'PendingAsyncMDN',
        channel_name:'str',
        cid:'str',
        now:'datetime | None'=None,
        ) -> 'int':
        """ Persists one receipt as due immediately, returning the row id it can be completed by.

        A message whose receipt is already queued returns zero - that is a replay of a message
        whose first delivery is still waiting to be acknowledged, and the queued receipt is
        already the one the peer is owed.
        """
        if now is None:
            now = utcnow()

        now_iso = now.isoformat()
        headers_json = dumps(pending.headers)

        # The database column is an integer, the same way SQLite would store the boolean anyway.
        if pending.verify_tls:
            verify_tls = 1
        else:
            verify_tls = 0

        insert = async_mdn_table.insert()
        insert_statement = insert.values(
            as2_from=as2_from,
            as2_to=as2_to,
            message_id=message_id,
            channel_name=channel_name,
            cid=cid,
            url=pending.url,
            body=pending.body,
            headers=headers_json,
            verify_tls=verify_tls,
            timeout_seconds=pending.timeout_seconds,
            attempt_count=0,
            next_attempt_iso=now_iso,
            created_iso=now_iso,
        )

        # A constraint violation means this message's receipt is already in the queue.
        try:
            with self.engine.begin() as connection:
                result = connection.execute(insert_statement)
        except IntegrityError:
            logger.info('AS2 async MDN for message `%s` is already queued; cid:%s', message_id, cid)
            return 0

        out = result.inserted_primary_key[0]
        return out

# ################################################################################################################################

    def get(self, row_id:'int') -> 'QueuedAsyncMDN | None':
        """ Returns one queued receipt by its row id, or None when it was already delivered.
        """
        statement = self._new_select().where(async_mdn_table.c.id == row_id)

        with self.engine.connect() as connection:
            result = connection.execute(statement)
            row = result.first()

        if row is None:
            return None

        out = self._to_queued(row)
        return out

# ################################################################################################################################

    def due(self, now:'datetime', limit:'int'=AS2.Async_MDN.Batch_Size) -> 'queued_async_mdn_list':
        """ Returns the receipts whose next attempt is due, oldest first, up to one batch.

        The batch is what keeps a long outage from turning the drain into a run over the whole
        queue at once - the rest stays due and the next run picks it up.
        """
        now_iso = now.isoformat()

        statement = self._new_select().where(
            async_mdn_table.c.next_attempt_iso <= now_iso,
        ).order_by(async_mdn_table.c.next_attempt_iso).limit(limit)

        with self.engine.connect() as connection:
            result = connection.execute(statement)
            rows = result.fetchall()

        # Our response to produce
        out:'queued_async_mdn_list' = []

        for row in rows:
            item = self._to_queued(row)
            out.append(item)

        return out

# ################################################################################################################################

    def complete(self, row_id:'int') -> 'None':
        """ Removes one receipt from the queue, which is what a delivered receipt means -
        the evidence itself lives in the audit log, the queue row only tracked the delivery.
        """
        delete = async_mdn_table.delete()
        delete_statement = delete.where(async_mdn_table.c.id == row_id)

        with self.engine.begin() as connection:
            _ = connection.execute(delete_statement)

# ################################################################################################################################

    def reschedule(self, row_id:'int', attempt_count:'int', now:'datetime') -> 'datetime':
        """ Records one failed attempt and returns when the next one is due.
        """
        next_attempt = now + get_retry_delay(attempt_count)

        update = async_mdn_table.update()
        update_statement = update.where(async_mdn_table.c.id == row_id).values(
            attempt_count=attempt_count,
            next_attempt_iso=next_attempt.isoformat(),
        )

        with self.engine.begin() as connection:
            _ = connection.execute(update_statement)

        return next_attempt

# ################################################################################################################################

    def run_retention(self, now:'datetime') -> 'int':
        """ Removes the receipts that have been in the queue longer than the retention window,
        returning how many were dropped. A destination that has been unreachable for that long
        is not going to accept a receipt whose message the sender has long since resent.
        """
        cutoff = now - timedelta(days=AS2.Async_MDN.Retention_Days)
        cutoff_iso = cutoff.isoformat()

        delete = async_mdn_table.delete()
        delete_statement = delete.where(async_mdn_table.c.created_iso < cutoff_iso)

        with self.engine.begin() as connection:
            result = connection.execute(delete_statement)

        out = result.rowcount

        if out:
            suffix = 'receipt' if out == 1 else 'receipts'
            logger.warning('AS2 async MDN queue dropped %d undelivered %s older than %s', out, suffix, cutoff_iso)

        return out

# ################################################################################################################################

    def _new_select(self) -> 'any_':
        """ Returns the column list every read of the queue shares.
        """
        out = select(
            async_mdn_table.c.id,
            async_mdn_table.c.as2_from,
            async_mdn_table.c.as2_to,
            async_mdn_table.c.message_id,
            async_mdn_table.c.channel_name,
            async_mdn_table.c.cid,
            async_mdn_table.c.url,
            async_mdn_table.c.body,
            async_mdn_table.c.headers,
            async_mdn_table.c.verify_tls,
            async_mdn_table.c.timeout_seconds,
            async_mdn_table.c.attempt_count,
        )

        return out

# ################################################################################################################################

    def _to_queued(self, row:'any_') -> 'QueuedAsyncMDN':
        """ Turns one row of the queue into the receipt it describes.
        """
        row_id, as2_from, as2_to, message_id, channel_name, cid, url, body, headers, verify_tls, timeout_seconds, \
            attempt_count = row

        out = QueuedAsyncMDN()

        out.id = row_id
        out.as2_from = as2_from
        out.as2_to = as2_to
        out.message_id = message_id
        out.channel_name = channel_name
        out.cid = cid
        out.url = url
        out.body = body
        out.headers = loads(headers)
        out.verify_tls = verify_tls == 1
        out.timeout_seconds = timeout_seconds
        out.attempt_count = attempt_count

        return out

# ################################################################################################################################
# ################################################################################################################################

def post_async_mdn(item:'QueuedAsyncMDN') -> 'int':
    """ Delivers one queued receipt over HTTP, returning the status code the destination answered
    with. The timeout is what keeps a destination that accepts the connection and then says
    nothing from holding the caller for as long as it likes.
    """
    response = httpx.post(
        item.url,
        content=item.body,
        headers=item.headers,
        timeout=item.timeout_seconds,
        verify=item.verify_tls,
    )

    out = response.status_code
    return out

# ################################################################################################################################
# ################################################################################################################################

def deliver(queue:'AsyncMDNQueue', item:'QueuedAsyncMDN', post:'callable_', now:'datetime') -> 'bool':
    """ Makes one delivery attempt at one queued receipt, returning whether the peer accepted it.

    A receipt the peer accepted leaves the queue. A failed attempt stays, with its next attempt
    scheduled further out, until the attempt ceiling is reached - past that point the sender has
    long since had its own overdue-MDN alert, and keeping the row would only repeat a request
    to a destination that has stopped answering.
    """
    attempt_count = item.attempt_count + 1

    try:
        status_code = post(item)

    # The peer's endpoint is an external boundary - anything it does is an attempt that failed.
    except Exception as e:
        logger.warning('AS2 async MDN delivery to `%s` failed on attempt %d for message `%s`; cid:%s; e:`%s`',
            item.url, attempt_count, item.message_id, item.cid, e)
        is_delivered = False

    else:
        is_delivered = 200 <= status_code < 300

        if is_delivered:
            logger.info('AS2 async MDN delivered to `%s` (HTTP %d) for message `%s`; cid:%s',
                item.url, status_code, item.message_id, item.cid)
        else:
            logger.warning('AS2 async MDN refused by `%s` (HTTP %d) on attempt %d for message `%s`; cid:%s',
                item.url, status_code, attempt_count, item.message_id, item.cid)

    # A delivered receipt has nothing left to track.
    if is_delivered:
        queue.complete(item.id)
        return True

    # An attempt past the ceiling is given up on, loudly - the receipt is gone and the audit log
    # is where the operator sees that the peer never got it.
    if attempt_count >= AS2.Async_MDN.Max_Attempts:
        logger.error('AS2 async MDN for message `%s` given up on after %d attempts to `%s`; cid:%s',
            item.message_id, attempt_count, item.url, item.cid)
        queue.complete(item.id)
        return False

    next_attempt = queue.reschedule(item.id, attempt_count, now)

    logger.info('AS2 async MDN for message `%s` rescheduled to %s after attempt %d; cid:%s',
        item.message_id, next_attempt.isoformat(), attempt_count, item.cid)

    return False

# ################################################################################################################################

def deliver_due(queue:'AsyncMDNQueue', post:'callable_', now:'datetime') -> 'int':
    """ Runs one drain of the queue, returning how many receipts the peers accepted.
    """
    items = queue.due(now)

    # Our response to produce
    out = 0

    for item in items:
        if deliver(queue, item, post, now):
            out += 1

    return out

# ################################################################################################################################
# ################################################################################################################################
