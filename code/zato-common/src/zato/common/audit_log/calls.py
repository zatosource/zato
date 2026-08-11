# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# One helper every outgoing connection wrapper records its calls through - the same
# shape REST outgoing writes, so the alerting collectors read every instrumented
# source alike. A call that failed on credentials gets the auth-failed event type,
# because its remedy is different and alerting counts it separately.

from __future__ import annotations

# Zato
from zato.common.audit_log.common import AuditEvent, AuditOutcome
from zato.common.util.api import new_cid_server

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.audit_log.api import AuditLog
    AuditLog = AuditLog

# ################################################################################################################################
# ################################################################################################################################

def record_remote_call(
    audit_log:'AuditLog',
    source:'str',
    object_name:'str',
    *,
    cid:'str' = '',
    is_ok:'bool',
    is_auth_error:'bool' = False,
    duration_ms:'int' = 0,
    status:'str' = '',
    endpoint:'str' = '',
    ) -> 'None':
    """ Records one completed remote call of an outgoing connection - the completing
    event the usage and alerting queries look for, with the outcome and duration
    the collectors measure. Calls with no service context get a correlation id
    of their own.
    """

    # A wrapper-level call carries no service context, so the id is minted here
    if not cid:
        cid = new_cid_server()

    if is_ok:
        outcome = AuditOutcome.OK
    else:
        outcome = AuditOutcome.Error

    # A credentials failure is its own event type because its remedy is different
    if is_auth_error:
        event_type = AuditEvent.Auth_Failed
    else:
        event_type = AuditEvent.Response_Received

    _ = audit_log.insert(
        source,
        event_type,
        object_name,
        cid=cid,
        endpoint=endpoint,
        outcome=outcome,
        status=status,
        duration_ms=duration_ms,
    )

# ################################################################################################################################
# ################################################################################################################################
