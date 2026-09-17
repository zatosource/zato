# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The Object section of a REST or SOAP channel's evidence - what the channel is, read off the ODB,
# so the model reads what the channel is before it reads how it failed. Secrets never appear,
# a security definition is named by its name and type alone. The alert settings lines at its end
# are the ones explain/settings_info.py builds for every object that has an Alerts tab.

from __future__ import annotations

# Zato
from zato.common.alerting.explain.settings_info import settings_lines, Off, On
from zato.common.alerting.object_config import alert_type_channels, transport_by_channel_source, Alert_Channel_Connection
from zato.common.api import Sec_Def_Type_Name
from zato.common.audit_log.common import AuditSource
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

# What a channel says of a service or a security definition it has none of
_none = 'None'

# What the Transport line of each channel source reads as
_transport_label_by_source = {
    AuditSource.REST_Channel: 'REST',
    AuditSource.SOAP_Channel: 'SOAP',
}

# ################################################################################################################################
# ################################################################################################################################

def describe_channel(session:'SASession', cluster_id:'int', source:'str', name:'str') -> 'anylist | None':
    """ The label and value pairs describing one REST or SOAP channel - its transport, path, method, service,
    security, data format, whether its audit log is on and the alert thresholds it sets of its own, and for a
    SOAP channel its SOAP action and version. None when no channel of the source goes by the name in the cluster.
    """
    row = session.query(HTTPSOAP).\
        filter(HTTPSOAP.cluster_id==cluster_id).\
        filter(HTTPSOAP.connection==Alert_Channel_Connection).\
        filter(HTTPSOAP.transport==transport_by_channel_source[source]).\
        filter(HTTPSOAP.name==name).\
        first()

    if row is None:
        return None

    opaque = parse_instance_opaque_attr(row)

    # Our response to produce
    out:'anylist' = []

    out.append(('Name', row.name))
    out.append(('Transport', _transport_label_by_source[source]))
    out.append(('Active', 'yes' if row.is_active else 'no'))
    out.append(('URL path', row.url_path))

    # A SOAP channel is told apart from the others at its path by the action it answers to
    if source == AuditSource.SOAP_Channel:
        out.append(('SOAP action', row.soap_action))
        out.append(('SOAP version', row.soap_version))

    if row.method:
        out.append(('Method', row.method))
    else:
        out.append(('Method', 'any'))

    if row.service is None:
        out.append(('Service', _none))
    else:
        out.append(('Service', row.service.name))

    if row.security is None:
        out.append(('Security', _none))
    else:
        out.append(('Security', f'{row.security.name} ({Sec_Def_Type_Name[row.security.sec_type]})'))

    if row.data_format:
        out.append(('Data format', row.data_format))

    # A channel created before the flag existed logs, the same as one whose flag is on
    is_audit_log_active = True
    if 'is_audit_log_active' in opaque:
        is_audit_log_active = opaque['is_audit_log_active'] is True

    out.append(('Audit log', On if is_audit_log_active else Off))

    out.extend(settings_lines(alert_type_channels, opaque))

    return out

# ################################################################################################################################
# ################################################################################################################################
