# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The payloads of the audit log, each stored once in the payload table under the digest of its content,
# however many events carry it. An event references its payload by the digest, and a payload is deleted
# when the last event referencing it is deleted or pruned.
#
# On PostgreSQL, a writer locks the payload rows it references before it inserts the missing ones,
# and a deletion locks them for update before it checks for references in a statement of its own,
# so that a payload is never deleted while a transaction that has not committed yet references it.

from __future__ import annotations

# stdlib
from hashlib import blake2b

# SQLAlchemy
from sqlalchemy import bindparam, select
from sqlalchemy.dialects.postgresql import insert as postgresql_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

# Zato
from zato.common.audit_log.common import event_payload_table, event_table
from zato.common.db_env.common import Type_PostgreSQL, Type_SQLite

# Zato - Rust
from zato_common_core.zato_common_core import extract_search_text

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Connection
    from zato.common.audit_log.pending import pending_event_list
    from zato.common.typing_ import anydict, dictlist, strlist, strnone, strstrdict

    # Dummy assignments to satisfy type checkers
    anydict = anydict
    Connection = Connection
    pending_event_list = pending_event_list
    dictlist = dictlist
    strstrdict = strstrdict
    strlist = strlist
    strnone = strnone

# ################################################################################################################################
# ################################################################################################################################

# How many bytes a digest of a payload has
_digest_size = 16

# The insert of each database, which skips a payload that is stored already
_payload_inserts:'anydict' = {}

for _dialect_name, _insert in ((Type_SQLite, sqlite_insert), (Type_PostgreSQL, postgresql_insert)):
    _payload_insert = _insert(event_payload_table).on_conflict_do_nothing(index_elements=[event_payload_table.c.digest])
    _payload_inserts[_dialect_name] = _payload_insert

# The payloads of the given digests that are stored already, locked on PostgreSQL against a concurrent deletion.
# Every transaction locks payloads in the order of their digests, so that no two of them wait for each other.
_stored_payloads_query = select(event_payload_table.c.digest)
_stored_payloads_query = _stored_payloads_query.where(
    event_payload_table.c.digest.in_(bindparam('payload_digests', expanding=True)))
_stored_payloads_query = _stored_payloads_query.order_by(event_payload_table.c.digest)
_stored_payloads_query = _stored_payloads_query.with_for_update(read=True, key_share=True)

# The payloads of the given digests, locked against a concurrent reference, in the same order
_deleted_payloads_query = select(event_payload_table.c.digest)
_deleted_payloads_query = _deleted_payloads_query.where(
    event_payload_table.c.digest.in_(bindparam('payload_digests', expanding=True)))
_deleted_payloads_query = _deleted_payloads_query.order_by(event_payload_table.c.digest)
_deleted_payloads_query = _deleted_payloads_query.with_for_update()

# The deletion of the payloads of the given digests that no event references
_is_referenced = select(event_table.c.id)
_is_referenced = _is_referenced.where(event_table.c.payload_digest == event_payload_table.c.digest)
_is_referenced = _is_referenced.exists()

_unreferenced_payloads_delete = event_payload_table.delete()
_unreferenced_payloads_delete = _unreferenced_payloads_delete.where(
    event_payload_table.c.digest.in_(bindparam('payload_digests', expanding=True)))
_unreferenced_payloads_delete = _unreferenced_payloads_delete.where(~_is_referenced)

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

def get_event_rows(batch:'pending_event_list', payloads:'strstrdict') -> 'dictlist':
    """ Returns the rows of the event table of a batch of events, which reference their payloads by digest,
    and adds each payload to the given dict under its digest.
    """
    out:'dictlist' = []

    for pending in batch:

        event_row = dict(pending.values)
        data = event_row.pop('data')

        if digest := event_row['payload_digest']:
            payloads[digest] = data

        out.append(event_row)

    return out

# ################################################################################################################################

def store_payloads(connection:'Connection', payloads:'strstrdict') -> 'None':
    """ Stores the given payloads, keyed by their digests, that are not stored yet, in the transaction of the connection.
    """
    digests = sorted(payloads)

    # The payloads stored already are found first, and on PostgreSQL they are locked,
    # so that no deletion removes them before this transaction commits the events that reference them ..
    result = connection.execute(_stored_payloads_query, {'payload_digests': digests})
    stored_digests = set(result.scalars())

    # .. the words of each of the other ones are extracted ..
    rows:'dictlist' = []

    for digest in digests:
        if digest not in stored_digests:
            data = payloads[digest]
            rows.append({
                'digest': digest,
                'data': data,
                'search_text': extract_search_text(data),
            })

    # .. and they are inserted, unless a concurrent transaction on PostgreSQL inserted one of them first.
    if rows:
        insert_statement = _payload_inserts[connection.dialect.name]
        _ = connection.execute(insert_statement, rows)

# ################################################################################################################################

def store_payload(connection:'Connection', data:'str') -> 'strnone':
    """ Stores one payload, unless it is stored already or empty, in the transaction of the connection,
    and returns the digest it is stored under, or None for an empty payload.
    """
    out = get_payload_digest(data)

    if out:
        store_payloads(connection, {out: data})

    return out

# ################################################################################################################################

def delete_unreferenced_payloads(connection:'Connection', digests:'strlist') -> 'None':
    """ Deletes the payloads of the given digests that no event references, in the transaction of the connection.
    """
    if not digests:
        return

    parameters = {'payload_digests': digests}

    # On PostgreSQL, the payloads are locked first, which waits for the writers that reference them to commit,
    # and the references are checked in a statement of its own, which sees what those writers committed ..
    if connection.dialect.name == Type_PostgreSQL:
        _ = connection.execute(_deleted_payloads_query, parameters)

    # .. and the payloads that are referenced by no event are deleted.
    _ = connection.execute(_unreferenced_payloads_delete, parameters)

# ################################################################################################################################

def update_event_payload(connection:'Connection', event_id:'int', values:'anydict', data:'str') -> 'None':
    """ Updates the given columns of one event and replaces its payload, in the transaction of the connection,
    and deletes the payload it replaced if no other event references it.
    """

    # The payload the event carries now ..
    previous_query = select(event_table.c.payload_digest)
    previous_query = previous_query.where(event_table.c.id == event_id)

    previous_digest = connection.execute(previous_query).scalar()

    # .. is replaced with the new one ..
    payload_digest = store_payload(connection, data)

    update_statement = event_table.update()
    update_statement = update_statement.where(event_table.c.id == event_id)
    update_statement = update_statement.values(payload_digest=payload_digest, **values)

    _ = connection.execute(update_statement)

    # .. and the previous one is deleted unless another event references it.
    if previous_digest:
        if previous_digest != payload_digest:
            delete_unreferenced_payloads(connection, [previous_digest])

# ################################################################################################################################
# ################################################################################################################################
