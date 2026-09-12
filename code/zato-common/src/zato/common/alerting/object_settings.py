# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The per-object alert settings as the sweep reads them - what an object's Alerts tab or its enmasse
# `alerts` block stored under the alert_ prefix, loaded once per sweep and turned into what the rule
# engine and the collectors take: the rule defaults an object overrides, the rules it mutes, the windows
# its measures are taken over and the email and LLM connections its alerts leave through.

from __future__ import annotations

# Zato
from zato.common.alerting import config_map
from zato.common.alerting.object_config import alert_type_channels, apply_defaults, conn_type_to_alert_type, \
    from_storage, is_alert_channel, Email_Connection_Field, Is_Active_Field, LLM_Connection_Field
from zato.common.alerting.time_slots import resolve_silence
from zato.common.audit_log.common import AuditSource
from zato.common.odb.model import GenericConn, HTTPSOAP
from zato.common.util.file_transfer_scheduler import get_schedule_list
from zato.common.util.sql import parse_instance_opaque_attr

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.typing_ import anydict, stranydict, strlist, strset
    anydict = anydict
    datetime = datetime
    SASession = SASession
    stranydict = stranydict
    strlist = strlist
    strset = strset

# ################################################################################################################################
# ################################################################################################################################

# The rules the silence slot of the moment speaks for, and the default it hands its seconds to
_silence_rules = ['Channel_Silent']
_silence_default = 'silence_seconds'

# The audit sources whose objects carry settings of a type, where that is not every source the type
# matches on - the channels type matches on three channel kinds, and REST channels alone have an Alerts tab.
_object_sources_by_type = {
    alert_type_channels: [AuditSource.REST_Channel],
}

# ################################################################################################################################
# ################################################################################################################################

def _settings_from_item(alert_type:'str', item:'anydict') -> 'stranydict':
    """ The alert settings of one stored object under their own names, every one it never stored at its default.
    """
    apply_defaults(alert_type, item)
    out = from_storage(alert_type, item)
    return out

# ################################################################################################################################

def load_object_settings(session:'SASession', cluster_id:'int') -> 'anydict':
    """ The alert settings of every object whose type has them, by alert type and then by the name a fact
    about the object goes by - a connection's own name, and the name of each of its file transfer schedules,
    because the arrival, expectation and run facts are keyed by schedule, not by connection, and a REST
    channel's own name. An object that never stored a setting reads at the seeded defaults, the same way
    the Dashboard shows it.
    """

    # Our response to produce
    out:'anydict' = {}

    for alert_type in conn_type_to_alert_type.values():
        if alert_type not in out:
            out[alert_type] = {}

    out[alert_type_channels] = {}

    conn_types = list(conn_type_to_alert_type)

    rows = session.query(GenericConn).\
        filter(GenericConn.type_.in_(conn_types)).\
        filter(GenericConn.cluster_id==cluster_id).\
        all()

    for row in rows:

        alert_type = conn_type_to_alert_type[row.type_]

        # The stored alert_* values, every missing one at its default ..
        item = dict(parse_instance_opaque_attr(row))
        values = _settings_from_item(alert_type, item)

        # .. under the connection's name ..
        by_object = out[alert_type]
        by_object[row.name] = values

        # .. and under the name of each of its schedules.
        for schedule in get_schedule_list(session, row.id):
            by_object[schedule['name']] = values

    # The REST channels carry their settings in the same flat keys, in their own table
    channel_rows = session.query(HTTPSOAP).\
        filter(HTTPSOAP.cluster_id==cluster_id).\
        all()

    by_channel = out[alert_type_channels]

    for channel_row in channel_rows:

        if not is_alert_channel(channel_row.connection, channel_row.transport):
            continue

        item = dict(parse_instance_opaque_attr(channel_row))
        by_channel[channel_row.name] = _settings_from_item(alert_type_channels, item)

    return out

# ################################################################################################################################

def build_rule_values(
    alert_type:'str',
    values:'stranydict',
    now:'datetime | None' = None,
    rule_name:'str' = '',
    ) -> 'stranydict':
    """ The object's numbers under the names the rules read them by - `default.max_consecutive_failures`
    resolves against the top-level key `max_consecutive_failures` of the match data, and a key that is
    already there wins over the rule's own default. Two fields may hand their numbers to one default name,
    each for rules of its own - a channel's five windows are all a `window_seconds` - and the field tied
    to the rule being matched is the one that speaks then, the first one when no rule is named.
    A channel's silence is the one of the time slot containing the moment, so the moment is needed to read it.
    """

    # Our response to produce
    out:'stranydict' = {}

    for field in config_map.type_fields[alert_type]:

        # Toggles carry no number a rule reads
        if 'default' not in field:
            continue

        default_name = field['default']

        # A default another field named already is taken over by the field of the rule being matched alone
        if default_name in out:
            if rule_name not in field['rules']:
                continue

        out[default_name] = config_map.to_rule_value(values[field['name']], field['is_percent'])

    # The silence slot of the moment says how long a channel may stay silent right now
    if alert_type == alert_type_channels:
        if now is not None:
            out[_silence_default] = resolve_silence(values, now).seconds

    return out

# ################################################################################################################################

def get_muted_rule_names(alert_type:'str', values:'stranydict', now:'datetime | None'=None) -> 'strlist':
    """ The rules an object's toggles switch off for that object - a toggle that is off names
    the rules it stands for, and a fact about the object never reaches them. A channel's silence
    switch is the one of the time slot containing the moment.
    """

    # Our response to produce
    out:'strlist' = []

    for field in config_map.type_fields[alert_type]:

        if field['kind'] != config_map.Kind_Toggle:
            continue

        if values[field['name']]:
            continue

        out.extend(field['rules'])

    if alert_type == alert_type_channels:
        if now is not None:

            # The slot of the moment decides, whatever the all-day switch says ..
            for rule_name in _silence_rules:
                if rule_name in out:
                    out.remove(rule_name)

            # .. and a slot switched off mutes the silence rule for this sweep alone.
            if not resolve_silence(values, now).is_on:
                out.extend(_silence_rules)

    return out

# ################################################################################################################################

def is_object_active(values:'stranydict') -> 'bool':
    """ Whether alerts are raised for the object at all.
    """
    out = values[Is_Active_Field] is True
    return out

# ################################################################################################################################

def get_email_connection(values:'stranydict') -> 'str':
    """ The encoded email connection an object's alerts leave through, empty when it has none of its own.
    """
    out = values[Email_Connection_Field]
    return out

# ################################################################################################################################

def get_llm_connection(values:'stranydict') -> 'str':
    """ The LLM connection that explains an object's alerts, empty when it has none of its own.
    """
    out = values[LLM_Connection_Field]
    return out

# ################################################################################################################################

def get_names_with_toggle(settings_by_object:'anydict', toggle_name:'str') -> 'strset':
    """ The objects whose given toggle is on.
    """

    # Our response to produce
    out:'strset' = set()

    for object_name, values in settings_by_object.items():
        if values[toggle_name] is True:
            out.add(object_name)

    return out

# ################################################################################################################################

def get_silence_expected_names(object_settings:'anydict', now:'datetime') -> 'strset':
    """ The active REST channels whose silence slot of the moment says traffic is expected -
    the ones the silence collector measures in this sweep.
    """

    # Our response to produce
    out:'strset' = set()

    if alert_type_channels not in object_settings:
        return out

    for object_name, values in object_settings[alert_type_channels].items():

        if not is_object_active(values):
            continue

        if resolve_silence(values, now).is_on:
            out.add(object_name)

    return out

# ################################################################################################################################

def build_window_seconds_by_object(object_settings:'anydict', window_seconds_by_source:'anydict') -> 'anydict':
    """ The measuring window of each measure of each object that has one of its own, by audit source, then by
    object name and then by measure - only the windows that differ from the source's own for that measure,
    because those are the ones that need to be measured again on their own.
    """

    # Our response to produce
    out:'anydict' = {}

    for alert_type, by_object in object_settings.items():

        # The type's duration fields, each with the measures it drives
        window_fields = []

        for field in config_map.type_fields[alert_type]:
            if field['kind'] == config_map.Kind_Duration:
                window_fields.append(field)

        if not window_fields:
            continue

        if alert_type in _object_sources_by_type:
            object_sources = _object_sources_by_type[alert_type]
        else:
            object_sources = config_map.type_sources[alert_type]

        for source in object_sources:

            if source in window_seconds_by_source:
                source_windows = window_seconds_by_source[source]
            else:
                source_windows = {}

            for object_name, values in by_object.items():

                for field in window_fields:

                    window = values[field['name']]

                    for measure in field[config_map.Measures_Key]:

                        # An object measured over the source's window has nothing of its own to be measured over
                        if measure in source_windows:
                            if window == source_windows[measure]:
                                continue

                        if source not in out:
                            out[source] = {}

                        if object_name not in out[source]:
                            out[source][object_name] = {}

                        out[source][object_name][measure] = window

    return out

# ################################################################################################################################
# ################################################################################################################################
