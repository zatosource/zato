# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.api import HL7
from zato.common.hl7.fields import ConnectionField, field_list, get_column_defaults, get_defaults, get_int_names, \
    get_names, get_opaque_defaults

# ################################################################################################################################
# ################################################################################################################################

FHIRField = ConnectionField
fhir_field_list = field_list

# ################################################################################################################################
# ################################################################################################################################

# Every field an outgoing FHIR connection carries, in the order the Dashboard and enmasse present them.
# Name and address are not here because they are required rather than defaulted.
Outconn_Fields:'fhir_field_list' = [

    FHIRField('is_active', True, is_column=True),
    FHIRField('pool_size', HL7.Default.pool_size, is_column=True),

    # Which definition the connection authenticates with - none of its own means the requests go out unauthenticated
    FHIRField('security_id', 0),

    # Audit - off unless turned on per connection
    FHIRField('is_audit_log_active', False),
]

# ################################################################################################################################
# ################################################################################################################################

Outconn_Column_Defaults = get_column_defaults(Outconn_Fields)
Outconn_Opaque_Defaults = get_opaque_defaults(Outconn_Fields)
Outconn_Defaults        = get_defaults(Outconn_Fields)
Outconn_Int_Names       = get_int_names(Outconn_Fields)
Outconn_Names           = get_names(Outconn_Fields)

# ################################################################################################################################
# ################################################################################################################################

# What the connection authenticates with, worked out from the security definition each time the
# connection's config is normalized rather than stored, which is why these are not fields of their own.
Outconn_Auth_Defaults:'dict[str, object]' = {
    'auth_type': HL7.Const.FHIR_Auth_Type.No_Auth.id,
    'username': '',
    'secret': '',
}

# Everything the config manager fills in when the create path does not supply it
Outconn_Config_Defaults:'dict[str, object]' = dict(Outconn_Defaults, **Outconn_Auth_Defaults)

# ################################################################################################################################
# ################################################################################################################################

# What enmasse names a connection's security definition by. The id is what a connection stores, but an id
# means nothing in another environment, so YAML carries the definition's name in its place.
Outconn_Security_Id_Key   = 'security_id'
Outconn_Security_Name_Key = 'security'

# ################################################################################################################################

def get_enmasse_outconn_names() -> 'tuple':
    """ The outgoing field names as enmasse presents them, which is every stored field except that
    the security definition appears under the name YAML refers to it by.
    """
    names = []

    for name in Outconn_Names:

        if name == Outconn_Security_Id_Key:
            names.append(Outconn_Security_Name_Key)
        else:
            names.append(name)

    out = tuple(names)
    return out

# ################################################################################################################################

Outconn_Enmasse_Names = get_enmasse_outconn_names()

# ################################################################################################################################
# ################################################################################################################################
