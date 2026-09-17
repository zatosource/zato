# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The evidence behind an MCP gateway's alerts - the tool calls each measure was counted from, read the way
# the collectors counted them, and what a gateway's row says went wrong rewritten from its data document
# into one line a person and the LLM can read - the error text, the error code, what refused the response
# and whether the cap cut it.

from __future__ import annotations

# SQLAlchemy
from sqlalchemy import and_, select

# Zato
from zato.common.alerting.collectors.common import is_object, is_recent, is_source
from zato.common.alerting.collectors.evidence_rows import row_columns, rows_from, select_rows, window_start_iso, \
    Max_Rows_Per_Measure
from zato.common.alerting.collectors.mcp import Error_Code_Invalid_Params, Error_Code_Method_Not_Found
from zato.common.audit_log.api import event_attr_table, event_table, AuditEvent
from zato.common.audit_log.common import MCPAttr
from zato.common.json_internal import loads

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from sqlalchemy.engine import Engine
    from zato.common.typing_ import anylist, dictlist, stranydict, strlist
    anylist = anylist
    datetime = datetime
    dictlist = dictlist
    Engine = Engine
    stranydict = stranydict
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

# The error codes of the calls that were the agent's mistake, as the invalid-call collector counts them
_invalid_call_error_codes = (Error_Code_Method_Not_Found, Error_Code_Invalid_Params)

# What the was_truncated attribute reads as when the cap cut a response
_was_truncated_value = str(True)

# What a row says when its data document names no error - the response was refused or cut rather than failed
_text_rejected  = 'Response rejected'
_text_truncated = 'Response truncated'
_text_throttled = 'Caller rate-limited'

# The keys of the data document that go into the row's line after its error text, in this order
_detail_keys = ('error_code', 'reject_kind', 'was_truncated', 'tokens_before', 'tokens_after', 'retry_after_seconds')

# ################################################################################################################################
# ################################################################################################################################

def describe_mcp_row(data:'stranydict', event_type:'str') -> 'str':
    """ One line saying what a gateway's row was about - the error text when the call failed, what happened
    to the response otherwise, then the details the collectors counted by - `Unknown tool: get_orderz
    (error_code=-32601)`, `Response rejected (reject_kind=size, tokens_before=9000)`.
    """
    if 'error_message' in data:
        out = data['error_message']
    elif 'reject_kind' in data:
        out = _text_rejected
    elif 'was_truncated' in data:
        out = _text_truncated
    elif event_type == AuditEvent.Rate_Limited:
        out = _text_throttled
    else:
        out = event_type

    parts:'strlist' = []

    for key in _detail_keys:
        if key in data:
            parts.append(f'{key}={data[key]}')

    if parts:
        out = f'{out} ({", ".join(parts)})'

    return out

# ################################################################################################################################

def attach_mcp_details(rows:'dictlist') -> 'None':
    """ Rewrites each gateway row's data document into the one line the Failures section groups by,
    so two calls of a tool that does not exist read as one failure and a rejection reads as what refused it.
    """
    for row in rows:

        # A row without a document has nothing more to say than its type
        if not row['data']:
            row['data'] = row['event_type']
            continue

        data = loads(row['data'])
        row['data'] = describe_mcp_row(data, row['event_type'])

# ################################################################################################################################

def _select_attr_rows(engine:'Engine', fact:'stranydict', now:'datetime', attr_conditions:'anylist') -> 'dictlist':
    """ The gateway's tool calls within the fact's window whose attributes meet the conditions, newest first.
    """
    conditions = [
        is_source(fact['source']),
        is_object(fact['object_name']),
        event_table.c.event_type == AuditEvent.MCP_Tools_Call,
        is_recent(window_start_iso(fact, now)),
    ]
    conditions.extend(attr_conditions)

    attr_join = event_table.join(event_attr_table, event_table.c.id == event_attr_table.c.event_id)

    statement = select(*row_columns).select_from(attr_join).where(and_(*conditions))
    statement = statement.order_by(event_table.c.id.desc()).limit(Max_Rows_Per_Measure)

    with engine.connect() as connection:
        result = connection.execute(statement).fetchall()

    out = rows_from(result)
    attach_mcp_details(out)

    return out

# ################################################################################################################################

def collect_invalid_calls(engine:'Engine', fact:'stranydict', now:'datetime') -> 'dictlist':
    """ The tool calls the invalid-call count was counted from - the ones naming a tool the gateway
    does not expose or passing arguments its schema refused.
    """
    out = _select_attr_rows(engine, fact, now, [
        event_attr_table.c.name == MCPAttr.Error_Code,
        event_attr_table.c.value_number.in_(_invalid_call_error_codes),
    ])
    return out

# ################################################################################################################################

def collect_rejections(engine:'Engine', fact:'stranydict', now:'datetime') -> 'dictlist':
    """ The tool calls the rejection count was counted from - the ones whose response a safeguard or the cap refused.
    """
    out = _select_attr_rows(engine, fact, now, [
        event_attr_table.c.name == MCPAttr.Reject_Kind,
    ])
    return out

# ################################################################################################################################

def collect_mcp_truncations(engine:'Engine', fact:'stranydict', now:'datetime') -> 'dictlist':
    """ The tool calls the truncation count was counted from - the ones whose response the cap cut short.
    """
    out = _select_attr_rows(engine, fact, now, [
        event_attr_table.c.name == MCPAttr.Was_Truncated,
        event_attr_table.c.value == _was_truncated_value,
    ])
    return out

# ################################################################################################################################

def collect_throttled(engine:'Engine', fact:'stranydict', now:'datetime') -> 'dictlist':
    """ The requests the throttled count was counted from - the gateway's rate-limited rows, each naming its caller.
    """
    conditions = [
        is_source(fact['source']),
        is_object(fact['object_name']),
        event_table.c.event_type == AuditEvent.Rate_Limited,
        is_recent(window_start_iso(fact, now)),
    ]

    out = select_rows(engine, conditions)
    attach_mcp_details(out)

    return out

# ################################################################################################################################

def collect_repeat_calls(engine:'Engine', fact:'stranydict', now:'datetime') -> 'dictlist':
    """ The tool calls the repeat-call count was counted from - the calls of the one session to the one tool
    the fact names, whatever their outcome, so the evidence shows what an agent in a loop kept asking for.
    """
    conditions = [
        is_source(fact['source']),
        is_object(fact['object_name']),
        event_table.c.event_type == AuditEvent.MCP_Tools_Call,
        event_table.c.sub_key == fact['repeat_call_session'],
        event_table.c.endpoint == fact['repeat_call_tool'],
        is_recent(window_start_iso(fact, now)),
    ]

    out = select_rows(engine, conditions)
    attach_mcp_details(out)

    return out

# ################################################################################################################################
# ################################################################################################################################
