# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The channels of the template came in through enmasse and go back out through it - an export of the running server's
# configuration has the delivery keys and the static response as the template gave them.

# Zato
from zato.common.api import HTTP_SOAP

# Test support
from queue_delivery.channel.client import export_config, exported_by_name
from queue_delivery.channel.type_under_test import Channel_DLQ_Discard, Channel_DLQ_Forward, Channel_DLQ_Keep, \
    Channel_DLQ_Retry, Channel_Hooked, Channel_No_DLQ, Channel_No_Retries, Channel_Orders, Channel_Plain, Channel_Static, \
    Channel_Static_Text, Channel_Static_XML, DLQ_Channel_Max_Retries, DLQ_Channel_Sleep_Time, DLQ_Retry_Channel_Rounds, \
    DLQ_Retry_Interval, Forward_Topic, Orders_Max_Retries, Orders_Sleep_Time, Static_Response_JSON, Static_Response_Text, \
    Static_Response_XML
from queue_delivery.channel_scenarios.base import ChannelScenarioBase

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

_retry = HTTP_SOAP.Retry
_queue = HTTP_SOAP.Queue
_dlq = HTTP_SOAP.DLQ

# The keys an export never writes at their defaults
_delivery_keys = _retry.FieldList + _queue.FieldList + (
    _dlq.Field_Use_DLQ, _dlq.Field_Action, _dlq.Field_Retries, _dlq.Field_Retry_Interval, _dlq.Field_Forward_To,
    _dlq.Field_Keep_Header, _queue.Field_Queue_Response,
)

# What the templates give their orders channels - a threshold and a multiplier of their own
_orders_backoff_threshold = 10
_orders_backoff_multiplier = 1

# ################################################################################################################################
# ################################################################################################################################

class EnmasseScenarios(ChannelScenarioBase):

    def _delivery_keys_of(self, item:'anydict') -> 'anydict':
        """ The delivery keys an exported channel carries, and only those.
        """
        out = {}

        for key in _delivery_keys:
            if key in item:
                out[key] = item[key]

        return out

# ################################################################################################################################

    def test_an_export_has_the_delivery_keys_and_the_static_response_as_the_template_had_them(self) -> 'None':
        """ Only the settings moved away from their defaults are written and the static responses come back verbatim.
        """
        exported = export_config()
        channels = exported_by_name(exported, self.t.enmasse_section)

        for key in self.t.connections:
            assert self.conn(key) in channels, (key, sorted(channels))

        # The switch off - nothing about delivery is written
        assert self._delivery_keys_of(channels[self.conn(Channel_Plain)]) == {}

        assert self._delivery_keys_of(channels[self.conn(Channel_Orders)]) == {
            _queue.Field_Use_Queue: True,
            _retry.Field_Max_Retries: Orders_Max_Retries,
            _retry.Field_Sleep_Time: Orders_Sleep_Time,
            _retry.Field_Backoff_Threshold: _orders_backoff_threshold,
            _retry.Field_Backoff_Multiplier: _orders_backoff_multiplier,
            _dlq.Field_Use_DLQ: False,
        }

        assert self._delivery_keys_of(channels[self.conn(Channel_No_Retries)]) == {
            _queue.Field_Use_Queue: True,
            _dlq.Field_Use_DLQ: False,
        }

        assert self._delivery_keys_of(channels[self.conn(Channel_DLQ_Keep)]) == {
            _queue.Field_Use_Queue: True,
            _retry.Field_Max_Retries: DLQ_Channel_Max_Retries,
            _retry.Field_Sleep_Time: DLQ_Channel_Sleep_Time,
        }

        assert self._delivery_keys_of(channels[self.conn(Channel_No_DLQ)]) == {
            _queue.Field_Use_Queue: True,
            _retry.Field_Max_Retries: DLQ_Channel_Max_Retries,
            _retry.Field_Sleep_Time: DLQ_Channel_Sleep_Time,
            _dlq.Field_Use_DLQ: False,
        }

        assert self._delivery_keys_of(channels[self.conn(Channel_DLQ_Retry)]) == {
            _queue.Field_Use_Queue: True,
            _retry.Field_Max_Retries: DLQ_Channel_Max_Retries,
            _retry.Field_Sleep_Time: DLQ_Channel_Sleep_Time,
            _dlq.Field_Action: _dlq.Action.Retry,
            _dlq.Field_Retries: DLQ_Retry_Channel_Rounds,
            _dlq.Field_Retry_Interval: DLQ_Retry_Interval,
        }

        assert self._delivery_keys_of(channels[self.conn(Channel_DLQ_Forward)]) == {
            _queue.Field_Use_Queue: True,
            _retry.Field_Max_Retries: DLQ_Channel_Max_Retries,
            _retry.Field_Sleep_Time: DLQ_Channel_Sleep_Time,
            _dlq.Field_Action: _dlq.Action.Forward,
            _dlq.Field_Retry_Interval: DLQ_Retry_Interval,
            _dlq.Field_Forward_To: Forward_Topic,
        }

        assert self._delivery_keys_of(channels[self.conn(Channel_DLQ_Discard)]) == {
            _queue.Field_Use_Queue: True,
            _retry.Field_Max_Retries: DLQ_Channel_Max_Retries,
            _retry.Field_Sleep_Time: DLQ_Channel_Sleep_Time,
            _dlq.Field_Action: _dlq.Action.Discard,
            _dlq.Field_Retry_Interval: DLQ_Retry_Interval,
        }

        # The static responses, verbatim
        static_responses = {
            Channel_Static: Static_Response_JSON,
            Channel_Static_XML: Static_Response_XML,
            Channel_Static_Text: Static_Response_Text,
        }

        for key, expected in static_responses.items():
            assert self._delivery_keys_of(channels[self.conn(key)]) == {
                _queue.Field_Use_Queue: True,
                _dlq.Field_Use_DLQ: False,
                _queue.Field_Queue_Response: expected,
            }, key

        # A channel whose service has the hook carries no static response
        assert self._delivery_keys_of(channels[self.conn(Channel_Hooked)]) == {
            _queue.Field_Use_Queue: True,
            _dlq.Field_Use_DLQ: False,
        }

# ################################################################################################################################
# ################################################################################################################################
