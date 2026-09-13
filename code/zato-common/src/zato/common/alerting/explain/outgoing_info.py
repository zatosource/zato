# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The Object section of an outgoing REST connection's evidence - what the connection is, read off the ODB
# as a channel's is, so the model reads where the calls went before it reads how they failed. Secrets never
# appear, a security definition is named by its name and type alone. A health check's alert reads the same
# Object, because the check calls the same address.

from __future__ import annotations

# Zato
from zato.common.alerting.explain.settings_info import settings_lines, Off, On
from zato.common.alerting.object_config import alert_type_rest
from zato.common.api import CONNECTION, HTTP_SOAP, Sec_Def_Type_Name, URL_TYPE
from zato.common.odb.model import HTTPSOAP
from zato.common.util.sql import parse_instance_opaque_attr

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.typing_ import anylist
    anylist = anylist
    SASession = SASession

# ################################################################################################################################
# ################################################################################################################################

_retry = HTTP_SOAP.Retry

# What a connection says of a security definition it has none of
_none = 'None'

# What a connection with no ping method of its own pings with
_default_ping_method = 'HEAD'

# ################################################################################################################################
# ################################################################################################################################

def describe_outgoing_rest(session:'SASession', cluster_id:'int', name:'str') -> 'anylist | None':
    """ The label and value pairs describing one outgoing REST connection - its address, method, timeout,
    pool size, whether TLS is validated, its security definition, how it retries, whether its audit log is on
    and the alert thresholds it sets of its own. None when no outgoing REST connection goes by the name in the cluster.
    """
    row = session.query(HTTPSOAP).\
        filter(HTTPSOAP.cluster_id==cluster_id).\
        filter(HTTPSOAP.connection==CONNECTION.OUTGOING).\
        filter(HTTPSOAP.transport==URL_TYPE.PLAIN_HTTP).\
        filter(HTTPSOAP.name==name).\
        first()

    if row is None:
        return None

    opaque = parse_instance_opaque_attr(row)

    # Our response to produce
    out:'anylist' = []

    out.append(('Name', row.name))
    out.append(('Active', 'yes' if row.is_active else 'no'))
    out.append(('Address', f'{row.host}{row.url_path}'))

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

    # A connection created before the flag existed logs, the same as one whose flag is on
    is_audit_log_active = True
    if 'is_audit_log_active' in opaque:
        is_audit_log_active = opaque['is_audit_log_active'] is True

    out.append(('Audit log', On if is_audit_log_active else Off))

    out.extend(settings_lines(alert_type_rest, opaque))

    return out

# ################################################################################################################################
# ################################################################################################################################
