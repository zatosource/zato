# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The queue switch and the DLQ settings of an outgoing connection - fields, defaults, types and validation.

# Zato
from zato.common.api import HTTP_SOAP

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, strlist
    anydict = anydict
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

_queue = HTTP_SOAP.Queue
_dlq = HTTP_SOAP.DLQ

# Every field and its default
Delivery_Field_Defaults = {
    _queue.Field_Use_Queue: _queue.Default_Use_Queue,
    _dlq.Field_Use_DLQ: _dlq.Default_Use_DLQ,
    _dlq.Field_Action: _dlq.Default_Action,
    _dlq.Field_Retries: _dlq.Default_Retries,
    _dlq.Field_Retry_Interval: _dlq.Default_Retry_Interval,
    _dlq.Field_Forward_To: _dlq.Default_Forward_To,
    _dlq.Field_Keep_Header: _dlq.Default_Keep_Header,
}

Delivery_Fields = tuple(Delivery_Field_Defaults)

Delivery_Bool_Fields = (_queue.Field_Use_Queue, _dlq.Field_Use_DLQ, _dlq.Field_Keep_Header)
Delivery_Int_Fields = (_dlq.Field_Retries, _dlq.Field_Retry_Interval)
Delivery_Actions = (_dlq.Action.Keep, _dlq.Action.Retry, _dlq.Action.Forward, _dlq.Action.Discard)

# ################################################################################################################################
# ################################################################################################################################

def apply_delivery_defaults(item:'anydict') -> 'None':
    """ Fills in, in place, every delivery field the item does not carry.
    """
    for name, default in Delivery_Field_Defaults.items():
        if item.get(name) is None:
            item[name] = default

# ################################################################################################################################

def validate_delivery_fields(item:'anydict') -> 'None':
    """ Raises ValueError on a delivery field whose value is not what the field takes, every field must be present.
    """
    for name in Delivery_Bool_Fields:
        value = item[name]
        if not isinstance(value, bool):
            raise ValueError(f'`{name}` must be a boolean, not `{value!r}`')

    for name in Delivery_Int_Fields:
        value = item[name]

        # A bool is an int, and not a count
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError(f'`{name}` must be an integer, not `{value!r}`')

        if value < 0:
            raise ValueError(f'`{name}` must not be negative, not `{value}`')

    action = item[_dlq.Field_Action]
    if action not in Delivery_Actions:
        raise ValueError(f'`{_dlq.Field_Action}` must be one of `{list(Delivery_Actions)}`, not `{action!r}`')

    forward_to = item[_dlq.Field_Forward_To]
    if not isinstance(forward_to, str):
        raise ValueError(f'`{_dlq.Field_Forward_To}` must be a topic name, not `{forward_to!r}`')

    if action == _dlq.Action.Forward:
        if not forward_to:
            raise ValueError(f'`{_dlq.Field_Forward_To}` is required when `{_dlq.Field_Action}` is `{_dlq.Action.Forward}`')

# ################################################################################################################################
# ################################################################################################################################
