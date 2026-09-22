# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The alert settings lines of an object's evidence - whether its alerts are on and the thresholds it sets
# of its own, read off its stored alert_* attributes. Shared by the Object sections of the channels and of
# the outgoing REST connections, so a person reading either learns what the object was held to without
# opening its Alerts tab.

from __future__ import annotations

# Zato
from zato.common.alerting.config_map import format_size, type_fields, Kind_Size
from zato.common.alerting.object_config import field_display, from_storage, get_defaults, Email_Connection_Field, \
    Is_Active_Field, LLM_Connection_Field
from zato.common.api import HTTP_SOAP

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist, strlist
    anydict = anydict
    anylist = anylist
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

# What the yes and no of a switch read as
On = 'on'
Off = 'off'

# What an object with every alert setting at its default says of them
No_Own_Settings = 'none, the defaults apply'

# The labels of the two lines
Label_Alerts = 'Alerts'
Label_Own_Settings = 'Alert settings of its own'

# The labels of the two queue delivery switches every kind of outgoing connection that can use a queue carries
Label_Use_Queue = 'Use queue'
Label_Use_DLQ = 'Use DLQ'

_queue = HTTP_SOAP.Queue
_dlq = HTTP_SOAP.DLQ

# The settings that are not thresholds - the switch is said on its own line and the connections
# are not what an object measures
_non_threshold_fields = (Is_Active_Field, Email_Connection_Field, LLM_Connection_Field)

# What a switch reads as in the settings line
_toggle_values = {
    True: On,
    False: Off,
}

# The fields stored as bytes, whichever type they belong to - they read as a size a person can follow
_size_field_names:'set[str]' = set()

for _type_field_list in type_fields.values():
    for _field in _type_field_list:
        if _field['kind'] == Kind_Size:
            _size_field_names.add(_field['name'])

# ################################################################################################################################
# ################################################################################################################################

def format_setting(name:'str', value:'object') -> 'str':
    """ One alert setting as it reads in the settings line - its label from the shared display table,
    its value with the unit the table gives it, a switch as on or off.
    """
    label, unit = field_display[name]

    if isinstance(value, bool):
        out = f'{label} {_toggle_values[value]}'
    elif name in _size_field_names:
        out = f'{label} {format_size(value)}'
    elif unit:
        out = f'{label} {value} {unit}'
    else:
        out = f'{label} {value}'

    return out

# ################################################################################################################################

def own_settings_line(alert_type:'str', settings:'anydict') -> 'str':
    """ The thresholds an object sets of its own, the ones that differ from the defaults of its type.
    """
    defaults = get_defaults(alert_type)
    parts:'strlist' = []

    for name, default in defaults.items():

        if name in _non_threshold_fields:
            continue

        if name not in settings:
            continue

        if settings[name] == default:
            continue

        parts.append(format_setting(name, settings[name]))

    if parts:
        out = ', '.join(parts)
    else:
        out = No_Own_Settings

    return out

# ################################################################################################################################

def queue_lines(opaque:'anydict') -> 'anylist':
    """ The two lines an outgoing connection's queue delivery switches make - whether a send the receiving system
    did not take waits in the connection's queue, and whether a message the queue gave up on goes to the DLQ.
    A connection saved before the switches existed carries their defaults.
    """
    is_queue_on = _queue.Default_Use_Queue
    if _queue.Field_Use_Queue in opaque:
        is_queue_on = opaque[_queue.Field_Use_Queue] is True

    is_dlq_on = _dlq.Default_Use_DLQ
    if _dlq.Field_Use_DLQ in opaque:
        is_dlq_on = opaque[_dlq.Field_Use_DLQ] is True

    out = [
        (Label_Use_Queue, On if is_queue_on else Off),
        (Label_Use_DLQ, On if is_dlq_on else Off),
    ]
    return out

# ################################################################################################################################

def settings_lines(alert_type:'str', opaque:'anydict') -> 'anylist':
    """ The two lines an object's stored alert settings make - whether its alerts are on, when it stored the
    switch at all, and the thresholds it sets of its own.
    """

    # Our response to produce
    out:'anylist' = []

    settings = from_storage(alert_type, opaque)

    if Is_Active_Field in settings:
        out.append((Label_Alerts, On if settings[Is_Active_Field] is True else Off))

    out.append((Label_Own_Settings, own_settings_line(alert_type, settings)))

    return out

# ################################################################################################################################
# ################################################################################################################################
