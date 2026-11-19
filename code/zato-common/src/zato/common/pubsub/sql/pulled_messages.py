# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The building of the messages that pulls hand out from their leased rows, with the audit events of their reception,
# which runs in Rust in the transaction that leases the rows.

# Zato
from zato.common.api import HTTP_SOAP
from zato.common.audit_log.api import AuditEvent, AuditOutcome, AuditSource
from zato.common.pubsub.sql.pull import message_columns
from zato.common.util.time_ import parse_utc

# Zato - Rust
from zato_common_core.zato_common_core import PulledMessageBuilder

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strlist, strset

    # Dummy assignments to satisfy type checkers
    strlist = strlist
    strset = strset

# ################################################################################################################################
# ################################################################################################################################

_retry = HTTP_SOAP.Retry

# ################################################################################################################################
# ################################################################################################################################

def _get_column_names() -> 'strlist':
    """ Returns the names of the columns of the rows that a pull reads, in the order of the query.
    """
    out:'strlist' = []

    for column in message_columns:
        out.append(column.name)

    return out

# ################################################################################################################################

def new_pulled_message_builder(audit_disabled_topics:'strset', audit_payload_topics:'strset') -> 'PulledMessageBuilder':
    """ Returns the builder of the messages that pulls hand out, which reads the given topic sets of one backend
    on every pull.
    """
    column_names = _get_column_names()

    config = {
        'columns': column_names,
        'retry_names': _retry.FieldList,
        'audit_disabled_topics': audit_disabled_topics,
        'audit_payload_topics': audit_payload_topics,
        'parse_utc': parse_utc,
        'event_source': AuditSource.PubSub,
        'event_type': AuditEvent.Received,
        'event_outcome': AuditOutcome.OK,
    }

    out = PulledMessageBuilder(config)
    return out

# ################################################################################################################################
# ################################################################################################################################
