# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The one write every audited SQL statement goes through - an outgoing SQL connection
# that opted in leaves one request-sent event per statement, saying which connection
# ran what against which database, how long it took and how it ended. How much of
# the statement travels with the event is the connection's own choice - the SQL text
# alone, the text with its parameters, or everything including the rows that came back.
# The default is off - a connection that never asked for auditing leaves no trail
# and pays nothing.

from __future__ import annotations

# stdlib
from json import dumps

# Zato
from zato.common.audit_log.api import AuditEvent, AuditSource

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.audit_log.api import AuditLog
    from zato.common.typing_ import anylistnone, intnone, strdictnone
    AuditLog = AuditLog
    anylistnone = anylistnone
    intnone = intnone
    strdictnone = strdictnone

# ################################################################################################################################
# ################################################################################################################################

# The config key carrying an outgoing SQL connection's audit level - it comes from
# the connection's own Audit log field in the dashboard, or from enmasse.
Config_Audit_Log = 'audit_log'

# How much of each statement travels with its event.
Level_Off              = 'off'
Level_Statement        = 'statement'
Level_Statement_Params = 'statement-params'
Level_Full             = 'full'

# Everything a connection may ask for - anything else in its configuration is a typo
# that must not pass in silence, an audit trail that silently is not there is worse
# than a connection that refuses to start.
all_levels = {Level_Off, Level_Statement, Level_Statement_Params, Level_Full}

# The levels that carry the statement's parameters with the event
_levels_with_params = {Level_Statement_Params, Level_Full}

# ################################################################################################################################
# ################################################################################################################################

def record_sql_execution(
    audit_log:'AuditLog',
    conn_name:'str',
    level:'str',
    statement:'str',
    *,
    cid:'str',
    endpoint:'str',
    outcome:'str',
    params:'strdictnone' = None,
    rows:'anylistnone' = None,
    duration_ms:'int' = 0,
    error:'str' = '',
    ) -> 'intnone':
    """ Writes one audit event describing one executed SQL statement. The level says
    how much travels with the event - the statement alone, the statement with its
    parameters, or everything including the rows that came back. Returns the event id.
    """

    # The statement itself is on record at every level
    summary = {
        'statement': statement,
    }

    # The parameters travel only when the connection asked for them
    if level in _levels_with_params:
        summary['params'] = params

    # The rows travel only at the full level, and only when there are any -
    # a failed statement has none to speak of.
    if level == Level_Full and rows is not None:
        summary['rows'] = rows
        summary['row_count'] = len(rows)

    # A failed statement says what went wrong right in its data
    if error:
        summary['error'] = error

    # The level and the duration are searchable attributes -
    # "everything this connection ran with rows attached" and "the slowest statements" are one query each.
    attrs = {
        'level': level,
        'duration_ms': duration_ms,
    }

    # Database values such as timestamps or decimals are not JSON on their own,
    # which is what default=str is for.
    data = dumps(summary, default=str)

    # Our response to produce
    out = audit_log.insert(AuditSource.SQL_Outgoing, AuditEvent.Request_Sent, conn_name,
        cid=cid, endpoint=endpoint, outcome=outcome, duration_ms=duration_ms, data=data, attrs=attrs)

    return out

# ################################################################################################################################
# ################################################################################################################################
