# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.destination.payload import new_overrides, resolve_payload

# ################################################################################################################################
# ################################################################################################################################

# The destinations the overrides are about
_first_destination = 'hl7.forward.ehr'
_second_destination = 'rest.billing'

# What arrived on the channel and what a service may put in its place
_request_payload = 'MSH|^~\\&|SENDER|FACILITY|RECEIVER|FACILITY|20260101120000||ADT^A01|MSG00001|P|2.5'
_broadcast_payload = 'MSH|^~\\&|SENDER|FACILITY|RECEIVER|FACILITY|20260101120000||ADT^A08|MSG00002|P|2.5'
_single_payload = '{"patient_id": "12345"}'

# ################################################################################################################################
# ################################################################################################################################

class TestPayloadResolution:

    def test_a_service_that_says_nothing_sends_the_message_as_it_arrived(self) -> 'None':
        overrides = new_overrides()

        first = resolve_payload(_first_destination, overrides, _request_payload)
        second = resolve_payload(_second_destination, overrides, _request_payload)

        assert first == _request_payload
        assert second == _request_payload

# ################################################################################################################################

    def test_a_broadcast_payload_reaches_every_destination(self) -> 'None':
        overrides = new_overrides()

        overrides.broadcast = _broadcast_payload
        overrides.has_broadcast = True

        assert resolve_payload(_first_destination, overrides, _request_payload) == _broadcast_payload
        assert resolve_payload(_second_destination, overrides, _request_payload) == _broadcast_payload

# ################################################################################################################################

    def test_a_payload_set_for_one_destination_wins_over_the_broadcast(self) -> 'None':
        overrides = new_overrides()

        overrides.broadcast = _broadcast_payload
        overrides.has_broadcast = True
        overrides.per_destination[_second_destination] = _single_payload

        assert resolve_payload(_first_destination, overrides, _request_payload) == _broadcast_payload
        assert resolve_payload(_second_destination, overrides, _request_payload) == _single_payload

# ################################################################################################################################

    def test_a_destination_named_with_nothing_to_send_is_dropped(self) -> 'None':
        overrides = new_overrides()

        overrides.per_destination[_first_destination] = None

        assert resolve_payload(_first_destination, overrides, _request_payload) is None
        assert resolve_payload(_second_destination, overrides, _request_payload) == _request_payload

# ################################################################################################################################

    def test_a_destination_is_dropped_even_when_a_broadcast_was_set(self) -> 'None':
        overrides = new_overrides()

        overrides.broadcast = _broadcast_payload
        overrides.has_broadcast = True
        overrides.per_destination[_first_destination] = None

        assert resolve_payload(_first_destination, overrides, _request_payload) is None
        assert resolve_payload(_second_destination, overrides, _request_payload) == _broadcast_payload

# ################################################################################################################################

    def test_a_broadcast_of_nothing_is_not_the_same_as_saying_nothing(self) -> 'None':
        overrides = new_overrides()

        # A service that set the broadcast to nothing said every destination is to be dropped,
        # which is not the same as a service that never touched it at all.
        overrides.broadcast = None
        overrides.has_broadcast = True

        assert resolve_payload(_first_destination, overrides, _request_payload) is None

# ################################################################################################################################
# ################################################################################################################################
