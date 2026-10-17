# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.api import CONNECTION, HTTP_SOAP, URL_TYPE
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

_queue = HTTP_SOAP.Queue

# The queue switch and the DLQ settings, all optional
_delivery_fields = []

for _name in Delivery_Fields:
    if _name in Delivery_Bool_Fields:
        _delivery_fields.append(Boolean('-' + _name))
    elif _name in Delivery_Int_Fields:
        _delivery_fields.append(Int('-' + _name))
    else:
        _delivery_fields.append('-' + _name)

# The static response of a channel with the queue on travels next to the delivery settings
_delivery_fields.append('-' + _queue.Field_Queue_Response)

delivery_input = tuple(_delivery_fields)

# Outgoing REST and SOAP connections have a queue and a DLQ, and so do REST and SOAP channels
_transports_with_delivery_settings = (URL_TYPE.PLAIN_HTTP, URL_TYPE.SOAP)
_connections_with_delivery_settings = (CONNECTION.OUTGOING, CONNECTION.CHANNEL)

# ################################################################################################################################
# ################################################################################################################################

def has_delivery_settings(connection:'str', transport:'str') -> 'bool':
    """ Whether an object of this kind has delivery settings.
    """
    if connection not in _connections_with_delivery_settings:
        return False

    out = transport in _transports_with_delivery_settings
    return out

# ################################################################################################################################

def has_queue_response(connection:'str', transport:'str') -> 'bool':
    """ Whether an object of this kind has a static queue response - only a channel with delivery settings does.
    """
    if connection != CONNECTION.CHANNEL:
        return False

    out = has_delivery_settings(connection, transport)
    return out

# ################################################################################################################################

def prepare_delivery_settings(service:'AdminService', input:'Bunch', skip_opaque:'anylist', stored:'strdict') -> 'None':
    """ Fills in and validates the delivery settings of the object being written.
    """
    if not has_delivery_settings(input.connection, input.transport):
        skip_opaque.extend(Delivery_Fields)
        skip_opaque.append(_queue.Field_Queue_Response)
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

    _prepare_queue_response(input, skip_opaque, stored)

# ################################################################################################################################

def _prepare_queue_response(input:'Bunch', skip_opaque:'anylist', stored:'strdict') -> 'None':
    """ Fills in the static queue response of a channel - a caller that sent none keeps what is stored.
    """
    name = _queue.Field_Queue_Response

    if not has_queue_response(input.connection, input.transport):
        skip_opaque.append(name)
        return

    if input.get(name) is not None:
        return

    if name in stored:
        input[name] = stored[name]
    else:
        input[name] = _queue.Default_Queue_Response

# ################################################################################################################################

def apply_delivery_list_defaults(item:'strdict') -> 'None':
    """ Fills in the delivery defaults of a REST or SOAP channel or outgoing connection in a list.
    """
    if has_delivery_settings(item['connection'], item['transport']):
        apply_delivery_defaults(item)

        if has_queue_response(item['connection'], item['transport']):
            if item.get(_queue.Field_Queue_Response) is None:
                item[_queue.Field_Queue_Response] = _queue.Default_Queue_Response

# ################################################################################################################################
# ################################################################################################################################
