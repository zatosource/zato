# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The LLM producers - the tokens an outgoing LLM connection's calls used within a window, and the completions
# the provider cut short or declined to give. Both read the attributes the LLM wrapper writes next to each
# call's row - input_tokens and output_tokens as numbers, finish_reason as text - so nothing is parsed here.

from __future__ import annotations

# stdlib
from datetime import datetime, timedelta

# SQLAlchemy
from sqlalchemy import and_, func, select

# Zato
from zato.common.alerting.collectors.common import new_fact
from zato.common.audit_log.api import event_attr_table, event_table, AuditSource
from zato.common.audit_log.common import LLMAttr, LLMFinish

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Engine
    from zato.common.typing_ import dictlist, strintdict
    dictlist = dictlist
    Engine = Engine
    strintdict = strintdict

# ################################################################################################################################
# ################################################################################################################################

# The one source these collectors read - every LLM connection writes its calls under it
LLM_Source = AuditSource.LLM

# The fact key each counted finish reason lands under - a stop and a tool use are not counted
_count_key_by_finish_reason = {
    LLMFinish.Length:  'truncation_count',
    LLMFinish.Refusal: 'refusal_count',
}

# ################################################################################################################################
# ################################################################################################################################

def _window_conditions(window_seconds:'int', now:'datetime', object_name:'str') -> 'list':
    """ The predicates every LLM row within the window satisfies - the source, the moment and, when asked
    about one connection, its name.
    """
    window_start = now - timedelta(seconds=window_seconds)
    window_start_iso = window_start.isoformat()

    out = [
        event_table.c.event_time_iso >= window_start_iso,
        event_table.c.source == LLM_Source,
    ]

    # The optional criterion narrows the measures only when set
    if object_name:
        out.append(event_table.c.object_name == object_name)

    return out

# ################################################################################################################################

def collect_llm_token_facts(
    engine:'Engine',
    window_seconds:'int',
    now:'datetime',
    *,
    source:'str' = '',
    object_name:'str' = '',
    ) -> 'dictlist':
    """ Measures the tokens every outgoing LLM connection used within the window - the sum of the numeric
    input_tokens and output_tokens attributes of its calls, into `input_token_count`, `output_token_count`
    and their total `token_count`, one fact per connection whose calls used any. A failed call carries no
    usage and adds nothing, so a connection that only failed gets no fact here.
    """

    # Our response to produce
    out:'dictlist' = []

    # Only the LLM source has tokens to add up
    if source:
        if source != LLM_Source:
            return out

    conditions = _window_conditions(window_seconds, now, object_name)

    # Both token attributes of every row in the window, added up per connection and per attribute name
    conditions.append(event_attr_table.c.name.in_([LLMAttr.Input_Tokens, LLMAttr.Output_Tokens]))

    statement = select(
        event_table.c.object_name,
        event_attr_table.c.name,
        func.sum(event_attr_table.c.value_number),
    ).select_from(
        event_table.join(event_attr_table, event_attr_table.c.event_id == event_table.c.id)
    ).where(and_(*conditions)).group_by(event_table.c.object_name, event_attr_table.c.name)

    with engine.connect() as connection:
        rows = connection.execute(statement).fetchall()

    # The two counts of each connection, by attribute name
    counts_by_object:'dict[str, strintdict]' = {}

    for row_object_name, attr_name, total in rows:

        # Each backend returns its own numeric type for a sum, hence the conversion
        count = int(total)

        counts = counts_by_object.setdefault(row_object_name, {LLMAttr.Input_Tokens: 0, LLMAttr.Output_Tokens: 0})
        counts[attr_name] = count

    for row_object_name in sorted(counts_by_object):

        counts = counts_by_object[row_object_name]
        input_token_count = counts[LLMAttr.Input_Tokens]
        output_token_count = counts[LLMAttr.Output_Tokens]
        token_count = input_token_count + output_token_count

        # A connection whose calls used nothing at all has nothing to say
        if not token_count:
            continue

        fact = new_fact(LLM_Source, row_object_name)
        fact['token_count'] = token_count
        fact['input_token_count'] = input_token_count
        fact['output_token_count'] = output_token_count
        fact['window_seconds'] = window_seconds

        out.append(fact)

    return out

# ################################################################################################################################

def collect_llm_completion_facts(
    engine:'Engine',
    window_seconds:'int',
    now:'datetime',
    *,
    source:'str' = '',
    object_name:'str' = '',
    ) -> 'dictlist':
    """ Measures the completions every outgoing LLM connection was cut short on or refused within the window -
    the rows whose finish_reason attribute is `length`, into `truncation_count`, and the ones whose is `refusal`,
    into `refusal_count`, one fact per connection that had either, carrying both. A truncation and a refusal
    are OK rows, the provider answered with HTTP 200, which is why they are counted here and not among the errors,
    while a Gemini prompt block is an Error row with a refusal for its finish reason and is counted here all the same.
    """

    # Our response to produce
    out:'dictlist' = []

    # Only the LLM source has completions to count
    if source:
        if source != LLM_Source:
            return out

    conditions = _window_conditions(window_seconds, now, object_name)

    # The finish reason of every row in the window, counted per connection and per reason, the two counted ones only
    conditions.append(event_attr_table.c.name == LLMAttr.Finish_Reason)
    conditions.append(event_attr_table.c.value.in_(list(_count_key_by_finish_reason)))

    statement = select(
        event_table.c.object_name,
        event_attr_table.c.value,
        func.count(),
    ).select_from(
        event_table.join(event_attr_table, event_attr_table.c.event_id == event_table.c.id)
    ).where(and_(*conditions)).group_by(event_table.c.object_name, event_attr_table.c.value)

    with engine.connect() as connection:
        rows = connection.execute(statement).fetchall()

    # The two counts of each connection, by the fact key each finish reason lands under
    counts_by_object:'dict[str, strintdict]' = {}

    for row_object_name, finish_reason, count in rows:
        counts = counts_by_object.setdefault(row_object_name, {})
        counts[_count_key_by_finish_reason[finish_reason]] = count

    for row_object_name in sorted(counts_by_object):

        fact = new_fact(LLM_Source, row_object_name)
        fact['window_seconds'] = window_seconds

        for key, count in counts_by_object[row_object_name].items():
            fact[key] = count

        out.append(fact)

    return out

# ################################################################################################################################
# ################################################################################################################################
