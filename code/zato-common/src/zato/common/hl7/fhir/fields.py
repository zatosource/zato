# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.api import HL7, HTTP_SOAP
from zato.common.hl7.fields import ConnectionField, field_list, get_bool_names, get_column_defaults, get_defaults, \
    get_int_names, get_names, get_opaque_defaults

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strlist, strtuple

    strobjectdict = dict[str, object]

    # Add dummy assignments to satisfy type checkers
    strlist = strlist
    strtuple = strtuple

# ################################################################################################################################
# ################################################################################################################################

FHIRField = ConnectionField
fhir_field_list = field_list

_retry = HTTP_SOAP.Retry
_queue = HTTP_SOAP.Queue
_dlq = HTTP_SOAP.DLQ

# ################################################################################################################################
# ################################################################################################################################

# Every field an outgoing FHIR connection carries, in the order the Dashboard and enmasse present them.
Outgoing_Fields:'fhir_field_list' = [

    FHIRField('is_active', True, is_column=True),
    FHIRField('pool_size', HL7.Default.pool_size, is_column=True),

    # The security definition the connection authenticates with.
    FHIRField('security_id', 0),

    FHIRField('is_audit_log_active', True),

    # How a send that did not go through is tried again - the same settings an outgoing REST connection has.
    FHIRField(_retry.Field_Max_Retries, _retry.Default_Max_Retries),
    FHIRField(_retry.Field_Sleep_Time, _retry.Default_Sleep_Time),
    FHIRField(_retry.Field_Backoff_Threshold, _retry.Default_Backoff_Threshold),
    FHIRField(_retry.Field_Backoff_Multiplier, _retry.Default_Backoff_Multiplier),

    # Whether a send that did not go through waits in the connection's queue, and what its DLQ does.
    FHIRField(_queue.Field_Use_Queue, _queue.Default_Use_Queue),
    FHIRField(_dlq.Field_Use_DLQ, _dlq.Default_Use_DLQ),
    FHIRField(_dlq.Field_Action, _dlq.Default_Action),
    FHIRField(_dlq.Field_Retries, _dlq.Default_Retries),
    FHIRField(_dlq.Field_Retry_Interval, _dlq.Default_Retry_Interval),
    FHIRField(_dlq.Field_Forward_To, _dlq.Default_Forward_To),
    FHIRField(_dlq.Field_Keep_Header, _dlq.Default_Keep_Header),
]

# ################################################################################################################################
# ################################################################################################################################

Outgoing_Column_Defaults = get_column_defaults(Outgoing_Fields)
Outgoing_Opaque_Defaults = get_opaque_defaults(Outgoing_Fields)
Outgoing_Defaults        = get_defaults(Outgoing_Fields)
Outgoing_Int_Names       = get_int_names(Outgoing_Fields)
Outgoing_Bool_Names      = get_bool_names(Outgoing_Fields)
Outgoing_Names           = get_names(Outgoing_Fields)

# ################################################################################################################################
# ################################################################################################################################

# What the connection authenticates with.
Outgoing_Auth_Defaults:'strobjectdict' = {
    'auth_type': HL7.Const.FHIR_Auth_Type.No_Auth.id,
    'username': '',
    'secret': '',
}

# Everything the config manager fills in when the create path does not supply it.
Outgoing_Config_Defaults:'strobjectdict' = dict(Outgoing_Defaults, **Outgoing_Auth_Defaults)

# ################################################################################################################################
# ################################################################################################################################

# What enmasse names a connection's security definition by.
Outgoing_Security_Id_Key   = 'security_id'
Outgoing_Security_Name_Key = 'security'

# ################################################################################################################################

def get_enmasse_outgoing_names() -> 'strtuple':
    """ The outgoing field names as enmasse presents them, which is every stored field except that
    the security definition appears under the name YAML refers to it by.
    """
    names:'strlist' = []

    for name in Outgoing_Names:

        if name == Outgoing_Security_Id_Key:
            names.append(Outgoing_Security_Name_Key)
        else:
            names.append(name)

    out = tuple(names)
    return out

# ################################################################################################################################

Outgoing_Enmasse_Names = get_enmasse_outgoing_names()

# ################################################################################################################################
# ################################################################################################################################
