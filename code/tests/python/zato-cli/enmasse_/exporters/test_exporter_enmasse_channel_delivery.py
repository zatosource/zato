# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# How a REST or SOAP channel's delivery keys are exported - which of them are written and where in the field order they go.

# Zato
from zato.cli.enmasse.util import Channel_Delivery_Fields, export_channel_delivery_fields, get_object_order
from zato.cli.enmasse.util.delivery import Channel_Delivery_Defaults
from zato.common.api import HTTP_SOAP
from zato.common.util.delivery_config import Delivery_Fields

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
_retry = HTTP_SOAP.Retry

# The key each channel type writes last, and the one the delivery keys follow
_alerts_key = 'alerts:dict'
_rest_key_before = 'deprecation_successor'
_soap_key_before = 'response_cache:dict'

# ################################################################################################################################
# ################################################################################################################################

def _opaque_on_defaults() -> 'anydict':
    """ The opaque attributes of a channel that never moved a delivery key away from its default.
    """
    out = {}
    out.update(Channel_Delivery_Defaults)
    return out

# ################################################################################################################################

def _export(opaque:'anydict') -> 'anydict':
    out:'anydict' = {}
    export_channel_delivery_fields(out, opaque)
    return out

# ################################################################################################################################

def _slice_between(order:'strlist', key_before:'str', key_after:'str') -> 'strlist':
    """ The keys of an order strictly between two keys.
    """
    start = order.index(key_before) + 1
    end = order.index(key_after)

    out = order[start:end]
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestChannelDeliveryFieldOrder:

    def test_a_rest_channel_writes_the_delivery_keys_after_its_own_keys(self) -> 'None':

        order = list(get_object_order('channel_rest'))
        between = _slice_between(order, _rest_key_before, _alerts_key)

        assert between == list(Channel_Delivery_Fields)

# ################################################################################################################################

    def test_a_soap_channel_writes_the_delivery_keys_after_its_own_keys(self) -> 'None':

        order = list(get_object_order('channel_soap'))
        between = _slice_between(order, _soap_key_before, _alerts_key)

        assert between == list(Channel_Delivery_Fields)

# ################################################################################################################################

    def test_the_delivery_keys_are_the_retry_config_the_delivery_fields_and_the_static_response(self) -> 'None':

        expected = list(_retry.FieldList) + list(Delivery_Fields) + [_queue.Field_Queue_Response]

        assert list(Channel_Delivery_Fields) == expected

# ################################################################################################################################
# ################################################################################################################################

class TestChannelDeliveryExport:

    def test_a_channel_on_defaults_writes_nothing(self) -> 'None':

        exported = _export(_opaque_on_defaults())

        assert exported == {}

# ################################################################################################################################

    def test_a_channel_that_predates_the_keys_writes_nothing(self) -> 'None':

        exported = _export({})

        assert exported == {}

# ################################################################################################################################

    def test_every_key_moved_away_from_its_default_is_written(self) -> 'None':

        opaque = _opaque_on_defaults()
        opaque[_retry.Field_Max_Retries] = 7
        opaque[_queue.Field_Use_Queue] = True
        opaque[_dlq.Field_Use_DLQ] = False
        opaque[_dlq.Field_Action] = _dlq.Action.Forward
        opaque[_dlq.Field_Retries] = 9
        opaque[_dlq.Field_Retry_Interval] = 120
        opaque[_dlq.Field_Forward_To] = 'orders.failed'
        opaque[_dlq.Field_Keep_Header] = False
        opaque[_queue.Field_Queue_Response] = '{"accepted": true}'

        exported = _export(opaque)

        assert exported == {
            _retry.Field_Max_Retries: 7,
            _queue.Field_Use_Queue: True,
            _dlq.Field_Use_DLQ: False,
            _dlq.Field_Action: _dlq.Action.Forward,
            _dlq.Field_Retries: 9,
            _dlq.Field_Retry_Interval: 120,
            _dlq.Field_Forward_To: 'orders.failed',
            _dlq.Field_Keep_Header: False,
            _queue.Field_Queue_Response: '{"accepted": true}',
        }

# ################################################################################################################################

    def test_the_static_response_is_written_only_when_not_empty(self) -> 'None':

        opaque = _opaque_on_defaults()
        opaque[_queue.Field_Use_Queue] = True

        exported = _export(opaque)
        assert _queue.Field_Queue_Response not in exported

        opaque[_queue.Field_Queue_Response] = 'ACCEPTED\nThank you'

        exported = _export(opaque)
        assert exported[_queue.Field_Queue_Response] == 'ACCEPTED\nThank you'

# ################################################################################################################################
# ################################################################################################################################
