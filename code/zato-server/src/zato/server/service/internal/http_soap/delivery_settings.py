# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.api import CONNECTION, URL_TYPE
from zato.common.util.delivery_config import apply_delivery_defaults, Delivery_Bool_Fields, Delivery_Field_Defaults, \
    Delivery_Fields, Delivery_Int_Fields, validate_delivery_fields
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

# The queue switch and the DLQ settings, all optional
_delivery_fields = []

for _name in Delivery_Fields:
    if _name in Delivery_Bool_Fields:
        _delivery_fields.append(Boolean('-' + _name))
    elif _name in Delivery_Int_Fields:
        _delivery_fields.append(Int('-' + _name))
    else:
        _delivery_fields.append('-' + _name)

delivery_input = tuple(_delivery_fields)

# ################################################################################################################################
# ################################################################################################################################

def has_delivery_settings(connection:'str', transport:'str') -> 'bool':
    """ Whether an object of this kind has delivery settings.
    """
    if connection != CONNECTION.OUTGOING:
        return False

    out = transport == URL_TYPE.PLAIN_HTTP
    return out

# ################################################################################################################################

def prepare_delivery_settings(service:'AdminService', input:'Bunch', skip_opaque:'anylist', stored:'strdict') -> 'None':
    """ Fills in and validates the delivery settings of the object being written.
    """
    if not has_delivery_settings(input.connection, input.transport):
        skip_opaque.extend(Delivery_Fields)
        return

    for name, default in Delivery_Field_Defaults.items():

        if input.get(name) is not None:
            continue

        if name in stored:
            input[name] = stored[name]
        else:
            input[name] = default

    try:
        validate_delivery_fields(input)
    except ValueError as e:
        raise BadRequest(service.cid, str(e))

# ################################################################################################################################

def apply_delivery_list_defaults(item:'strdict') -> 'None':
    """ Fills in the delivery defaults of an outgoing REST connection in a list.
    """
    if has_delivery_settings(item['connection'], item['transport']):
        apply_delivery_defaults(item)

# ################################################################################################################################
# ################################################################################################################################
