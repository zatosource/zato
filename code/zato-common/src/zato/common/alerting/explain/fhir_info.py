# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The Object section of an outgoing FHIR connection's evidence - what the connection is, read off the ODB as an
# outgoing REST connection's is, so the model reads where the calls went before it reads how they failed. Secrets
# never appear, a security definition is named by its name and type alone. A health check's alert reads the same
# Object, because the check reads the same server's CapabilityStatement, and says how often the check runs.

from __future__ import annotations

# Zato
from zato.common.alerting.explain.outgoing_info import health_check_line
from zato.common.alerting.explain.settings_info import queue_lines, settings_lines, Off, On
from zato.common.alerting.object_config import alert_type_fhir
from zato.common.api import GENERIC, Sec_Def_Type_Name
from zato.common.odb.model import GenericConn, SecurityBase
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

# What a connection says of a security definition it has none of
_none = 'None'

# ################################################################################################################################
# ################################################################################################################################

def _security_line(session:'SASession', cluster_id:'int', security_id:'int') -> 'str':
    """ The name and type of the security definition the connection authenticates with - `Basic Auth`
    or `Bearer token` - or that it has none, a definition deleted since the connection was saved reading as none too.
    """
    if not security_id:
        return _none

    sec_def = session.query(SecurityBase).\
        filter(SecurityBase.cluster_id==cluster_id).\
        filter(SecurityBase.id==security_id).\
        first()

    if sec_def is None:
        return _none

    out = f'{sec_def.name} ({Sec_Def_Type_Name[sec_def.sec_type]})'
    return out

# ################################################################################################################################

def describe_outgoing_fhir(session:'SASession', cluster_id:'int', name:'str') -> 'anylist | None':
    """ The label and value pairs describing one outgoing FHIR connection - its address, pool size, its security
    definition, whether its audit log is on, how often its health check runs and the alert thresholds it sets
    of its own. None when no outgoing FHIR connection goes by the name in the cluster.
    """
    row = session.query(GenericConn).\
        filter(GenericConn.cluster_id==cluster_id).\
        filter(GenericConn.type_==GENERIC.CONNECTION.TYPE.OUTCONN_HL7_FHIR).\
        filter(GenericConn.name==name).\
        first()

    if row is None:
        return None

    opaque = parse_instance_opaque_attr(row)

    # Our response to produce
    out:'anylist' = []

    out.append(('Name', row.name))
    out.append(('Type', 'FHIR'))
    out.append(('Active', 'yes' if row.is_active else 'no'))
    out.append(('Address', row.address))

    if row.pool_size:
        out.append(('Pool size', row.pool_size))

    # The security definition is stored by its id alone, so its name and type are read off its own row
    security_id = 0
    if 'security_id' in opaque:
        if isinstance(opaque['security_id'], int):
            security_id = opaque['security_id']

    out.append(('Security', _security_line(session, cluster_id, security_id)))

    # A save the server did not take waits in the connection's queue, and one the queue gave up on goes to its DLQ
    out.extend(queue_lines(opaque))

    # A connection created before the flag existed logs, the same as one whose flag is on
    is_audit_log_active = True
    if 'is_audit_log_active' in opaque:
        is_audit_log_active = opaque['is_audit_log_active'] is True

    out.append(('Audit log', On if is_audit_log_active else Off))

    out.append(('Health check', health_check_line(opaque)))

    # The settings are the FHIR type's - the outcome codes on top of the REST ones
    out.extend(settings_lines(alert_type_fhir, opaque))

    return out

# ################################################################################################################################
# ################################################################################################################################
