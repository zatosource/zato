# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What every evidence reader shares - the columns an evidence row carries, how a query's rows become
# evidence rows, where a fact's window starts and the cap on how many rows one measure contributes.

from __future__ import annotations

# stdlib
from datetime import timedelta

# SQLAlchemy
from sqlalchemy import and_, select

# Zato
from zato.common.alerting.collectors.common import Default_Window_Seconds
from zato.common.audit_log.api import event_table

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from sqlalchemy.engine import Engine
    from zato.common.typing_ import anylist, dictlist, stranydict
    anylist = anylist
    datetime = datetime
    dictlist = dictlist
    Engine = Engine
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

# How many rows one measure contributes at most - the budget the document is fitted to
# trims further, this only keeps a very busy connection from being read in full.
Max_Rows_Per_Measure = 200

# The columns every evidence row carries.
row_columns = (
    event_table.c.id,
    event_table.c.event_time_iso,
    event_table.c.event_type,
    event_table.c.endpoint,
    event_table.c.outcome,
    event_table.c.status,
    event_table.c.duration_ms,
    event_table.c.data,
    event_table.c.ext_client_id,
    event_table.c.application_outcome,
)

# ################################################################################################################################
# ################################################################################################################################

def window_start_iso(fact:'stranydict', now:'datetime') -> 'str':
    """ Where the fact's window starts - a fact measured without a window, e.g. a probe's
    point-in-time reading, is read over the default window instead.
    """
    window_seconds = fact['window_seconds']

    if not window_seconds:
        window_seconds = Default_Window_Seconds

    start = now - timedelta(seconds=window_seconds)
    out = start.isoformat()

    return out

# ################################################################################################################################

def rows_from(result:'anylist') -> 'dictlist':
    """ The rows of a query as evidence rows.
    """

    # Our response to produce
    out:'dictlist' = []

    for event_id, event_time_iso, event_type, endpoint, outcome, status, duration_ms, data, ext_client_id, \
        application_outcome in result:

        row:'stranydict' = {
            'id': event_id,
            'event_time_iso': event_time_iso,
            'event_type': event_type,
            'endpoint': endpoint,
            'outcome': outcome,
            'status': status,
            'duration_ms': duration_ms,
            'data': data,
            'ext_client_id': ext_client_id,
            'application_outcome': application_outcome,
        }

        out.append(row)

    return out

# ################################################################################################################################

def select_rows(engine:'Engine', conditions:'anylist') -> 'dictlist':
    """ The newest rows meeting the conditions, newest first, capped per measure.
    """
    statement = select(*row_columns).where(and_(*conditions)).order_by(event_table.c.id.desc()).limit(Max_Rows_Per_Measure)

    with engine.connect() as connection:
        result = connection.execute(statement).fetchall()

    out = rows_from(result)
    return out

# ################################################################################################################################
# ################################################################################################################################
