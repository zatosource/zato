# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The queue delivery producer - one fact per outgoing connection that has a queue or a DLQ, with how many messages
# wait in the queue and how many the DLQ holds. Both numbers are read off the connection itself rather than the
# audit log, the way an MCP gateway's tool count is, so a connection nobody has called within any window is
# measured all the same and the measure has no window.

from __future__ import annotations

# Zato
from zato.common.alerting.collectors.common import new_fact
from zato.common.audit_log.api import AuditSource
from zato.common.pubsub.outgoing import OutgoingType

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, dictlist, strdict

# ################################################################################################################################
# ################################################################################################################################

# The audit source each kind of outgoing connection writes under - what the rules of its alert type match on
_source_by_conn_type:'strdict' = {
    OutgoingType.REST: AuditSource.REST_Outgoing,
    OutgoingType.SOAP: AuditSource.SOAP_Outgoing,
    OutgoingType.FHIR: AuditSource.FHIR,
    OutgoingType.MLLP: AuditSource.MLLP_Outgoing,
}

# ################################################################################################################################
# ################################################################################################################################

def collect_queue_facts(queue_rows:'dictlist | None') -> 'dictlist':
    """ One fact per outgoing connection the sweep knows the queue and DLQ depths of, with `queue_depth` and
    `dlq_depth` - the rows are the ones the delivery page lists, one per connection that has a queue or a DLQ.
    A connection of a kind that has no alert type of its own is left out.
    """

    # Our response to produce
    out:'dictlist' = []

    if not queue_rows:
        return out

    for row in sorted(queue_rows, key=_row_key):

        conn_type = row['conn_type']

        # A kind of connection whose alerts are not measured here
        if conn_type not in _source_by_conn_type:
            continue

        fact = new_fact(_source_by_conn_type[conn_type], row['name'])
        fact['queue_depth'] = row['queue_depth']
        fact['dlq_depth'] = row['dlq_depth']

        out.append(fact)

    return out

# ################################################################################################################################

def _row_key(row:'anydict') -> 'tuple[str, str]':
    """ The rows in a stable order - by kind, then by name.
    """
    out = (row['conn_type'], row['name'])
    return out

# ################################################################################################################################
# ################################################################################################################################
