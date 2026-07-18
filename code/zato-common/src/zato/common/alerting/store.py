# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The alert store - alerts with their dedup count and lifecycle. A repeated finding
# about the same object within its rule's window increments the existing alert's count
# instead of raising a new one, so a flapping channel produces a single alert rendered
# as `[17x] channel adt.main silent` rather than seventeen rows. Acknowledgment
# and resolution are recorded in place, with the acting user and the time.

from __future__ import annotations

# stdlib
from dataclasses import dataclass
from datetime import datetime, timedelta

# SQLAlchemy
from sqlalchemy import select, update

# Zato
from zato.common.alerting.model import AlertState
from zato.common.audit_log.common import alert_table

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Engine
    from zato.common.alerting.model import AlertRule, Finding
    from zato.common.typing_ import anydict, dictlist, intnone
    AlertRule = AlertRule
    anydict = anydict
    dictlist = dictlist
    Engine = Engine
    Finding = Finding
    intnone = intnone

# ################################################################################################################################
# ################################################################################################################################

# How many repetitions make the count prefix appear - a first occurrence has no prefix.
_prefix_from_count = 2

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class RaiseResult:
    """ The result of raising one alert - either a new row or an incremented count
    on an existing one.
    """
    alert_id: 'intnone' = None
    is_new: bool = False
    count: int = 0

# ################################################################################################################################
# ################################################################################################################################

def _find_open_alert(engine:'Engine', rule_name:'str', finding:'Finding') -> 'anydict | None':
    """ Returns the newest unresolved alert of one rule about one object, or None.
    """
    statement = select(alert_table)
    statement = statement.where(alert_table.c.rule_name == rule_name)
    statement = statement.where(alert_table.c.object_name == finding.object_name)
    statement = statement.where(alert_table.c.kind == finding.kind)
    statement = statement.where(alert_table.c.state != AlertState.Resolved)
    statement = statement.order_by(alert_table.c.id.desc())
    statement = statement.limit(1)

    with engine.connect() as connection:
        result = connection.execute(statement)
        row = result.first()

    if row is None:
        return None

    out = dict(row._mapping)
    return out

# ################################################################################################################################

def raise_alert(engine:'Engine', rule:'AlertRule', finding:'Finding', now:'datetime') -> 'RaiseResult':
    """ Records one finding as an alert - a new row, unless an unresolved alert
    of the same rule about the same object was raised within the dedup window,
    in which case its count grows by one instead.
    """

    # Our response to produce
    out = RaiseResult()

    now_iso = now.isoformat()

    existing = _find_open_alert(engine, rule.name, finding)

    if existing:

        # An unresolved alert younger than the window absorbs the repetition ..
        last_raised = datetime.fromisoformat(existing['last_raised_iso'])
        window_end = last_raised + timedelta(seconds=rule.dedup_window_seconds)

        if now < window_end:

            new_count = existing['count'] + 1

            statement = update(alert_table)
            statement = statement.where(alert_table.c.id == existing['id'])
            statement = statement.values(count=new_count, last_raised_iso=now_iso, message=finding.message)

            with engine.begin() as connection:
                _ = connection.execute(statement)

            out.alert_id = existing['id']
            out.is_new = False
            out.count = new_count

            return out

    # .. otherwise the finding becomes a new alert of its own.
    values = {
        'rule_name': rule.name,
        'source': finding.source,
        'object_name': finding.object_name,
        'kind': finding.kind,
        'severity': finding.severity,
        'message': finding.message,
        'link': finding.link,
        'count': 1,
        'state': AlertState.Unobserved,
        'first_raised_iso': now_iso,
        'last_raised_iso': now_iso,
        'observed_by': '',
        'observed_iso': '',
        'resolved_by': '',
        'resolved_iso': '',
    }

    with engine.begin() as connection:
        result = connection.execute(alert_table.insert().values(**values))

    out.alert_id = result.inserted_primary_key[0]
    out.is_new = True
    out.count = 1

    return out

# ################################################################################################################################

def observe_alert(engine:'Engine', alert_id:'int', observed_by:'str', now:'datetime') -> 'None':
    """ Records that an operator acknowledged one alert.
    """
    statement = update(alert_table)
    statement = statement.where(alert_table.c.id == alert_id)
    statement = statement.values(state=AlertState.Observed, observed_by=observed_by, observed_iso=now.isoformat())

    with engine.begin() as connection:
        _ = connection.execute(statement)

# ################################################################################################################################

def resolve_alert(engine:'Engine', alert_id:'int', resolved_by:'str', now:'datetime') -> 'None':
    """ Records that one alert was resolved - subsequent findings about the same object
    raise a new alert instead of incrementing this one.
    """
    statement = update(alert_table)
    statement = statement.where(alert_table.c.id == alert_id)
    statement = statement.values(state=AlertState.Resolved, resolved_by=resolved_by, resolved_iso=now.isoformat())

    with engine.begin() as connection:
        _ = connection.execute(statement)

# ################################################################################################################################

def get_alerts(engine:'Engine', *, state:'str'='') -> 'dictlist':
    """ Returns alerts as dicts, newest first, optionally of one lifecycle state.
    """
    statement = select(alert_table)

    if state:
        statement = statement.where(alert_table.c.state == state)

    statement = statement.order_by(alert_table.c.id.desc())

    out:'dictlist' = []

    with engine.connect() as connection:
        for row in connection.execute(statement):
            out.append(dict(row._mapping))

    return out

# ################################################################################################################################

def render_alert_message(count:'int', message:'str') -> 'str':
    """ Renders one alert line - repetitions show up as a count prefix,
    `[3x] channel adt.main silent`, in the UI and in email digests alike.
    """
    if count >= _prefix_from_count:
        out = f'[{count}x] {message}'
    else:
        out = message

    return out

# ################################################################################################################################
# ################################################################################################################################
