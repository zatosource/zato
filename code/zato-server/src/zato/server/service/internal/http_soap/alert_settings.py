# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.alerting import config_map
from zato.common.alerting.fault_codes import parse_fault_codes
from zato.common.alerting.object_config import alert_type_by_http_soap, alert_type_channels, alert_type_soap, \
    alert_types_outgoing_http, apply_defaults, get_alert_type, get_defaults, get_field_kinds, get_field_names, storage_name, \
    Kind_Active
from zato.common.alerting.status_codes import parse_status_codes
from zato.common.alerting.time_slots import validate_silence_slots
from zato.server.connection.http_soap import BadRequest
from zato.server.service import Boolean, Int

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.ext.bunch import Bunch
    from zato.common.typing_ import anylist, strdict
    from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

# The alert settings a REST or SOAP channel and an outgoing REST or SOAP connection carry, under their storage names -
# the switches as booleans, the numbers and the durations as integers, the rest as text, each optional so that
# a caller that knows nothing of them sends nothing. The two types share most names, and a name both have is
# of one kind in all, so the input covers the union of the types once.
alert_toggle_kinds = (Kind_Active, config_map.Kind_Toggle, config_map.Kind_Ruleset_Toggle)
alert_int_kinds = (config_map.Kind_Number, config_map.Kind_Duration)

alert_fields = []
alert_storage_names = []

# The storage names of each type's own fields - what is skipped when an object of the other type is written
alert_storage_names_by_type = {}

for _alert_type in alert_type_by_http_soap.values():

    if _alert_type in alert_storage_names_by_type:
        continue

    alert_storage_names_by_type[_alert_type] = []

    for _alert_field_name, _alert_field_kind in get_field_kinds(_alert_type).items():

        _alert_storage_name = storage_name(_alert_field_name)
        alert_storage_names_by_type[_alert_type].append(_alert_storage_name)

        if _alert_storage_name in alert_storage_names:
            continue

        alert_storage_names.append(_alert_storage_name)

        if _alert_field_kind in alert_toggle_kinds:
            alert_fields.append(Boolean('-' + _alert_storage_name))
        elif _alert_field_kind in alert_int_kinds:
            alert_fields.append(Int('-' + _alert_storage_name))
        else:
            alert_fields.append('-' + _alert_storage_name)

alert_input = tuple(alert_fields)

# The alert settings that are validated beyond their type - a channel's silence slots travel as a JSON list
# in a string, an outgoing REST or SOAP connection's status codes as a comma-separated list of codes and classes
# and an outgoing SOAP connection's fault codes as a comma-separated list of fault code names
alert_silence_slots_name = storage_name(config_map.Silence_Slots_Field_Name)
alert_status_codes_name = storage_name(config_map.Status_Codes_Field_Name)
alert_fault_codes_name = storage_name(config_map.Fault_Codes_Field_Name)

# ################################################################################################################################
# ################################################################################################################################

def prepare_alert_settings(service:'AdminService', input:'Bunch', skip_opaque:'anylist', stored:'strdict') -> 'None':
    """ The alert settings of the object being written - a REST or SOAP channel and an outgoing REST connection
    have every one of their type's, the ones the caller sent as sent, the rest as the object already stores them
    or, on a new object, at their defaults. Any other object has none, and the names of the other type are
    skipped either way when the opaque attributes are stored.
    """
    alert_type = get_alert_type(input.connection, input.transport)

    if not alert_type:
        skip_opaque.extend(alert_storage_names)
        return

    for name in alert_storage_names:
        if name not in alert_storage_names_by_type[alert_type]:
            skip_opaque.append(name)

    defaults = get_defaults(alert_type)

    for name in get_field_names(alert_type):
        key = storage_name(name)

        # A setting the caller sent stands ..
        if input.get(key) is not None:
            continue

        # .. one it did not send is what the object already stores ..
        if key in stored:
            input[key] = stored[key]

        # .. or the default when the object stores nothing yet.
        else:
            input[key] = defaults[name]

    # A slot without both ends, a bad HH:MM or a silence below the least allowed is refused here,
    # before anything is written ..
    if alert_type == alert_type_channels:
        _ = validate_silence_slots(input[alert_silence_slots_name])

    # .. and so is a status code that is neither three digits nor a class such as 5xx ..
    if alert_type in alert_types_outgoing_http:
        try:
            _ = parse_status_codes(input[alert_status_codes_name])
        except ValueError as e:
            raise BadRequest(service.cid, str(e))

    # .. and a fault code that is not a name such as Receiver or x:Timeout.
    if alert_type == alert_type_soap:
        try:
            _ = parse_fault_codes(input[alert_fault_codes_name])
        except ValueError as e:
            raise BadRequest(service.cid, str(e))


# ################################################################################################################################

def apply_list_defaults(item:'strdict') -> 'None':
    """ A channel or an outgoing REST or SOAP connection created before a setting existed reads the same
    as one created after it - the defaults fill in whatever a listed item does not carry yet.
    """
    if alert_type := get_alert_type(item['connection'], item['transport']):
        apply_defaults(alert_type, item)

# ################################################################################################################################
# ################################################################################################################################
