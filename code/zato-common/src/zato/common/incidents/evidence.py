# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# SQLAlchemy
from sqlalchemy import and_, select

# Zato
from zato.common.audit_log.common import event_table, AuditOutcome

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Engine
    from zato.common.typing_ import dictlist, stranydict
    Engine = Engine

# ################################################################################################################################
# ################################################################################################################################

# The configuration keys that go into an evidence pack - addressing, timeouts and security
# identifiers only, never the credentials themselves.
_config_keys = (
    'name',
    'is_active',
    'address_host',
    'address_url_path',
    'method',
    'data_format',
    'content_type',
    'timeout',
    'pool_size',
    'validate_tls',
    'ping_method',
    'security_name',
    'sec_type',
    'username',
)

# ################################################################################################################################
# ################################################################################################################################

def collect_audit_trail(
    engine:'Engine',
    source:'str',
    object_name:'str',
    max_events:'int',
    ) -> 'dictlist':
    """ Returns the newest audit events of one connection, newest first. Failed events carry
    their data - the error text or the response body - and successful ones do not,
    which keeps the pack small while showing every error in full.
    """

    # Our response to produce
    out:'dictlist' = []

    statement = select(
        event_table.c.cid,
        event_table.c.event_type,
        event_table.c.endpoint,
        event_table.c.outcome,
        event_table.c.status,
        event_table.c.event_time_iso,
        event_table.c.size,
        event_table.c.duration_ms,
        event_table.c.data,
    ).where(and_(
        event_table.c.source == source,
        event_table.c.object_name == object_name,
    )).order_by(event_table.c.id.desc()).limit(max_events)

    with engine.connect() as connection:
        rows = connection.execute(statement).fetchall()

    for cid, event_type, endpoint, outcome, status, event_time_iso, size, duration_ms, data in rows:

        event:'stranydict' = {
            'cid': cid,
            'event_type': event_type,
            'endpoint': endpoint,
            'outcome': outcome,
            'status': status,
            'event_time_iso': event_time_iso,
            'size': size,
            'duration_ms': duration_ms,
        }

        # Only failed events carry their data - that is where the error text lives.
        if outcome == AuditOutcome.Error:
            event['data'] = data

        out.append(event)

    return out

# ################################################################################################################################

def build_evidence(alert:'stranydict', conn_config:'stranydict', audit_trail:'dictlist') -> 'stranydict':
    """ Assembles the pack the diagnosis works from - the alert that fired, the connection's
    configuration reduced to its non-secret keys, and the audit trail.
    """

    # Only the keys of interest go in, and only when the connection's configuration has them -
    # e.g. a connection with no security definition has no security_name at all.
    connection:'stranydict' = {}

    for key in _config_keys:
        if key in conn_config:
            connection[key] = conn_config[key]

    out = {
        'alert': alert,
        'connection': connection,
        'audit_trail': audit_trail,
    }

    return out

# ################################################################################################################################
# ################################################################################################################################
