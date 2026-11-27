# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The payloads of the audit log, each stored once in the payload table under the digest of its content,
# however many events have it. An event references its payload by the id of the payload's row, and a payload
# is deleted when the last event referencing it is deleted or pruned.
#
# A writer locks the payload rows it references before it inserts the missing ones,
# and a deletion locks them for update before it checks for references in a statement of its own,
# so that a payload is never deleted while a transaction that has not committed yet references it.

from __future__ import annotations

# stdlib
from hashlib import blake2b

# SQLAlchemy
from sqlalchemy import and_, false, select
from sqlalchemy.dialects.postgresql import insert as postgresql_insert

# Zato
from zato.common.audit_log.common import event_payload_table, event_table
from zato.common.db_env.any_of import any_of
from zato.common.db_env.plain_sql import PlainStatement
from zato.common.pubsub.sql.schema import message_table

# Zato - Rust
from zato_common_core.zato_common_core import extract_search_text

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Connection, CursorResult
    from zato.common.audit_log.pending import pending_event_list
    from zato.common.typing_ import any_, anydict, dictlist, intlist, intnone, strintdict, strlist, strnone, strstrdict

    # Dummy assignments to satisfy type checkers
    any_ = any_
    anydict = anydict
    Connection = Connection
    CursorResult = CursorResult
    pending_event_list = pending_event_list
    dictlist = dictlist
    intlist = intlist
    intnone = intnone
    strintdict = strintdict
    strlist = strlist
    strnone = strnone
    strstrdict = strstrdict

# ################################################################################################################################
# ################################################################################################################################

# How many bytes a digest of a payload has
_digest_size = 16

# The key of an event row under which get_event_rows gives the digest of the event's payload, which insert_events
# replaces with the id of the payload's row.
Payload_Digest_Key = 'payload_digest'

# The insert that skips a payload that is stored already and returns the id and the digest of each row it inserted
_payload_insert = postgresql_insert(event_payload_table)
_payload_insert = _payload_insert.on_conflict_do_nothing(index_elements=[event_payload_table.c.digest])
_payload_insert = _payload_insert.returning(event_payload_table.c.id, event_payload_table.c.digest)
_payload_insert_statement = PlainStatement(_payload_insert)

# The ids and the digests of the payloads of the given digests that are stored already, locked
# against a concurrent deletion. Every transaction locks payloads in the order of their digests,
# so that no two of them wait for each other.
_stored_payloads_query = select(event_payload_table.c.id, event_payload_table.c.digest)
_stored_payloads_query = _stored_payloads_query.where(
    any_of(event_payload_table.c.digest, 'payload_digests'))
_stored_payloads_query = _stored_payloads_query.order_by(event_payload_table.c.digest)
_stored_payloads_query = _stored_payloads_query.with_for_update(read=True, key_share=True)
_stored_payloads_statement = PlainStatement(_stored_payloads_query)

# The payloads of the given ids, locked against a concurrent reference, in the order of their digests
_deleted_payloads_query = select(event_payload_table.c.id)
_deleted_payloads_query = _deleted_payloads_query.where(
    any_of(event_payload_table.c.id, 'payload_ids'))
_deleted_payloads_query = _deleted_payloads_query.order_by(event_payload_table.c.digest)
_deleted_payloads_query = _deleted_payloads_query.with_for_update()

# The deletion of the payloads of the given ids that neither an event nor a pub/sub message that has not dropped
# its payload references
_is_referenced = select(event_table.c.id)
_is_referenced = _is_referenced.where(event_table.c.payload_id == event_payload_table.c.id)
_is_referenced = _is_referenced.exists()

_is_message_payload = select(message_table.c.id)
_is_message_payload = _is_message_payload.where(and_(
    message_table.c.payload_id == event_payload_table.c.id,
    message_table.c.payload_dropped.is_(false()),
))
_is_message_payload = _is_message_payload.exists()

_unreferenced_payloads_delete = event_payload_table.delete()
_unreferenced_payloads_delete = _unreferenced_payloads_delete.where(
    any_of(event_payload_table.c.id, 'payload_ids'))
_unreferenced_payloads_delete = _unreferenced_payloads_delete.where(~_is_referenced)
_unreferenced_payloads_delete = _unreferenced_payloads_delete.where(~_is_message_payload)

# ################################################################################################################################
# ################################################################################################################################

def get_payload_digest(data:'str') -> 'strnone':
    """ Returns the digest a payload is stored under, or None for an empty payload, which is not stored.
    """
    if not data:
        return None

    encoded = data.encode('utf8')

    out = blake2b(encoded, digest_size=_digest_size).hexdigest()
    return out

# ################################################################################################################################

def prepare_payloads(batch:'pending_event_list') -> 'None':
    """ Computes the digest and the search text of the payload of each event of a batch, before the write
    that stores them, so that the transaction of the write is shorter. Each distinct payload
    of the batch is processed once, however many events carry it.
    """

    # The digest of each payload of the batch, by the payload, and the search text of each digest
    digest_by_data:'anydict' = {}
    search_text_by_digest:'strstrdict' = {}

    for pending in batch:

        data = pending.values['data']

        # A payload already seen in this batch is reused ..
        if data in digest_by_data:
            digest = digest_by_data[data]

        # .. while any other one is digested and its words are extracted.
        else:
            digest = get_payload_digest(data)
            digest_by_data[data] = digest

            if digest:
                search_text_by_digest[digest] = extract_search_text(data)

        pending.payload_digest = digest

        if digest:
            pending.search_text = search_text_by_digest[digest]

        pending.is_payload_prepared = True

# ################################################################################################################################

def get_event_rows(batch:'pending_event_list', payloads:'strstrdict', search_texts:'strstrdict') -> 'dictlist':
    """ Returns the rows of the event table of a batch of events, each with the digest of its payload
    under Payload_Digest_Key, adds each payload to the given dict under its digest, and adds the search text
    of each prepared payload to the other dict under its digest. The digests of the events that were not prepared
    are computed here, each distinct payload of the batch once, however many events have it.
    """
    out:'dictlist' = []

    # The digest of each payload of the batch that was not prepared, by the payload
    digest_by_data:'anydict' = {}

    for pending in batch:

        event_row = dict(pending.values)
        data = event_row.pop('data')

        # A prepared event carries its digest and search text ..
        if pending.is_payload_prepared:
            digest = pending.payload_digest

            if digest:
                search_texts[digest] = pending.search_text

        # .. while the digest of any other one is computed now.
        elif data in digest_by_data:
            digest = digest_by_data[data]

        else:
            digest = get_payload_digest(data)
            digest_by_data[data] = digest

        if digest:
            payloads[digest] = data

        event_row[Payload_Digest_Key] = digest
        out.append(event_row)

    return out

# ################################################################################################################################

def assign_payload_ids(rows:'dictlist', payload_ids:'strintdict') -> 'None':
    """ Replaces the digest of the payload of each event row of get_event_rows with the id of the payload's row,
    or with None for an event without a payload.
    """
    for row in rows:
        if digest := row.pop(Payload_Digest_Key):
            row['payload_id'] = payload_ids[digest]
        else:
            row['payload_id'] = None

# ################################################################################################################################

def store_payloads(connection:'Connection', payloads:'strstrdict', search_texts:'strstrdict') -> 'strintdict':
    """ Stores the given payloads, keyed by their digests, that are not stored yet, in the transaction of the connection,
    with the search texts of the given dict, keyed by the same digests, and with search texts extracted here
    for the payloads that dict has none for. Returns the id of the row of each payload by its digest.
    """
    stored = find_stored_payloads(connection, payloads)

    out = insert_new_payloads(connection, stored, payloads, search_texts)
    return out

# ################################################################################################################################

def find_stored_payloads(connection:'Connection', payloads:'strstrdict') -> 'CursorResult[any_]':
    """ Finds which of the given payloads, keyed by their digests, are stored already, and locks them,
    so that no deletion removes them before this transaction commits the events that reference them.
    The rows of the result are read by insert_new_payloads.
    """
    digests = sorted(payloads)

    out = _stored_payloads_statement.execute(connection, {'payload_digests': digests})
    return out

# ################################################################################################################################

def insert_new_payloads(
    connection:'Connection',
    stored:'CursorResult[any_]',
    payloads:'strstrdict',
    search_texts:'strstrdict',
    ) -> 'strintdict':
    """ Inserts the given payloads, keyed by their digests, that the result of find_stored_payloads does not list,
    with the search texts of the given dict, keyed by the same digests, and with search texts extracted here
    for the payloads that dict has none for. Returns the id of the row of each payload by its digest.
    """
    digests = sorted(payloads)

    # The ids of the payloads stored already ..
    out:'strintdict' = {}

    for row in stored:
        out[row.digest] = row.id

    # .. the words of each payload not stored yet are extracted, unless they were extracted before the write ..
    rows:'dictlist' = []

    for digest in digests:
        if digest not in out:
            data = payloads[digest]

            if digest in search_texts:
                search_text = search_texts[digest]
            else:
                search_text = extract_search_text(data)

            rows.append({
                'digest': digest,
                'data': data,
                'search_text': search_text,
            })

    # .. they are inserted with multi-row statements, which return their ids, unless a concurrent transaction
    # inserted one of them first ..
    if rows:
        inserted = _payload_insert_statement.insert_rows(connection, rows)

        for row in inserted:
            out[row.digest] = row.id

        # .. in which case the payloads it inserted are read and locked like the ones stored already.
        concurrent_digests:'strlist' = []

        for digest in digests:
            if digest not in out:
                concurrent_digests.append(digest)

        if concurrent_digests:
            concurrent = _stored_payloads_statement.execute(connection, {'payload_digests': concurrent_digests})

            for row in concurrent:
                out[row.digest] = row.id

    return out

# ################################################################################################################################

def store_payload(connection:'Connection', data:'str') -> 'intnone':
    """ Stores one payload, unless it is stored already or empty, in the transaction of the connection,
    and returns the id of its row, or None for an empty payload.
    """
    if digest := get_payload_digest(data):
        payload_ids = store_payloads(connection, {digest: data}, {})
        out = payload_ids[digest]
    else:
        out = None

    return out

# ################################################################################################################################

def delete_unreferenced_payloads(connection:'Connection', payload_ids:'intlist') -> 'None':
    """ Deletes the payloads of the given ids that no event references, in the transaction of the connection.
    """
    if not payload_ids:
        return

    parameters = {'payload_ids': payload_ids}

    # The payloads are locked first, which waits for the writers that reference them to commit,
    # and the references are checked in a statement of its own, which sees what those writers committed ..
    _ = connection.execute(_deleted_payloads_query, parameters)

    # .. and the payloads that are referenced by no event are deleted.
    _ = connection.execute(_unreferenced_payloads_delete, parameters)

# ################################################################################################################################

def update_event_payload(connection:'Connection', event_id:'int', values:'anydict', data:'str') -> 'None':
    """ Updates the given columns of one event and replaces its payload, in the transaction of the connection,
    and deletes the payload it replaced if no other event references it.
    """

    # The payload the event has now ..
    previous_query = select(event_table.c.payload_id)
    previous_query = previous_query.where(event_table.c.id == event_id)

    previous_payload_id = connection.execute(previous_query).scalar()

    # .. is replaced with the new one ..
    payload_id = store_payload(connection, data)

    update_statement = event_table.update()
    update_statement = update_statement.where(event_table.c.id == event_id)
    update_statement = update_statement.values(payload_id=payload_id, **values)

    _ = connection.execute(update_statement)

    # .. and the previous one is deleted unless another event references it.
    if previous_payload_id:
        if previous_payload_id != payload_id:
            delete_unreferenced_payloads(connection, [previous_payload_id])

# ################################################################################################################################
# ################################################################################################################################
