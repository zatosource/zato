# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The Object section of an outgoing MLLP connection's evidence - what the connection is, read off the ODB, so the
# model reads where the connection sends and how it copes with a failed send before it reads how its messages were
# acknowledged. The alert settings lines at its end are the ones explain/settings_info.py builds for every object
# that has alert settings.

from __future__ import annotations

# Zato
from zato.common.alerting.explain.settings_info import settings_lines, Off, On
from zato.common.alerting.object_config import alert_type_mllp_outgoing
from zato.common.api import GENERIC, HL7
from zato.common.odb.model import GenericConn
from zato.common.util.sql import parse_instance_opaque_attr

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.typing_ import anylist, stranydict
    anylist = anylist
    SASession = SASession
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

# What the Type line of the connection reads as
_type_label = 'MLLP outgoing connection'

# The stored fields whose absence means the connection was saved before the field existed, and what they read as then
_defaults = {
    'pool_size': HL7.Default.pool_size,
    'max_wait_time': HL7.Default.max_wait_time,
    'max_retries': HL7.Default.max_retries,
    'backoff_base_seconds': HL7.Default.backoff_base_seconds,
    'backoff_cap_seconds': HL7.Default.backoff_cap_seconds,
    'circuit_breaker_threshold_percent': HL7.Default.circuit_breaker_threshold_percent,
    'circuit_breaker_window_seconds': HL7.Default.circuit_breaker_window_seconds,
    'circuit_breaker_reset_seconds': HL7.Default.circuit_breaker_reset_seconds,
    'tls_ca_path': '',
    'is_audit_log_active': True,
}

# ################################################################################################################################
# ################################################################################################################################

def _stored_value(opaque:'stranydict', name:'str') -> 'object':
    """ One stored field of the connection, at the field's default when the connection was saved before the field existed.
    """
    if name in opaque:
        out = opaque[name]
    else:
        out = _defaults[name]

    return out

# ################################################################################################################################

def describe_mllp_outgoing(session:'SASession', cluster_id:'int', name:'str') -> 'anylist | None':
    """ The label and value pairs describing one outgoing MLLP connection - where it sends, whether over TLS,
    how many connections it keeps open, how long it waits for an acknowledgment, how a failed send is retried
    and when sending pauses, whether its audit log is on and the alert thresholds it sets of its own.
    None when no outgoing MLLP connection goes by the name in the cluster.
    """
    row = session.query(GenericConn).\
        filter(GenericConn.cluster_id==cluster_id).\
        filter(GenericConn.type_==GENERIC.CONNECTION.TYPE.OUTCONN_HL7_MLLP).\
        filter(GenericConn.name==name).\
        first()

    if row is None:
        return None

    opaque = parse_instance_opaque_attr(row)

    # Our response to produce
    out:'anylist' = []

    out.append(('Name', row.name))
    out.append(('Type', _type_label))
    out.append(('Active', 'yes' if row.is_active else 'no'))
    out.append(('Address', row.address))

    # TLS is keyed off the CA bundle alone - a connection with one verifies the remote system's certificate against it
    is_tls = bool(_stored_value(opaque, 'tls_ca_path'))
    out.append(('TLS', On if is_tls else Off))

    out.append(('Connections kept open', row.pool_size))
    out.append(('Ack wait', f'{_stored_value(opaque, "max_wait_time")}s'))

    max_retries = _stored_value(opaque, 'max_retries')
    backoff_base = _stored_value(opaque, 'backoff_base_seconds')
    backoff_cap = _stored_value(opaque, 'backoff_cap_seconds')
    out.append(('Retries', f'{max_retries}, backing off from {backoff_base}s up to {backoff_cap}s'))

    breaker_threshold = _stored_value(opaque, 'circuit_breaker_threshold_percent')
    breaker_window = _stored_value(opaque, 'circuit_breaker_window_seconds')
    breaker_reset = _stored_value(opaque, 'circuit_breaker_reset_seconds')
    out.append(('Sending pauses', f'at {breaker_threshold}% failures in {breaker_window}s, for {breaker_reset}s'))

    # The alerts read the audit log, so a connection with it off has nothing for them to count
    is_audit_log_active = _stored_value(opaque, 'is_audit_log_active') is True
    out.append(('Audit log', On if is_audit_log_active else Off))

    out.extend(settings_lines(alert_type_mllp_outgoing, opaque))

    return out

# ################################################################################################################################
# ################################################################################################################################
