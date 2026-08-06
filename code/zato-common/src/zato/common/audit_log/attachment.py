# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from base64 import b64decode, b64encode
from json import dumps, loads

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.common.audit_log.common import event_body_table, AuditBody

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Engine
    from zato.common.typing_ import anydictnone, anylist, stranydict

    # Dummy assignments to satisfy type checkers
    anydictnone = anydictnone
    anylist = anylist
    Engine = Engine
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

# The environment variable overriding how big one attachment may be for its bytes to be kept
Env_Max_Attachment_Size = 'Zato_Audit_Log_Max_Attachment_Size'

# How big one attachment may be for its bytes to be kept when the environment does not say otherwise
_default_max_attachment_size = 10 * 1024 * 1024

# ################################################################################################################################

def get_max_attachment_size() -> 'int':
    """ Returns how big one attachment may be, in bytes, for its content to be stored.
    """
    if value := os.environ.get(Env_Max_Attachment_Size, ''):
        out = int(value)
    else:
        out = _default_max_attachment_size

    return out

# ################################################################################################################################

def build_attachment(filename:'str', content_type:'str', content:'bytes') -> 'stranydict':
    """ Builds one attachment envelope out of a file's name, type and bytes.
    An attachment bigger than the cap keeps its metadata and loses its bytes,
    saying so through the is_content_kept flag.
    """
    size = len(content)
    max_size = get_max_attachment_size()

    out:'stranydict' = {
        'filename': filename,
        'content_type': content_type,
        'size': size,
        'is_content_kept': size <= max_size,
        'content': '',
    }

    if out['is_content_kept']:
        out['content'] = b64encode(content).decode('ascii')

    return out

# ################################################################################################################################

def build_attachment_rows(event_id:'int', event_time_iso:'str', attachments:'anylist') -> 'anylist':
    """ Turns attachment envelopes into event_body rows - one row per attachment,
    stamped with the event's own time so pruning never needs a join.
    """
    out:'anylist' = []

    for attachment in attachments:
        out.append({
            'event_id': event_id,
            'kind': AuditBody.Attachment,
            'event_time_iso': event_time_iso,
            'data': dumps(attachment),
        })

    return out

# ################################################################################################################################

def list_attachments(engine:'Engine', event_id:'int') -> 'anylist':
    """ Returns the attachments of one event as metadata only - the id of each body row
    along with the filename, type, size and whether the bytes were kept, never the bytes.
    """
    query = select(event_body_table.c.id, event_body_table.c.data)
    query = query.where(event_body_table.c.event_id == event_id)
    query = query.where(event_body_table.c.kind == AuditBody.Attachment)
    query = query.order_by(event_body_table.c.id)

    out:'anylist' = []

    with engine.connect() as connection:
        for row in connection.execute(query):

            envelope = loads(row[1])

            out.append({
                'id': row[0],
                'filename': envelope['filename'],
                'content_type': envelope['content_type'],
                'size': envelope['size'],
                'is_content_kept': envelope['is_content_kept'],
            })

    return out

# ################################################################################################################################

def get_attachment(engine:'Engine', body_row_id:'int') -> 'anydictnone':
    """ Returns one attachment by its body-row id, its bytes decoded, or None
    when there is no such row or the row is not an attachment. The id of the event
    the attachment belongs to comes along, so access to it can be recorded
    against that event.
    """
    query = select(event_body_table.c.data, event_body_table.c.event_id)
    query = query.where(event_body_table.c.id == body_row_id)
    query = query.where(event_body_table.c.kind == AuditBody.Attachment)

    with engine.connect() as connection:
        result = connection.execute(query)
        row = result.first()

    if not row:
        return None

    envelope = loads(row[0])

    out:'stranydict' = {
        'event_id': row[1],
        'filename': envelope['filename'],
        'content_type': envelope['content_type'],
        'size': envelope['size'],
        'is_content_kept': envelope['is_content_kept'],
        'content': b64decode(envelope['content']),
    }

    return out

# ################################################################################################################################
# ################################################################################################################################
