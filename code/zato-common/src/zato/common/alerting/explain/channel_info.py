# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The Object section of a REST channel's evidence - what the channel is, read off the ODB,
# so the model reads what the channel is before it reads how it failed. Secrets never appear,
# a security definition is named by its name and type alone.

from __future__ import annotations

# Zato
from zato.common.alerting.object_config import alert_type_channels, field_display, from_storage, get_defaults, \
    Alert_Channel_Connection, Alert_Channel_Transport, Email_Connection_Field, Is_Active_Field, LLM_Connection_Field
from zato.common.api import Sec_Def_Type_Name
from zato.common.odb.model import HTTPSOAP
from zato.common.util.sql import parse_instance_opaque_attr

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.typing_ import anylist, strlist
    anylist = anylist
    SASession = SASession
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

# What the yes and no of a switch read as
_on = 'on'
_off = 'off'

# What a channel says of a service or a security definition it has none of
_none = 'None'

# What a channel with every alert setting at its default says of them
_no_own_settings = 'none, the defaults apply'

# The settings that are not thresholds - the switch is said on its own line and the connections
# are not what a channel measures
_non_threshold_fields = (Is_Active_Field, Email_Connection_Field, LLM_Connection_Field)

# What a switch reads as in the settings line
_toggle_values = {
    True: _on,
    False: _off,
}

# ################################################################################################################################
# ################################################################################################################################

def _format_setting(name:'str', value:'object') -> 'str':
    """ One alert setting as it reads in the settings line - its label from the shared display table,
    its value with the unit the table gives it, a switch as on or off.
    """
    label, unit = field_display[name]

    if isinstance(value, bool):
        out = f'{label} {_toggle_values[value]}'
    elif unit:
        out = f'{label} {value} {unit}'
    else:
        out = f'{label} {value}'

    return out

# ################################################################################################################################

def _own_settings_line(settings:'dict') -> 'str':
    """ The thresholds a channel sets of its own, the ones that differ from the defaults - a person reading
    the evidence learns what the channel was held to without opening its Alerts tab.
    """
    defaults = get_defaults(alert_type_channels)
    parts:'strlist' = []

    for name, default in defaults.items():

        if name in _non_threshold_fields:
            continue

        if name not in settings:
            continue

        if settings[name] == default:
            continue

        parts.append(_format_setting(name, settings[name]))

    if parts:
        out = ', '.join(parts)
    else:
        out = _no_own_settings

    return out

# ################################################################################################################################

def describe_rest_channel(session:'SASession', cluster_id:'int', name:'str') -> 'anylist | None':
    """ The label and value pairs describing one REST channel - its path, method, service, security,
    data format, whether its audit log is on and the alert thresholds it sets of its own. None when
    no REST channel goes by the name in the cluster.
    """
    row = session.query(HTTPSOAP).\
        filter(HTTPSOAP.cluster_id==cluster_id).\
        filter(HTTPSOAP.connection==Alert_Channel_Connection).\
        filter(HTTPSOAP.transport==Alert_Channel_Transport).\
        filter(HTTPSOAP.name==name).\
        first()

    if row is None:
        return None

    opaque = parse_instance_opaque_attr(row)

    # Our response to produce
    out:'anylist' = []

    out.append(('Name', row.name))
    out.append(('Active', 'yes' if row.is_active else 'no'))
    out.append(('URL path', row.url_path))

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

    out.append(('Audit log', _on if is_audit_log_active else _off))

    settings = from_storage(alert_type_channels, opaque)

    if Is_Active_Field in settings:
        out.append(('Alerts', _on if settings[Is_Active_Field] is True else _off))

    out.append(('Alert settings of its own', _own_settings_line(settings)))

    return out

# ################################################################################################################################
# ################################################################################################################################
