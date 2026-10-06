# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The queue switch and the DLQ settings of an outgoing connection and of a REST or SOAP channel in enmasse.

# stdlib
from json import loads

# Zato
from zato.cli.enmasse.util.invocation import export_retry_fields, Retry_Field_Defaults
from zato.common.api import HTTP_SOAP
from zato.common.util.delivery_config import apply_delivery_defaults, Delivery_Field_Defaults, Delivery_Fields, \
    validate_delivery_fields

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict
    anydict = anydict

# ################################################################################################################################
# ################################################################################################################################

_queue = HTTP_SOAP.Queue

Delivery_Fields = Delivery_Fields

# A channel's static queue response is a channel-only key, next to the retry config and the delivery fields
Channel_Delivery_Defaults = {}
Channel_Delivery_Defaults.update(Retry_Field_Defaults)
Channel_Delivery_Defaults.update(Delivery_Field_Defaults)
Channel_Delivery_Defaults[_queue.Field_Queue_Response] = _queue.Default_Queue_Response

Channel_Delivery_Fields = tuple(Channel_Delivery_Defaults)

# ################################################################################################################################
# ################################################################################################################################

def prepare_delivery_fields(connection_def:'anydict', connection_type:'str') -> 'None':
    """ Fills in, in place, the defaults of a YAML definition and validates its delivery fields.
    """
    apply_delivery_defaults(connection_def)

    try:
        validate_delivery_fields(connection_def)
    except ValueError as e:
        connection_name = connection_def['name']
        raise Exception(f'{e} for {connection_type} connection `{connection_name}`')

# ################################################################################################################################

def _fields_need_update(yaml_def:'anydict', db_def:'anydict', defaults:'anydict') -> 'bool':
    """ Whether a stored object differs from its YAML definition in any of the given fields, an absent value being its default.
    """
    for name, default in defaults.items():

        yaml_value = yaml_def.get(name)
        if yaml_value is None:
            yaml_value = default

        db_value = db_def.get(name)
        if db_value is None:
            db_value = default

        if yaml_value != db_value:
            return True

    return False

# ################################################################################################################################

def delivery_needs_update(yaml_def:'anydict', db_def:'anydict') -> 'bool':
    """ Whether a stored connection differs from its YAML definition in any delivery field.
    """
    out = _fields_need_update(yaml_def, db_def, Delivery_Field_Defaults)
    return out

# ################################################################################################################################

def prepare_channel_delivery_fields(channel_def:'anydict', connection_type:'str') -> 'None':
    """ Fills in the defaults of a channel's YAML definition and validates its delivery fields and its static queue response.
    """
    prepare_delivery_fields(channel_def, connection_type)

    queue_response = channel_def.get(_queue.Field_Queue_Response)
    if queue_response is None:
        return

    channel_name = channel_def['name']

    if not isinstance(queue_response, str):
        raise Exception(f'`{_queue.Field_Queue_Response}` must be a string, not `{queue_response!r}` ' + \
            f'for {connection_type} `{channel_name}`')

    # A static response is only ever returned by a channel that queues its requests
    if not channel_def[_queue.Field_Use_Queue]:
        raise Exception(f'`{_queue.Field_Queue_Response}` requires `{_queue.Field_Use_Queue}` to be true ' + \
            f'for {connection_type} `{channel_name}`')

# ################################################################################################################################

def take_channel_delivery_attrs(channel_def:'anydict') -> 'anydict':
    """ Removes the delivery keys from a channel's YAML definition, returning them as the channel's opaque attributes -
    every key is returned, a key the definition does not carry at its default, so the file is the source of truth
    for a channel that is being updated too.
    """
    out = {}

    for name, default in Channel_Delivery_Defaults.items():
        if name in channel_def:
            out[name] = channel_def.pop(name)
        else:
            out[name] = default

    return out

# ################################################################################################################################

def channel_delivery_needs_update(yaml_def:'anydict', db_def:'anydict') -> 'bool':
    """ Whether a stored channel differs from its YAML definition in any delivery key - the stored values are opaque attributes.
    """
    opaque = {}

    if opaque1 := db_def.get('opaque1'):
        opaque = loads(opaque1)

    out = _fields_need_update(yaml_def, opaque, Channel_Delivery_Defaults)
    return out

# ################################################################################################################################

def export_channel_delivery_fields(exported_channel:'anydict', opaque:'anydict') -> 'None':
    """ Copies a channel's delivery keys from its opaque attributes to its exported definition - only what differs from the defaults.
    """
    export_retry_fields(exported_channel, opaque)
    export_delivery_fields(exported_channel, opaque)

    if queue_response := opaque.get(_queue.Field_Queue_Response):
        exported_channel[_queue.Field_Queue_Response] = queue_response

# ################################################################################################################################

def export_delivery_fields(exported_conn:'anydict', opaque:'anydict') -> 'None':
    """ Copies the delivery fields from a connection's opaque attributes to its exported definition.
    """
    for name, default in Delivery_Field_Defaults.items():

        value = opaque.get(name)
        if value is None:
            continue

        # Defaults are not exported
        if value != default:
            exported_conn[name] = value

# ################################################################################################################################
# ################################################################################################################################
