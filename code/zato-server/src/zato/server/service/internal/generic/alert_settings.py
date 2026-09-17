# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The alert settings of a generic connection whose type alerts - an outgoing FHIR connection today - as the
# generic Create and Edit write them. The twin of prepare_alert_settings for HTTPSOAP objects - the settings
# ride in the opaque attributes under their storage names, the ones the caller sent stand, the rest come from
# what the row already stores or from the type's defaults, and a text setting that does not parse is refused
# before anything is written.

# Zato
from zato.common.alerting import config_map
from zato.common.alerting.ack_codes import parse_ack_codes
from zato.common.alerting.fault_codes import parse_fault_codes
from zato.common.alerting.object_config import conn_type_to_alert_type, from_storage, get_defaults, get_field_names, \
    storage_name
from zato.common.alerting.outcome_codes import parse_outcome_codes
from zato.common.alerting.status_codes import parse_status_codes
from zato.common.alerting.time_slots import validate_silence_slots
from zato.common.alerting.validate_numbers import validate_number_settings
from zato.server.connection.http_soap import BadRequest

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, callable_, strdict
    from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

# The text settings that are parsed before they are stored, each by the parser of its own syntax
_parsers:'dict[str, callable_]' = {
    config_map.Status_Codes_Field_Name: parse_status_codes,
    config_map.Fault_Codes_Field_Name: parse_fault_codes,
    config_map.Outcome_Codes_Field_Name: parse_outcome_codes,
    config_map.Ack_Codes_Field_Name: parse_ack_codes,
}

# ################################################################################################################################
# ################################################################################################################################

def prepare_generic_alert_settings(service:'AdminService', conn_type:'str', data:'anydict', stored:'strdict') -> 'anydict':
    """ The alert settings of the generic connection being written, under their storage names - every one of its
    type's, the ones the caller sent as sent, the rest as the row already stores them or, on a new row, at their
    defaults. A connection of a type that does not alert has none, and the result is empty.
    """

    # Our response to produce
    out:'anydict' = {}

    if conn_type not in conn_type_to_alert_type:
        return out

    alert_type = conn_type_to_alert_type[conn_type]
    defaults = get_defaults(alert_type)
    field_names = get_field_names(alert_type)

    for name in field_names:
        key = storage_name(name)

        # A setting the caller sent stands ..
        if data.get(key) is not None:
            out[key] = data[key]

        # .. one it did not send is what the row already stores ..
        elif key in stored:
            out[key] = stored[key]

        # .. or the default when the row stores nothing yet.
        else:
            out[key] = defaults[name]

    # A slot without both ends, a bad HH:MM or a silence below the least allowed is refused here,
    # before anything is written ..
    if config_map.Silence_Slots_Field_Name in field_names:
        _ = validate_silence_slots(out[storage_name(config_map.Silence_Slots_Field_Name)])

    # .. so is a status code that is neither three digits nor a class such as 5xx, a fault code
    # .. that is not a name such as Receiver and an outcome code that is not one such as not-found ..
    for name, parser in _parsers.items():
        if name in field_names:
            try:
                _ = parser(out[storage_name(name)])
            except ValueError as e:
                raise BadRequest(service.cid, str(e))

    # .. and so is a threshold that is not a number or is negative.
    try:
        validate_number_settings(alert_type, from_storage(alert_type, out))
    except ValueError as e:
        raise BadRequest(service.cid, str(e))

    return out

# ################################################################################################################################
# ################################################################################################################################
