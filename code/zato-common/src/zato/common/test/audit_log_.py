# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The audit log of the tests that build the components of a server without the server itself, which records
# their operations in the same transactions as a server does.

# stdlib
from typing import NamedTuple

# Zato
from zato.common.audit_log.api import AuditLog
from zato.common.audit_log.export.api import AuditExport

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.audit_log.pending import pending_event_list
    from zato.common.typing_ import stranydict

    # Dummy assignments to satisfy type checkers
    pending_event_list = pending_event_list
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The server that the audit events of the tests name
    Server_Name = 'test-server'

# ################################################################################################################################
# ################################################################################################################################

class ExportedEvent(NamedTuple):
    """ One event as the export received it after its commit.
    """
    event_id: int
    values: 'stranydict'
    is_export_payload_active: bool

# Type aliases
exported_event_list = list[ExportedEvent]

# ################################################################################################################################
# ################################################################################################################################

class RecordingAuditExport(AuditExport):
    """ An export that records the events of each batch handed to it after a commit and sends nothing.
    """
    def __init__(self) -> 'None':
        self.events:'exported_event_list' = []

    def emit_batch(self, batch:'pending_event_list') -> 'None':
        for pending in batch:
            values = dict(pending.values)
            event = ExportedEvent(pending.event_id, values, pending.is_export_payload_active)
            self.events.append(event)

# ################################################################################################################################
# ################################################################################################################################

def new_test_audit_log() -> 'AuditLog':
    """ Returns an audit log whose events name the server of the tests.
    """
    out = AuditLog(ModuleCtx.Server_Name)
    return out

# ################################################################################################################################
# ################################################################################################################################
