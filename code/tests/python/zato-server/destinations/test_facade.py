# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.server.destination.facade import DestinationFacade

# ################################################################################################################################
# ################################################################################################################################

# The destinations the service says something about
_first_destination = 'hl7.forward.ehr'
_second_destination = 'rest.billing'

# What arrived on the channel and what a service may put in its place
_request_payload = 'MSH|^~\\&|SENDER|FACILITY|RECEIVER|FACILITY|20260101120000||ADT^A01|MSG00001|P|2.5'
_broadcast_payload = 'MSH|^~\\&|SENDER|FACILITY|RECEIVER|FACILITY|20260101120000||ADT^A08|MSG00002|P|2.5'
_single_payload = '{"patient_id": "12345"}'

# ################################################################################################################################
# ################################################################################################################################

def _new_facade() -> 'DestinationFacade':
    out = DestinationFacade()
    out.init(_request_payload)

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestReading:

    def test_a_destination_is_sent_the_message_as_it_arrived(self) -> 'None':
        facade = _new_facade()

        assert facade[_first_destination] == _request_payload
        assert facade[_second_destination] == _request_payload

# ################################################################################################################################

    def test_a_destination_reads_back_what_the_service_set_for_it(self) -> 'None':
        facade = _new_facade()

        facade[_second_destination] = _single_payload

        assert facade[_first_destination] == _request_payload
        assert facade[_second_destination] == _single_payload

# ################################################################################################################################

    def test_the_broadcast_payload_reads_back_as_it_was_set(self) -> 'None':
        facade = _new_facade()

        facade.payload = _broadcast_payload

        assert facade.payload == _broadcast_payload
        assert facade[_first_destination] == _broadcast_payload

# ################################################################################################################################
# ################################################################################################################################

class TestWhatTheEngineIsToldToDo:

    def test_a_service_that_says_nothing_leaves_every_destination_alone(self) -> 'None':
        facade = _new_facade()

        overrides = facade.get_overrides()

        assert overrides.has_broadcast is False
        assert overrides.per_destination == {}

# ################################################################################################################################

    def test_setting_the_payload_is_what_marks_the_broadcast_as_set(self) -> 'None':
        facade = _new_facade()

        facade.payload = _broadcast_payload

        overrides = facade.get_overrides()

        assert overrides.has_broadcast is True
        assert overrides.broadcast == _broadcast_payload

# ################################################################################################################################

    def test_a_broadcast_of_nothing_is_still_a_broadcast(self) -> 'None':
        facade = _new_facade()

        facade.payload = None

        overrides = facade.get_overrides()

        assert overrides.has_broadcast is True
        assert overrides.broadcast is None

# ################################################################################################################################

    def test_a_destination_set_to_nothing_is_one_the_engine_drops(self) -> 'None':
        facade = _new_facade()

        facade[_first_destination] = None

        overrides = facade.get_overrides()

        assert _first_destination in overrides.per_destination
        assert overrides.per_destination[_first_destination] is None

# ################################################################################################################################

    def test_the_facade_describes_everything_the_service_said(self) -> 'None':
        facade = _new_facade()

        facade.payload = _broadcast_payload
        facade[_second_destination] = _single_payload

        assert facade.to_dict() == {
            'payload': _broadcast_payload,
            'has_payload': True,
            'per_destination': {_second_destination: _single_payload},
        }

# ################################################################################################################################

    def test_each_invocation_starts_with_the_service_having_said_nothing(self) -> 'None':
        facade = _new_facade()

        facade.payload = _broadcast_payload
        facade[_second_destination] = _single_payload

        # The pipeline re-initializes the facade per invocation, which is what stops one message
        # from carrying over what the service said about the one before it.
        facade.init(_request_payload)

        overrides = facade.get_overrides()

        assert overrides.has_broadcast is False
        assert overrides.per_destination == {}
        assert facade[_second_destination] == _request_payload

# ################################################################################################################################
# ################################################################################################################################
