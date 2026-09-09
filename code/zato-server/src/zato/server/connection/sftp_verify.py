# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from functools import partial
from time import monotonic

# Zato
from zato.common.audit_log.api import AuditEvent, AuditOutcome
from zato.common.audit_log.file_transfer import Operation_Store, Status_Verified, Status_Verify_Failed
from zato.server.connection.file_transfer_verify import verify_store, FileTransferVerifyError

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    from zato.server.connection.sftp import SFTPConnection
    SFTPConnection = SFTPConnection

# ################################################################################################################################
# ################################################################################################################################

# Milliseconds per second.
_ms_per_second = 1000

# ################################################################################################################################
# ################################################################################################################################

def _elapsed_ms(start:'float') -> 'int':
    elapsed = monotonic() - start
    out = int(elapsed * _ms_per_second)
    return out

# ################################################################################################################################

def _get_remote_size(conn:'SFTPConnection', remote_path:'str') -> 'int':
    info = conn.get_info(remote_path)
    out = info.size
    return out

# ################################################################################################################################

def record_sftp_store(
    conn:'SFTPConnection',
    remote_path:'str',
    size:'int',
    checksum:'str',
    content:'any_',
    start:'float',
    ) -> 'None':
    """ Verifies an uploaded file and records the store, raising FileTransferVerifyError on a mismatch.
    A directory has no checksum and is recorded without verification.
    """
    if not checksum:
        duration_ms = _elapsed_ms(start)
        conn._record_transfer(Operation_Store, remote_path, outcome=AuditOutcome.OK, size=size, duration_ms=duration_ms)
        return

    # The stored file is verified ..
    get_remote_size = partial(_get_remote_size, conn)
    verify_start = monotonic()
    verification = verify_store(get_remote_size, conn.read, remote_path, size, checksum, conn.wrapper.verify_how)
    verification['verify_ms'] = _elapsed_ms(verify_start)

    duration_ms = _elapsed_ms(start)

    # .. a mismatch is recorded on the store's row and as a Verify_Failed event ..
    if mismatch := verification['mismatch']:
        conn._record_transfer(Operation_Store, remote_path,
            outcome=AuditOutcome.Error, size=size, duration_ms=duration_ms, checksum=checksum, content=content,
            status=Status_Verify_Failed, error=mismatch, extra=verification)
        conn._record_transfer(Operation_Store, remote_path,
            outcome=AuditOutcome.Error, size=size, checksum=checksum, error=mismatch, extra=verification,
            event_type=AuditEvent.Verify_Failed)
        raise FileTransferVerifyError(mismatch)

    # .. and a match is recorded on the store's row.
    conn._record_transfer(Operation_Store, remote_path,
        outcome=AuditOutcome.OK, size=size, duration_ms=duration_ms, checksum=checksum, content=content,
        status=Status_Verified, extra=verification)

# ################################################################################################################################
# ################################################################################################################################
