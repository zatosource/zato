# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The dedup records of the message IDs of publications. A publication writes the dedup record of its message ID
# before its message, so its ID is recognized as a repeat for the window of the dedup record,
# whether or not the message itself is still retained.

# stdlib
from logging import getLogger

# SQLAlchemy
from sqlalchemy import and_, BigInteger, bindparam, cast, exists, literal_column, null, select, String, union_all

# Zato
from zato.common.common_db.message_dedup import dedup_records_query, dedup_upsert, Kind, new_dedup_record
from zato.common.common_db.schema import message_dedup_table
from zato.common.db_env.any_of import any_of
from zato.common.db_env.plain_sql import PlainStatement
from zato.common.pubsub.sql.errors import PubSubDuplicateMsgID
from zato.common.pubsub.sql.payloads import get_chunks
from zato.common.pubsub.sql.schema import message_table

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Connection
    from zato.common.pubsub.sql.pending import pending_publication_list
    from zato.common.typing_ import any_, anydict, anylist, strlist

    # Dummy assignments to satisfy type checkers
    any_ = any_
    anydict = anydict
    anylist = anylist
    Connection = Connection
    pending_publication_list = pending_publication_list
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# The message IDs of publications are unique across all the topics.
Dedup_Scope = ''

# What separates the topic name from the checksum of the payload in a fingerprint. The checksum consists of digits only,
# so the last separator of a fingerprint always ends its topic name.
_fingerprint_separator = ':'

# ################################################################################################################################

# The fingerprint of a stored message, built in SQL exactly as get_fingerprint builds it in Python.
message_fingerprint = message_table.c.topic_name.concat(literal_column(f"'{_fingerprint_separator}'"))
message_fingerprint = message_fingerprint.concat(cast(message_table.c.payload_crc32, String))

# ################################################################################################################################

def new_fingerprint_rewrite(message_id_condition:'any_') -> 'any_':
    """ Returns the update that gives the dedup records of the matching message IDs the fingerprints of their stored messages.
    """
    is_message = message_table.c.msg_id == message_dedup_table.c.message_id

    stored_fingerprint = select(message_fingerprint).where(is_message).scalar_subquery()
    has_message = exists().where(is_message)

    out = message_dedup_table.update()
    out = out.where(and_(
        message_dedup_table.c.kind == bindparam('dedup_kind'),
        message_dedup_table.c.scope == bindparam('dedup_scope'),
        message_id_condition,
        has_message,
    ))
    out = out.values(fingerprint=stored_fingerprint)

    return out

# ################################################################################################################################

# The rewrite of the fingerprints of the dedup records of given message IDs.
_fingerprint_rewrite = PlainStatement(new_fingerprint_rewrite(
    any_of(message_dedup_table.c.message_id, 'dedup_message_ids')))

# The fingerprints that given message IDs stand for, read in one statement - those of their stored messages ..
_source_message = 'message'
_source_dedup   = 'dedup'

_message_fingerprints_select = select(
    literal_column(f"'{_source_message}'").label('source'),
    message_table.c.msg_id.label('msg_id'),
    message_fingerprint.label('fingerprint'),
    cast(null(), BigInteger).label('expires_ms'),
)
_message_fingerprints_select = _message_fingerprints_select.where(any_of(message_table.c.msg_id, 'write_msg_ids'))

# .. and those of their dedup records, with the time when each record expires.
_dedup_fingerprints_select = select(
    literal_column(f"'{_source_dedup}'"),
    message_dedup_table.c.message_id,
    message_dedup_table.c.fingerprint,
    message_dedup_table.c.expires_ms,
)
_dedup_fingerprints_select = _dedup_fingerprints_select.where(and_(
    message_dedup_table.c.kind == bindparam('dedup_kind'),
    message_dedup_table.c.scope == bindparam('dedup_scope'),
    any_of(message_dedup_table.c.message_id, 'dedup_message_ids'),
))

_existing_fingerprints_query = PlainStatement(union_all(_message_fingerprints_select, _dedup_fingerprints_select))

# ################################################################################################################################
# ################################################################################################################################

def get_fingerprint(topic_name:'str', payload_crc32:'int') -> 'str':
    """ Returns the fingerprint of a publication, which tells a repeated publication from a different message.
    """
    out = f'{topic_name}{_fingerprint_separator}{payload_crc32}'
    return out

# ################################################################################################################################

def _get_msg_ids(publications:'pending_publication_list') -> 'strlist':
    """ Returns the message IDs of the publications, each once, in the order of the publications.
    """
    out:'strlist' = []
    seen:'set[str]' = set()

    for pending in publications:
        msg_id = pending.message_values['msg_id']
        if msg_id not in seen:
            seen.add(msg_id)
            out.append(msg_id)

    return out

# ################################################################################################################################

def _get_dedup_records(connection:'Connection', msg_ids:'strlist') -> 'anydict':
    """ Returns the fingerprint and the expiration time of each dedup record of the given message IDs, by message ID.
    """
    out:'anydict' = {}

    for chunk in get_chunks(msg_ids):
        parameters = {'dedup_kind': Kind.Pubsub, 'dedup_scope': Dedup_Scope, 'dedup_message_ids': chunk}
        for row in dedup_records_query.execute(connection, parameters):
            out[row.message_id] = (row.fingerprint, row.expires_ms)

    return out

# ################################################################################################################################

def write_dedup_records(connection:'Connection', publications:'pending_publication_list') -> 'pending_publication_list':
    """ Writes the dedup record of each message ID of the publications in the caller's transaction and returns
    the publications whose dedup records were written, which go on to insert their messages. Each other publication
    is a repeat if its fingerprint matches that of the dedup record that remains and fails with PubSubDuplicateMsgID otherwise.
    """
    # The first publication of a message ID within a commit provides its dedup record ..
    records:'anydict' = {}

    for pending in publications:
        msg_id = pending.message_values['msg_id']
        if msg_id not in records:
            records[msg_id] = new_dedup_record(
                Kind.Pubsub, Dedup_Scope, msg_id, pending.fingerprint, pending.received_ms, pending.dedup_expires_ms)

    # .. the dedup records are written in the order of their keys, so that concurrent commits with the same message IDs
    # .. lock the records in one order and do not deadlock ..
    rows:'anylist' = []

    for msg_id in sorted(records):
        rows.append(records[msg_id])

    written:'set[str]' = set()

    for row in dedup_upsert.insert_rows(connection, rows):
        written.add(row.message_id)

    # .. a dedup record that was not written remains from an earlier publication ..
    remaining:'strlist' = []

    for msg_id in records:
        if msg_id not in written:
            remaining.append(msg_id)

    existing = _get_dedup_records(connection, remaining)

    out:'pending_publication_list' = []

    for pending in publications:

        msg_id = pending.message_values['msg_id']

        # .. each publication whose dedup record was written inserts its message,
        # .. including later ones of the same ID within this commit, which the insert of the message resolves ..
        if msg_id in written:
            out.append(pending)
            continue

        pending.subscriber_keys = []

        # .. a dedup record that expired and was swept after the upsert met it was one of a repeated message ..
        if msg_id not in existing:
            logger.info('Repeated publication of a swept dedup record -> msg_id:%s', msg_id)
            pending.is_repeat = True
            continue

        # .. and otherwise the fingerprint tells a repeat from a different message.
        fingerprint, _ = existing[msg_id]

        if fingerprint == pending.fingerprint:
            logger.info('Repeated publication within the dedup window -> msg_id:%s', msg_id)
            pending.is_repeat = True
        else:
            message = f'Message ID `{msg_id}` belongs to a different message received within the dedup window'
            pending.exception = PubSubDuplicateMsgID(message)

    return out

# ################################################################################################################################

def rewrite_fingerprints(connection:'Connection', duplicates:'pending_publication_list') -> 'None':
    """ Gives the dedup records of publications whose messages met stored messages with the same IDs the fingerprints
    of the stored messages, so that a dedup record and the message of its ID never disagree.
    """
    msg_ids = _get_msg_ids(duplicates)

    for chunk in get_chunks(msg_ids):
        parameters = {'dedup_kind': Kind.Pubsub, 'dedup_scope': Dedup_Scope, 'dedup_message_ids': chunk}
        _ = _fingerprint_rewrite.execute(connection, parameters)

# ################################################################################################################################

def get_existing_fingerprints(connection:'Connection', publications:'pending_publication_list') -> 'anydict':
    """ Returns the fingerprint that each message ID of the publications stands for already, by message ID,
    from its dedup record within its window, or otherwise from its stored message. An ID that stands for nothing is absent.
    """
    msg_ids = _get_msg_ids(publications)

    out:'anydict' = {}
    records:'anydict' = {}

    for chunk in get_chunks(msg_ids):
        parameters = {
            'write_msg_ids': chunk,
            'dedup_kind': Kind.Pubsub,
            'dedup_scope': Dedup_Scope,
            'dedup_message_ids': chunk,
        }

        for row in _existing_fingerprints_query.execute(connection, parameters):
            if row.source == _source_message:
                out[row.msg_id] = row.fingerprint
            else:
                records[row.msg_id] = (row.fingerprint, row.expires_ms)

    # A dedup record that expired by the time of the publication is replaced by it, so it stands for nothing.
    for pending in publications:
        msg_id = pending.message_values['msg_id']
        if msg_id in records:
            fingerprint, expires_ms = records[msg_id]
            if expires_ms > pending.received_ms:
                out[msg_id] = fingerprint

    return out

# ################################################################################################################################
# ################################################################################################################################
