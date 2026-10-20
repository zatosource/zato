# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from hashlib import sha256

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.common.audit_log.api import event_table, get_audit_engine
from zato.common.audit_log.attachment import get_attachment, list_attachments
from zato.common.file_transfer.spool import Chunk_Size

# ################################################################################################################################
# ################################################################################################################################

# How many bytes a large test file has - several chunks and a part of one more
Large_File_Size = Chunk_Size * 3 + 123

# ################################################################################################################################
# ################################################################################################################################

def new_large_file(directory:'str', file_name:'str') -> 'bytes':
    """ Writes a file of random bytes, several chunks long, and returns its bytes.
    """
    out = os.urandom(Large_File_Size)
    path = os.path.join(directory, file_name)

    with open(path, 'wb') as large_file:
        _ = large_file.write(out)

    return out

# ################################################################################################################################

def checksum_of_path(path:'str') -> 'str':
    """ The SHA-256 checksum of a local file.
    """
    with open(path, 'rb') as local_file:
        data = local_file.read()

    hasher = sha256(data)
    out = hasher.hexdigest()

    return out

# ################################################################################################################################

def get_kept_content(remote_path:'str') -> 'bytes':
    """ The bytes the audit log kept for the latest operation on a remote path.
    """
    engine = get_audit_engine()

    query = select(event_table.c.id)
    query = query.where(event_table.c.endpoint == remote_path)
    query = query.order_by(event_table.c.id.desc())
    query = query.limit(1)

    with engine.connect() as connection:
        event_id = connection.execute(query).scalar_one()

    items = list_attachments(engine, event_id)
    attachment_id = items[0]['id']

    attachment = get_attachment(engine, attachment_id)
    out = attachment['content']

    return out

# ################################################################################################################################
# ################################################################################################################################
