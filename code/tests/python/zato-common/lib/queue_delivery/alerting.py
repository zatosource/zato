# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The alerting side of queue delivery as the shared scenarios reach it - running one sweep on the server and reading
# the alerts it raised about a connection out of the audit log.

# stdlib
from json import loads

# SQLAlchemy
from sqlalchemy import func, select

# Zato
from zato.common.api import Alerting
from zato.common.audit_log.api import event_table, get_audit_engine
from zato.common.audit_log.common import AuditEvent

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.client import AdminClient
    from zato.common.typing_ import anylist

# ################################################################################################################################
# ################################################################################################################################

def get_newest_audit_event_id() -> 'int':
    """ The id of the newest event the audit log holds, zero when it holds none - what a scenario remembers before
    a sweep so it reads the alerts of that sweep alone.
    """
    engine = get_audit_engine()

    query = select(func.max(event_table.c.id))

    with engine.connect() as connection:
        out = connection.execute(query).scalar()

    if out is None:
        out = 0

    return out

# ################################################################################################################################

def run_sweep(client:'AdminClient') -> 'None':
    """ Runs one alerting sweep on the server, the way the scheduler does - with no extra of its own, so the alerts
    are raised and recorded and nothing needs delivering.
    """
    _ = client.invoke(Alerting.Service, {})

# ################################################################################################################################

def get_alerts_raised(object_name:'str', since_id:'int') -> 'anylist':
    """ The alerts raised about one object after the given event, oldest first - each with the source it was filed
    under and the rule that raised it.
    """
    engine = get_audit_engine()

    query = select(event_table)
    query = query.where(event_table.c.event_type == AuditEvent.Alert_Raised)
    query = query.where(event_table.c.object_name == object_name)
    query = query.where(event_table.c.id > since_id)
    query = query.order_by(event_table.c.id)

    out:'anylist' = []

    with engine.connect() as connection:
        for row in connection.execute(query):
            event = dict(row._mapping)
            details = loads(event['data'])

            out.append({
                'source': event['source'],
                'rule': details['rule'],
                'message': details['message'],
            })

    return out

# ################################################################################################################################
# ################################################################################################################################
