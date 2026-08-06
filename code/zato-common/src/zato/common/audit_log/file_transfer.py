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
from json import dumps

# Zato
from zato.common.audit_log.api import AuditEvent, AuditSource
from zato.common.audit_log.attachment import build_attachment

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.audit_log.api import AuditLog
    from zato.common.typing_ import bytesnone, intnone, stranydict
    AuditLog = AuditLog
    bytesnone = bytesnone
    intnone = intnone
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

# The operations one file transfer event describes.
Operation_Store  = 'store'
Operation_Delete = 'delete'

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

    # A failed operation says what went wrong right in its data
    if error:
        summary['error'] = error

    # The operation and its duration are searchable attributes -
    # "every delete on this share" and "the slowest transfers" are one query each.
    attrs = {
        'operation': operation,
        'duration_ms': duration_ms,
    }

    insert_options:'stranydict' = {
        'cid': cid,
        'endpoint': remote_path,
        'size': size,
        'outcome': outcome,
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
# ################################################################################################################################
