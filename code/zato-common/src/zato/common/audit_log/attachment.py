# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from json import dumps, loads

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.common.audit_log.common import event_body_table, AuditBody

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from sqlalchemy.engine import Engine
    from zato.common.typing_ import anydictnone, anylist, intnone, stranydict

    # Dummy assignments to satisfy type checkers
    anydictnone = anydictnone
    anylist = anylist
    datetime = datetime
    Engine = Engine
    intnone = intnone
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

# The environment variable overriding how big one attachment may be for its bytes to be kept
Env_Max_Attachment_Size = 'Zato_Audit_Log_Max_Attachment_Size'

# How big one attachment may be for its bytes to be kept when the environment does not say otherwise
_default_max_attachment_size = 50 * 1024 * 1024

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

def _new_envelope(filename:'str', content_type:'str', size:'int', max_size:'int') -> 'stranydict':
    """ Builds the metadata of one attachment envelope, saying whether a file of this size keeps its bytes.
    """
    out:'stranydict' = {
        'filename': filename,
        'content_type': content_type,
        'size': size,
        'is_content_kept': size <= max_size,
        'content': b'',
    }

    return out

# ################################################################################################################################

def build_attachment(filename:'str', content_type:'str', content:'bytes', *, max_size:'intnone'=None) -> 'stranydict':
    """ Builds one attachment envelope out of a file's name, type and bytes.
    An attachment bigger than the cap keeps its metadata and loses its bytes,
    saying so through the is_content_kept flag. A caller with a cap of its own gives it in max_size.
    """
    size = len(content)

    if max_size is None:
        max_size = get_max_attachment_size()

    out = _new_envelope(filename, content_type, size, max_size)

    if out['is_content_kept']:
        out['content'] = content

    return out

# ################################################################################################################################

def build_attachment_from_file(filename:'str', content_type:'str', path:'str', size:'int') -> 'stranydict':
    """ Builds one attachment envelope out of a local file - its bytes are read only when they fit under the cap.
    """
    max_size = get_max_attachment_size()
    out = _new_envelope(filename, content_type, size, max_size)

    if out['is_content_kept']:

        with open(path, 'rb') as local_file:
            out['content'] = local_file.read()

    return out

# ################################################################################################################################

def build_attachment_rows(event_id:'int', event_time:'datetime', attachments:'anylist') -> 'anylist':
    """ Turns attachment envelopes into event_body rows - one row per attachment, with the metadata in data
    and the bytes in content, stamped with the event's own time so pruning never needs a join.
    """
    out:'anylist' = []

    for attachment in attachments:

        metadata = {
            'filename': attachment['filename'],
            'content_type': attachment['content_type'],
            'size': attachment['size'],
            'is_content_kept': attachment['is_content_kept'],
        }

        # An attachment whose bytes were not kept has no content at all
        if attachment['is_content_kept']:
            content = attachment['content']
        else:
            content = None

        out.append({
            'event_id': event_id,
            'kind': AuditBody.Attachment,
            'event_time': event_time,
            'data': dumps(metadata),
            'content': content,
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

            metadata = loads(row[1])

            out.append({
                'id': row[0],
                'filename': metadata['filename'],
                'content_type': metadata['content_type'],
                'size': metadata['size'],
                'is_content_kept': metadata['is_content_kept'],
            })

    return out

# ################################################################################################################################

def get_attachment(engine:'Engine', body_row_id:'int') -> 'anydictnone':
    """ Returns one attachment by its body-row id, with its bytes, or None
    when there is no such row or the row is not an attachment. The id of the event
    the attachment belongs to comes along, so access to it can be recorded
    against that event.
    """
    query = select(event_body_table.c.data, event_body_table.c.content, event_body_table.c.event_id)
    query = query.where(event_body_table.c.id == body_row_id)
    query = query.where(event_body_table.c.kind == AuditBody.Attachment)

    with engine.connect() as connection:
        result = connection.execute(query)
        row = result.first()

    if not row:
        return None

    metadata = loads(row.data)

    # An attachment whose bytes were not kept has no content at all
    if metadata['is_content_kept']:
        content = row.content
    else:
        content = b''

    out:'stranydict' = {
        'event_id': row.event_id,
        'filename': metadata['filename'],
        'content_type': metadata['content_type'],
        'size': metadata['size'],
        'is_content_kept': metadata['is_content_kept'],
        'content': content,
    }

    return out

# ################################################################################################################################
# ################################################################################################################################
