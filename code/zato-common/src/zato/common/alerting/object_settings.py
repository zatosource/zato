# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The per-object alert settings as the sweep reads them - what an object's Alerts tab or its enmasse
# `alerts` block stored under the alert_ prefix, loaded once per sweep and turned into what the rule
# engine and the collectors take: the rule defaults an object overrides, the rules it mutes, the window
# it is measured over and the email and LLM connections its alerts leave through.

from __future__ import annotations

# Zato
from zato.common.alerting import config_map
from zato.common.alerting.object_config import apply_defaults, conn_type_to_alert_type, Email_Connection_Field, \
    from_storage, Is_Active_Field, LLM_Connection_Field
from zato.common.odb.model import GenericConn
from zato.common.util.file_transfer_scheduler import get_schedule_list
from zato.common.util.sql import parse_instance_opaque_attr

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.typing_ import anydict, stranydict, strintdict, strlist
    anydict = anydict
    SASession = SASession
    stranydict = stranydict
    strintdict = strintdict
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

def load_object_settings(session:'SASession', cluster_id:'int') -> 'anydict':
    """ The alert settings of every object whose type has them, by alert type and then by the name a fact
    about the object goes by - the connection's own name, and the name of each of its file transfer schedules,
    because the arrival, expectation and run facts are keyed by schedule, not by connection.
    An object that never stored a setting reads at the seeded defaults, the same way the Dashboard shows it.
    """

    # Our response to produce
    out:'anydict' = {}

    for alert_type in conn_type_to_alert_type.values():
        if alert_type not in out:
            out[alert_type] = {}

    conn_types = list(conn_type_to_alert_type)

    rows = session.query(GenericConn).\
        filter(GenericConn.type_.in_(conn_types)).\
        filter(GenericConn.cluster_id==cluster_id).\
        all()

    for row in rows:

        alert_type = conn_type_to_alert_type[row.type_]

        # The stored alert_* values, every missing one at its default ..
        item = dict(parse_instance_opaque_attr(row))
        apply_defaults(alert_type, item)
        values = from_storage(alert_type, item)

        # .. under the connection's name ..
        by_object = out[alert_type]
        by_object[row.name] = values

        # .. and under the name of each of its schedules.
        for schedule in get_schedule_list(session, row.id):
            by_object[schedule['name']] = values

    return out

# ################################################################################################################################

def build_rule_values(alert_type:'str', values:'stranydict') -> 'stranydict':
    """ The object's numbers under the names the rules read them by - `default.max_consecutive_failures`
    resolves against the top-level key `max_consecutive_failures` of the match data, and a key that is
    already there wins over the rule's own default.
    """

    # Our response to produce
    out:'stranydict' = {}

    for field in config_map.type_fields[alert_type]:

        # Toggles carry no number a rule reads
        if 'default' not in field:
            continue

        out[field['default']] = config_map.to_rule_value(values[field['name']], field['is_percent'])

    return out

# ################################################################################################################################

def get_muted_rule_names(alert_type:'str', values:'stranydict') -> 'strlist':
    """ The rules an object's toggles switch off for that object - a toggle that is off names
    the rules it stands for, and a fact about the object never reaches them.
    """

    # Our response to produce
    out:'strlist' = []

    for field in config_map.type_fields[alert_type]:

        if field['kind'] != config_map.Kind_Toggle:
            continue

        if values[field['name']]:
            continue

        out.extend(field['rules'])

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

def build_window_seconds_by_object(object_settings:'anydict', window_seconds_by_source:'strintdict') -> 'anydict':
    """ The measuring window of each object that has one of its own, by audit source and then by object name -
    only the objects whose window differs from their source's, because those are the ones that
    need to be measured again on their own.
    """

    # Our response to produce
    out:'anydict' = {}

    for alert_type, by_object in object_settings.items():

        # The type's duration field, if it has one
        window_field_name = ''

        for field in config_map.type_fields[alert_type]:
            if field['kind'] == config_map.Kind_Duration:
                window_field_name = field['name']
                break

        if not window_field_name:
            continue

        for source in config_map.type_sources[alert_type]:

            if source in window_seconds_by_source:
                source_window = window_seconds_by_source[source]
            else:
                source_window = None

            for object_name, values in by_object.items():

                window = values[window_field_name]

                # An object measured over the source's window has nothing of its own to be measured over
                if window == source_window:
                    continue

                if source not in out:
                    out[source] = {}

                out[source][object_name] = window

    return out

# ################################################################################################################################
# ################################################################################################################################
