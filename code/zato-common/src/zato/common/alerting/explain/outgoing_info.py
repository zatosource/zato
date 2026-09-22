# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The Object section of an outgoing REST or SOAP connection's evidence - what the connection is, read off the ODB
# as a channel's is, so the model reads where the calls went before it reads how they failed. Secrets never
# appear, a security definition is named by its name and type alone. A health check's alert reads the same
# Object, because the check calls the same address, and says how often the check runs.

from __future__ import annotations

# Zato
from zato.common.alerting.explain.settings_info import queue_lines, settings_lines, Off, On
from zato.common.alerting.object_config import get_alert_type, transport_by_outgoing_source
from zato.common.api import CONNECTION, HTTP_SOAP, Sec_Def_Type_Name, URL_TYPE
from zato.common.odb.model import HTTPSOAP
from zato.common.util.api import pluralize
from zato.common.util.sql import parse_instance_opaque_attr

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.typing_ import anydict, anylist
    anydict = anydict
    anylist = anylist
    SASession = SASession

# ################################################################################################################################
# ################################################################################################################################

_retry = HTTP_SOAP.Retry
_health_check = HTTP_SOAP.HealthCheck

# What a connection says of a security definition it has none of
_none = 'None'

# What a connection with no ping method of its own pings with
_default_ping_method = 'HEAD'

# What the Object says of a connection with no health check
_no_health_check = 'off'

# What each transport is called in the Object section
_transport_label_by_transport = {
    URL_TYPE.PLAIN_HTTP: 'REST',
    URL_TYPE.SOAP: 'SOAP',
}

# The scheduler names a health check's unit in the plural, and the Object reads a count with the singular
_unit_singular = {
    'seconds': 'second',
    'minutes': 'minute',
    'hours': 'hour',
    'days': 'day',
}

# ################################################################################################################################
# ################################################################################################################################

def health_check_line(opaque:'anydict') -> 'str':
    """ How often the connection's health check runs - `every 5 minutes` - or that it has none.
    """
    if _health_check.Field_Run_Every not in opaque:
        return _no_health_check

    run_every = opaque[_health_check.Field_Run_Every]

    if not run_every:
        return _no_health_check

    unit = _unit_singular[opaque[_health_check.Field_Run_Unit]]
    out = 'every ' + pluralize(run_every, unit)

    return out

# ################################################################################################################################

def describe_outgoing_http(session:'SASession', cluster_id:'int', source:'str', name:'str') -> 'anylist | None':
    """ The label and value pairs describing one outgoing REST or SOAP connection - its transport, address,
    method, timeout, pool size, whether TLS is validated, its security definition, how it retries, whether its
    audit log is on, how often its health check runs and the alert thresholds it sets of its own. The source
    is the connection's own traffic or its health check, and says which transport's row to read.
    None when no outgoing connection of that transport goes by the name in the cluster.
    """
    transport = transport_by_outgoing_source[source]

    row = session.query(HTTPSOAP).\
        filter(HTTPSOAP.cluster_id==cluster_id).\
        filter(HTTPSOAP.connection==CONNECTION.OUTGOING).\
        filter(HTTPSOAP.transport==transport).\
        filter(HTTPSOAP.name==name).\
        first()

    if row is None:
        return None

    opaque = parse_instance_opaque_attr(row)

    # Our response to produce
    out:'anylist' = []

    out.append(('Name', row.name))
    out.append(('Transport', _transport_label_by_transport[transport]))
    out.append(('Active', 'yes' if row.is_active else 'no'))
    out.append(('Address', f'{row.host}{row.url_path}'))

    # A SOAP connection is told apart by the action it calls, and a fault arrives as a response of its own
    if transport == URL_TYPE.SOAP:
        out.append(('SOAP action', row.soap_action))
        out.append(('SOAP version', row.soap_version))

    if row.method:
        out.append(('Method', row.method))
    else:
        out.append(('Method', 'any'))

    if row.ping_method:
        out.append(('Ping method', row.ping_method))
    else:
        out.append(('Ping method', _default_ping_method))

    out.append(('Timeout', f'{row.timeout} s'))

    if row.pool_size:
        out.append(('Pool size', row.pool_size))

    # A connection created before the flag existed validates TLS, the same as one whose flag is on
    validate_tls = True
    if 'validate_tls' in opaque:
        validate_tls = opaque['validate_tls'] is True

    out.append(('TLS validation', On if validate_tls else Off))

    if row.security is None:
        out.append(('Security', _none))
    else:
        out.append(('Security', f'{row.security.name} ({Sec_Def_Type_Name[row.security.sec_type]})'))

    if row.data_format:
        out.append(('Data format', row.data_format))

    # A connection that retries says so - a retried call counts once in the measures, by its final outcome
    max_retries = _retry.Default_Max_Retries
    if _retry.Field_Max_Retries in opaque:
        max_retries = opaque[_retry.Field_Max_Retries]

    if max_retries:
        out.append(('Retries', max_retries))

    # A send the endpoint did not take waits in the connection's queue, and one the queue gave up on goes to its DLQ
    out.extend(queue_lines(opaque))

    # A connection created before the flag existed logs, the same as one whose flag is on
    is_audit_log_active = True
    if 'is_audit_log_active' in opaque:
        is_audit_log_active = opaque['is_audit_log_active'] is True

    out.append(('Audit log', On if is_audit_log_active else Off))

    out.append(('Health check', health_check_line(opaque)))

    # The settings are the ones of the row's own type - the SOAP type carries the fault codes on top of the REST ones
    out.extend(settings_lines(get_alert_type(CONNECTION.OUTGOING, transport), opaque))

    return out

# ################################################################################################################################
# ################################################################################################################################
