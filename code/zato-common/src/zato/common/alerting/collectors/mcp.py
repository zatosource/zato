# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The MCP gateway producers - what an agent did wrong within a window, the tool calls naming a tool the gateway
# does not have or passing arguments its schema refused, what the gateway itself enforced, the responses a
# safeguard or the size cap refused, the ones the cap cut short and the callers a rate limit answered 429,
# one session calling one tool over and over, the bytes of every response added up, and how many tools each
# gateway exposes. Every windowed measure reads the attributes the gateway writes next to each request's row.

from __future__ import annotations

# stdlib
from datetime import datetime, timedelta

# SQLAlchemy
from sqlalchemy import and_, func, select

# Zato
from zato.common.alerting.collectors.common import new_fact
from zato.common.audit_log.api import event_attr_table, event_table, AuditEvent, AuditSource
from zato.common.audit_log.common import MCPAttr

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Engine
    from zato.common.typing_ import anylist, dictlist, strintdict
    anylist = anylist
    dictlist = dictlist
    Engine = Engine
    strintdict = strintdict

# ################################################################################################################################
# ################################################################################################################################

# The one source these collectors read - every MCP gateway writes its requests under it
MCP_Source = AuditSource.MCP

# The JSON-RPC error codes of a call that was the agent's mistake - a tool the gateway does not expose
# and arguments its schema refused - rather than the backend's
Error_Code_Method_Not_Found = -32601
Error_Code_Invalid_Params   = -32602

_invalid_call_error_codes = (Error_Code_Method_Not_Found, Error_Code_Invalid_Params)

# What the was_truncated attribute reads as when the size cap cut a response - a boolean is stored as its text
_was_truncated_value = str(True)

# A session that called a tool once is not repeating itself
_repeat_call_min_count = 2

# ################################################################################################################################
# ################################################################################################################################

def _window_conditions(window_seconds:'int', now:'datetime', object_name:'str', event_type:'str') -> 'anylist':
    """ The predicates every row of one event type of the gateways within the window satisfies - the source,
    the moment, the type and, when asked about one gateway, its name.
    """
    window_start = now - timedelta(seconds=window_seconds)
    window_start_iso = window_start.isoformat()

    out = [
        event_table.c.event_time_iso >= window_start_iso,
        event_table.c.source == MCP_Source,
        event_table.c.event_type == event_type,
    ]

    # The optional criterion narrows the measures only when set
    if object_name:
        out.append(event_table.c.object_name == object_name)

    return out

# ################################################################################################################################

def _count_rows_by_object(engine:'Engine', conditions:'anylist', *, with_attrs:'bool') -> 'strintdict':
    """ How many rows satisfy the predicates, per gateway - joined on the attributes when a predicate reads one.
    """
    statement = select(
        event_table.c.object_name,
        func.count(),
    )

    if with_attrs:
        statement = statement.select_from(event_table.join(event_attr_table, event_attr_table.c.event_id == event_table.c.id))

    statement = statement.where(and_(*conditions)).group_by(event_table.c.object_name)

    with engine.connect() as connection:
        rows = connection.execute(statement).fetchall()

    # Our response to produce
    out:'strintdict' = {}

    for row_object_name, count in rows:
        out[row_object_name] = count

    return out

# ################################################################################################################################

def _count_facts(counts_by_object:'strintdict', key:'str', window_seconds:'int') -> 'dictlist':
    """ One fact per gateway with a count, the count under the given key.
    """

    # Our response to produce
    out:'dictlist' = []

    for row_object_name in sorted(counts_by_object):

        fact = new_fact(MCP_Source, row_object_name)
        fact[key] = counts_by_object[row_object_name]
        fact['window_seconds'] = window_seconds

        out.append(fact)

    return out

# ################################################################################################################################

def _is_other_source(source:'str') -> 'bool':
    """ Whether a read narrowed to a source is about anything but the gateways.
    """
    out = bool(source) and source != MCP_Source
    return out

# ################################################################################################################################

def collect_invalid_call_facts(
    engine:'Engine',
    window_seconds:'int',
    now:'datetime',
    *,
    source:'str' = '',
    object_name:'str' = '',
    ) -> 'dictlist':
    """ Measures the tool calls within the window that were the agent's mistake - the rows whose error_code
    attribute is -32601, a tool the gateway does not expose, or -32602, arguments its schema refused -
    into `invalid_call_count`, one fact per gateway that had any.
    """
    if _is_other_source(source):
        return []

    conditions = _window_conditions(window_seconds, now, object_name, AuditEvent.MCP_Tools_Call)
    conditions.append(event_attr_table.c.name == MCPAttr.Error_Code)
    conditions.append(event_attr_table.c.value_number.in_(_invalid_call_error_codes))

    counts_by_object = _count_rows_by_object(engine, conditions, with_attrs=True)

    out = _count_facts(counts_by_object, 'invalid_call_count', window_seconds)
    return out

# ################################################################################################################################

def collect_rejection_facts(
    engine:'Engine',
    window_seconds:'int',
    now:'datetime',
    *,
    source:'str' = '',
    object_name:'str' = '',
    ) -> 'dictlist':
    """ Measures the tool calls within the window whose response the gateway refused to pass on - the rows with
    a reject_kind attribute, a safeguard in reject mode or the size cap in block mode - into `rejection_count`.
    """
    if _is_other_source(source):
        return []

    conditions = _window_conditions(window_seconds, now, object_name, AuditEvent.MCP_Tools_Call)
    conditions.append(event_attr_table.c.name == MCPAttr.Reject_Kind)

    counts_by_object = _count_rows_by_object(engine, conditions, with_attrs=True)

    out = _count_facts(counts_by_object, 'rejection_count', window_seconds)
    return out

# ################################################################################################################################

def collect_throttled_facts(
    engine:'Engine',
    window_seconds:'int',
    now:'datetime',
    *,
    source:'str' = '',
    object_name:'str' = '',
    ) -> 'dictlist':
    """ Measures the requests within the window a caller's own rate limit answered 429 - the gateway's
    rate-limited rows - into `throttled_count`.
    """
    if _is_other_source(source):
        return []

    conditions = _window_conditions(window_seconds, now, object_name, AuditEvent.Rate_Limited)

    counts_by_object = _count_rows_by_object(engine, conditions, with_attrs=False)

    out = _count_facts(counts_by_object, 'throttled_count', window_seconds)
    return out

# ################################################################################################################################

def collect_mcp_truncation_facts(
    engine:'Engine',
    window_seconds:'int',
    now:'datetime',
    *,
    source:'str' = '',
    object_name:'str' = '',
    ) -> 'dictlist':
    """ Measures the tool calls within the window whose response the size cap cut short - the rows whose
    was_truncated attribute is true - into `truncation_count`, the key the LLM truncations use as well.
    """
    if _is_other_source(source):
        return []

    conditions = _window_conditions(window_seconds, now, object_name, AuditEvent.MCP_Tools_Call)
    conditions.append(event_attr_table.c.name == MCPAttr.Was_Truncated)
    conditions.append(event_attr_table.c.value == _was_truncated_value)

    counts_by_object = _count_rows_by_object(engine, conditions, with_attrs=True)

    out = _count_facts(counts_by_object, 'truncation_count', window_seconds)
    return out

# ################################################################################################################################

def collect_volume_facts(
    engine:'Engine',
    window_seconds:'int',
    now:'datetime',
    *,
    source:'str' = '',
    object_name:'str' = '',
    ) -> 'dictlist':
    """ Measures the bytes of every tool call's response within the window, added up per gateway into `volume_bytes`.
    """
    if _is_other_source(source):
        return []

    conditions = _window_conditions(window_seconds, now, object_name, AuditEvent.MCP_Tools_Call)

    statement = select(
        event_table.c.object_name,
        func.sum(event_table.c.size),
    ).where(and_(*conditions)).group_by(event_table.c.object_name)

    with engine.connect() as connection:
        rows = connection.execute(statement).fetchall()

    volume_by_object:'strintdict' = {}

    for row_object_name, total in rows:

        # Each backend returns its own numeric type for a sum, hence the conversion
        volume_bytes = int(total)

        # A gateway whose responses were all empty has nothing to say
        if not volume_bytes:
            continue

        volume_by_object[row_object_name] = volume_bytes

    out = _count_facts(volume_by_object, 'volume_bytes', window_seconds)
    return out

# ################################################################################################################################

def collect_repeat_call_facts(
    engine:'Engine',
    window_seconds:'int',
    now:'datetime',
    *,
    source:'str' = '',
    object_name:'str' = '',
    ) -> 'dictlist':
    """ Measures how many times one session called one tool within the window - the tool calls grouped by gateway,
    session and tool, each gateway keeping its largest count as `repeat_call_count` with the tool as `repeat_call_tool`
    and the session as `repeat_call_session`, which is the agent most likely stuck in a loop. Two sessions calling
    the same tool are two groups and never add up.
    """
    if _is_other_source(source):
        return []

    conditions = _window_conditions(window_seconds, now, object_name, AuditEvent.MCP_Tools_Call)

    # A row without a session cannot repeat itself
    conditions.append(event_table.c.sub_key != '')

    call_count = func.count().label('call_count')

    statement = select(
        event_table.c.object_name,
        event_table.c.sub_key,
        event_table.c.endpoint,
        call_count,
    ).where(and_(*conditions)).group_by(
        event_table.c.object_name, event_table.c.sub_key, event_table.c.endpoint,
    ).having(call_count >= _repeat_call_min_count)

    with engine.connect() as connection:
        rows = connection.execute(statement).fetchall()

    # The worst offender of each gateway - the largest count, the first one read on a tie
    worst_by_object:'dict[str, tuple[int, str, str]]' = {}

    for row_object_name, session_id, tool_name, count in rows:

        if row_object_name in worst_by_object:
            if count <= worst_by_object[row_object_name][0]:
                continue

        worst_by_object[row_object_name] = (count, tool_name, session_id)

    # Our response to produce
    out:'dictlist' = []

    for row_object_name in sorted(worst_by_object):

        count, tool_name, session_id = worst_by_object[row_object_name]

        fact = new_fact(MCP_Source, row_object_name)
        fact['repeat_call_count'] = count
        fact['repeat_call_tool'] = tool_name
        fact['repeat_call_session'] = session_id
        fact['window_seconds'] = window_seconds

        out.append(fact)

    return out

# ################################################################################################################################

def collect_tool_count_facts(tool_counts:'strintdict') -> 'dictlist':
    """ One fact per gateway the sweep knows the tool count of, with `tool_count` - read off the gateway itself
    rather than the audit log, so a gateway nobody has called yet is measured all the same.
    """

    # Our response to produce
    out:'dictlist' = []

    for gateway_name in sorted(tool_counts):

        fact = new_fact(MCP_Source, gateway_name)
        fact['tool_count'] = tool_counts[gateway_name]

        out.append(fact)

    return out

# ################################################################################################################################
# ################################################################################################################################
