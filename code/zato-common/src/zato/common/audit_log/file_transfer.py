# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The one write every outgoing file transfer goes through - a file handed to an SMB share,
# an FTP server or an SFTP one leaves one request-sent event saying which connection moved
# which remote path, how big it was, how long it took and how it ended. The file's bytes
# are not stored unless the connection asks for that, and then they travel as an attachment
# envelope under the same size cap every attachment observes, so the file can be reread
# and downloaded from the audit log the way any attachment can.

from __future__ import annotations

# stdlib
from base64 import b64decode
from json import dumps, loads

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.common.audit_log.api import event_body_table, event_table, get_audit_engine, AuditEvent, AuditSource
from zato.common.audit_log.attachment import build_attachment
from zato.common.audit_log.common import AuditBody
from zato.common.audit_log.resubmit import ResubmitException

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.audit_log.api import AuditLog
    from zato.common.typing_ import bytesnone, intlistnone, intnone, stranydict, strdictnone
    AuditLog = AuditLog
    bytesnone = bytesnone
    intlistnone = intlistnone
    intnone = intnone
    stranydict = stranydict
    strdictnone = strdictnone

# ################################################################################################################################
# ################################################################################################################################

# The operations one file transfer event describes.
Operation_Store  = 'store'
Operation_Read   = 'read'
Operation_Delete = 'delete'
Operation_Move   = 'move'

# What a stored file is served back as when nothing better is known about it
_default_content_type = 'application/octet-stream'

# ################################################################################################################################
# ################################################################################################################################

def record_file_transfer(
    audit_log:'AuditLog',
    conn_name:'str',
    operation:'str',
    remote_path:'str',
    *,
    cid:'str',
    outcome:'str',
    size:'int' = 0,
    duration_ms:'int' = 0,
    error:'str' = '',
    to_path:'str' = '',
    checksum:'str' = '',
    content:'bytesnone' = None,
    ) -> 'intnone':
    """ Writes one audit event describing an outgoing file operation. The content is stored
    only when given, as an attachment envelope under the shared size cap - which is what
    the per-connection body storage flag hands over when it is on. Returns the event id.
    """

    # What happened is readable off the event without opening anything else
    summary = {
        'operation': operation,
        'remote_path': remote_path,
        'size': size,
    }

    # A move says where the file went
    if to_path:
        summary['to_path'] = to_path

    # A failed operation says what went wrong right in its data
    if error:
        summary['error'] = error

    # The operation and its duration are searchable attributes -
    # "every delete on this share" and "the slowest transfers" are one query each.
    attrs = {
        'operation': operation,
        'duration_ms': duration_ms,
    }

    # The checksum is stored when the caller computed one off the bytes
    if checksum:
        attrs['checksum'] = checksum

    insert_options:'stranydict' = {
        'cid': cid,
        'endpoint': remote_path,
        'size': size,
        'outcome': outcome,
        'duration_ms': duration_ms,
        'data': dumps(summary),
        'attrs': attrs,
    }

    # The file's bytes travel as an attachment when the connection asked for them to be kept -
    # the envelope caps oversized files on its own, keeping their metadata.
    if content is not None:
        filename = remote_path.rstrip('/').split('/')[-1]
        insert_options['attachments'] = [build_attachment(filename, _default_content_type, content)]

    # Our response to produce
    out = audit_log.insert(AuditSource.File_Outgoing, AuditEvent.Request_Sent, conn_name, **insert_options)

    return out

# ################################################################################################################################

def record_schedule_event(
    audit_log:'AuditLog',
    conn_name:'str',
    event_type:'str',
    remote_path:'str',
    *,
    cid:'str',
    correl_id:'str',
    schedule:'str',
    outcome:'str',
    file_name:'str' = '',
    service:'str' = '',
    size:'int' = 0,
    error:'str' = '',
    extra:'strdictnone' = None,
    parents:'intlistnone' = None,
    ) -> 'intnone':
    """ Writes one audit event of a file transfer schedule - a file claimed, handed to its
    target service, moved or deleted afterwards, or a whole run summarized. The cid is the file's
    own and the correlation id is the run's, so one query shows either the file or the run.
    Returns the event id.
    """

    # What happened is readable off the event without opening anything else
    summary:'stranydict' = {
        'schedule': schedule,
        'remote_path': remote_path,
    }

    if file_name:
        summary['file_name'] = file_name

    if service:
        summary['service'] = service

    # A failed step says what went wrong right in its data
    if error:
        summary['error'] = error

    # Whatever else this kind of event has to say, e.g. where a file was moved
    # or how many files a run took.
    if extra:
        summary.update(extra)

    # The schedule and the file are searchable attributes - "everything schedule X did"
    # and "every event of file Y" are one query each.
    attrs:'stranydict' = {
        'schedule': schedule,
    }

    if file_name:
        attrs['file_name'] = file_name

    if service:
        attrs['service'] = service

    insert_options:'stranydict' = {
        'cid': cid,
        'correl_id': correl_id,
        'endpoint': remote_path,
        'size': size,
        'outcome': outcome,
        'data': dumps(summary),
        'attrs': attrs,
    }

    # A reprocessed event names the event it repeats
    if parents:
        insert_options['parents'] = parents

    # Our response to produce
    out = audit_log.insert(AuditSource.File_Outgoing, event_type, conn_name, **insert_options)

    return out

# ################################################################################################################################

def load_transfer_content(cid:'str') -> 'bytes':
    """ Returns the bytes the read event of one file transfer stored - what a reprocess
    hands to the target service again. When the read event stored no content,
    a ResubmitException is raised.
    """

    # Every file operation recorded under this cid, oldest first - the read is among them
    # when the connection keeps file contents.
    statement = select(
        event_table.c.id,
        event_table.c.data,
    ).where(event_table.c.cid == cid
    ).where(event_table.c.source == AuditSource.File_Outgoing
    ).where(event_table.c.event_type == AuditEvent.Request_Sent
    ).order_by(event_table.c.id)

    engine = get_audit_engine()

    with engine.connect() as connection:
        rows = connection.execute(statement).fetchall()

    # Find the read event - the operation is named in each event's data
    for row in rows:
        details = loads(row[1])
        if details['operation'] == Operation_Read:
            read_event_id = row[0]
            break
    else:
        raise ResubmitException(f'Cid `{cid}` has no read event to take the file from')

    # The bytes travel as the read event's attachment
    body_statement = select(event_body_table.c.data
    ).where(event_body_table.c.event_id == read_event_id
    ).where(event_body_table.c.kind == AuditBody.Attachment)

    with engine.connect() as connection:
        body_result = connection.execute(body_statement)
        body_row = body_result.first()

    if body_row is None:
        error_message = f'Cid `{cid}` stored no file content - turn on content storage on the connection to make files reprocessable'
        raise ResubmitException(error_message)

    envelope = loads(body_row[0])

    # An attachment over the size cap keeps its metadata but not its bytes
    if not envelope['is_content_kept']:
        raise ResubmitException(f'Cid `{cid}` stored no file content - the file was over the attachment size cap')

    out = b64decode(envelope['content'])

    return out

# ################################################################################################################################
# ################################################################################################################################
