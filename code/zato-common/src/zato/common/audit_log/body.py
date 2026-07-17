# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.common.audit_log.common import event_body_table

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Engine
    from zato.common.typing_ import callable_, strcalldict, strnone

    # Dummy assignments to satisfy type checkers
    Engine = Engine
    callable_ = callable_
    strcalldict = strcalldict
    strnone = strnone

# ################################################################################################################################
# ################################################################################################################################

# Sources whose bodies live outside the audit database register a resolver here.
# A resolver is a callable taking (event_id, kind) and returning the body or None.
_resolver_registry:'strcalldict' = {}

# ################################################################################################################################

def register_body_resolver(source:'str', resolver:'callable_') -> 'None':
    """ Registers a resolver returning message bodies for one audit source -
    for sources that keep their bodies in their own store rather than in the audit database.
    """
    _resolver_registry[source] = resolver

# ################################################################################################################################

def resolve_body(engine:'Engine', source:'str', event_id:'int', kind:'str'='') -> 'strnone':
    """ Returns the body of one event - through the source's own resolver if it registered one,
    out of the shared body table otherwise. An empty kind returns the newest body of any kind.
    """

    # A source with its own body store answers for itself ..
    if resolver := _resolver_registry.get(source):
        out = resolver(event_id, kind)
        return out

    # .. everything else reads the shared table.
    query = select(event_body_table.c.data)
    query = query.where(event_body_table.c.event_id == event_id)

    if kind:
        query = query.where(event_body_table.c.kind == kind)

    query = query.order_by(event_body_table.c.id.desc())
    query = query.limit(1)

    with engine.connect() as connection:
        result = connection.execute(query)
        row = result.first()

    if row:
        out = row[0]
    else:
        out = None

    return out

# ################################################################################################################################
# ################################################################################################################################
