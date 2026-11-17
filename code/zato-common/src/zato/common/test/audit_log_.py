# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The audit log of the tests that build the components of a server without the server itself, which records
# their operations in the same transactions as a server does.

# Zato
from zato.common.audit_log.api import AuditLog

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The server that the audit events of the tests name
    Server_Name = 'test-server'

# ################################################################################################################################
# ################################################################################################################################

def new_test_audit_log() -> 'AuditLog':
    """ Returns an audit log whose events name the server of the tests.
    """
    out = AuditLog(ModuleCtx.Server_Name)
    return out

# ################################################################################################################################
# ################################################################################################################################
