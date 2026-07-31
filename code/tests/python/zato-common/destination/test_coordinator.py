# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# Zato
from zato.common.destination.constants import DeliveryMode, Respond_From_Service
from zato.common.destination.coordinator import deliver, plan_hops
from zato.common.destination.model import parse_config
from zato.common.destination.payload import new_overrides

from connection_recorder import get_stored_list, new_test_context, Channel_Name, ConnectionRecorder, FHIR_Connection, \
    MLLP_Connection, Permanent_Error, Request_Payload, REST_Connection, Retry_Sleep_Seconds, Transient_Error

# ################################################################################################################################
# ################################################################################################################################

class TestPlanning:

    def test_every_active_destination_receives_the_message_as_it_arrived(self) -> 'None':
        config = parse_config(Channel_Name, get_stored_list())

        planned_list = plan_hops(config, new_overrides(), Request_Payload)

        assert len(planned_list) == 3

        for planned in planned_list:
            assert planned.payload == Request_Payload

        assert planned_list[0].sequence == 0
        assert planned_list[1].sequence == 1
        assert planned_list[2].sequence == 2

# ################################################################################################################################

    def test_a_paused_destination_is_left_out_of_the_delivery(self) -> 'None':
        stored = get_stored_list()
        stored[1]['is_active'] = False

        config = parse_config(Channel_Name, stored)

        planned_list = plan_hops(config, new_overrides(), Request_Payload)

        assert len(planned_list) == 2
        assert planned_list[0].entry.name == MLLP_Connection
        assert planned_list[1].entry.name == FHIR_Connection

# ################################################################################################################################

    def test_a_destination_the_service_dropped_is_left_out_of_the_delivery(self) -> 'None':
        config = parse_config(Channel_Name, get_stored_list())

        overrides = new_overrides()
        overrides.per_destination[REST_Connection] = None

        planned_list = plan_hops(config, overrides, Request_Payload)

        assert len(planned_list) == 2
        assert planned_list[0].entry.name == MLLP_Connection
        assert planned_list[1].entry.name == FHIR_Connection

# ################################################################################################################################
# ################################################################################################################################

class TestDelivery:

    def test_every_destination_receives_the_message(self) -> 'None':
        recorder = ConnectionRecorder()
        context = new_test_context(recorder)
        config = parse_config(Channel_Name, get_stored_list())

        result = deliver(context, config, new_overrides(), Request_Payload)

        assert result.has_response is False
        assert result.hops == []

        assert recorder.get_delivered_names() == [MLLP_Connection, REST_Connection, FHIR_Connection]

# ################################################################################################################################

    def test_all_at_once_hands_over_one_run_per_destination(self) -> 'None':
        recorder = ConnectionRecorder()
        context = new_test_context(recorder)
        config = parse_config(Channel_Name, get_stored_list(), Respond_From_Service, DeliveryMode.Same_Time)

        _ = deliver(context, config, new_overrides(), Request_Payload)

        assert recorder.spawn_count == 3

# ################################################################################################################################

    def test_one_after_another_hands_over_one_run_for_the_whole_list(self) -> 'None':
        recorder = ConnectionRecorder()
        context = new_test_context(recorder)
        config = parse_config(Channel_Name, get_stored_list(), Respond_From_Service, DeliveryMode.In_Order)

        _ = deliver(context, config, new_overrides(), Request_Payload)

        assert recorder.spawn_count == 1
        assert recorder.get_delivered_names() == [MLLP_Connection, REST_Connection, FHIR_Connection]

# ################################################################################################################################

    def test_one_destination_failing_does_not_stop_the_others(self) -> 'None':
        recorder = ConnectionRecorder()
        recorder.always_failing[REST_Connection] = Permanent_Error

        context = new_test_context(recorder)
        config = parse_config(Channel_Name, get_stored_list(), Respond_From_Service, DeliveryMode.In_Order)

        _ = deliver(context, config, new_overrides(), Request_Payload)

        assert recorder.get_delivered_names() == [MLLP_Connection, REST_Connection, FHIR_Connection]

# ################################################################################################################################

    def test_what_the_service_said_is_what_the_destinations_receive(self) -> 'None':
        recorder = ConnectionRecorder()
        context = new_test_context(recorder)
        config = parse_config(Channel_Name, get_stored_list())

        overrides = new_overrides()
        overrides.broadcast = 'Everyone gets this one'
        overrides.has_broadcast = True
        overrides.per_destination[FHIR_Connection] = {'resourceType': 'Patient'}

        _ = deliver(context, config, overrides, Request_Payload)

        delivered = dict(recorder.deliveries)

        assert delivered[MLLP_Connection] == 'Everyone gets this one'
        assert delivered[REST_Connection] == 'Everyone gets this one'
        assert delivered[FHIR_Connection] == {'resourceType': 'Patient'}

# ################################################################################################################################
# ################################################################################################################################

class TestRespondFrom:

    def test_the_answering_destination_is_delivered_to_first_and_its_answer_is_the_reply(self) -> 'None':
        recorder = ConnectionRecorder()
        context = new_test_context(recorder)
        config = parse_config(Channel_Name, get_stored_list(), FHIR_Connection, DeliveryMode.In_Order)

        result = deliver(context, config, new_overrides(), Request_Payload)

        assert result.has_response is True
        assert result.response == f'Accepted by {FHIR_Connection}'

        assert len(result.hops) == 1
        assert result.hops[0].destination_name == FHIR_Connection
        assert result.hops[0].is_ok is True

        # The one that answers goes first, whatever place it takes in the list
        assert recorder.get_delivered_names() == [FHIR_Connection, MLLP_Connection, REST_Connection]

# ################################################################################################################################

    def test_the_answering_destination_failing_is_the_channel_failing(self) -> 'None':
        recorder = ConnectionRecorder()
        recorder.always_failing[FHIR_Connection] = Permanent_Error

        context = new_test_context(recorder)
        config = parse_config(Channel_Name, get_stored_list(), FHIR_Connection)

        with pytest.raises(Exception) as raised:
            _ = deliver(context, config, new_overrides(), Request_Payload)

        assert Permanent_Error in str(raised.value)
        assert f'could not deliver to `{FHIR_Connection}`' in str(raised.value)

        # Nothing else was delivered to, so the caller resending reaches every destination once
        assert recorder.get_delivered_names() == [FHIR_Connection]

# ################################################################################################################################

    def test_a_channel_answering_from_a_destination_it_dropped_answers_from_its_service(self) -> 'None':
        recorder = ConnectionRecorder()
        context = new_test_context(recorder)
        config = parse_config(Channel_Name, get_stored_list(), FHIR_Connection)

        overrides = new_overrides()
        overrides.per_destination[FHIR_Connection] = None

        result = deliver(context, config, overrides, Request_Payload)

        assert result.has_response is False
        assert recorder.get_delivered_names() == [MLLP_Connection, REST_Connection]

# ################################################################################################################################

    def test_a_channel_answering_from_a_destination_that_is_paused_answers_from_its_service(self) -> 'None':
        recorder = ConnectionRecorder()
        context = new_test_context(recorder)

        # The destination the channel replies from is paused, so nothing plans a delivery to it
        stored = get_stored_list()
        stored[2]['is_active'] = False

        config = parse_config(Channel_Name, stored, FHIR_Connection)

        result = deliver(context, config, new_overrides(), Request_Payload)

        # The channel has no answer of its own to relay and the remaining destinations
        # still received the message.
        assert result.has_response is False
        assert recorder.get_delivered_names() == [MLLP_Connection, REST_Connection]

# ################################################################################################################################
# ################################################################################################################################

class TestRetries:

    def test_a_failure_another_attempt_can_get_past_is_tried_again(self) -> 'None':
        recorder = ConnectionRecorder()
        recorder.failing_attempts[MLLP_Connection] = 2

        context = new_test_context(recorder, retry_count=2)
        stored = get_stored_list()[:1]
        config = parse_config(Channel_Name, stored, MLLP_Connection)

        result = deliver(context, config, new_overrides(), Request_Payload)

        assert result.has_response is True
        assert result.hops[0].attempt_count == 3
        assert result.hops[0].is_ok is True

        # Two attempts failed, so two waits happened before the third one went through
        assert recorder.sleeps == [Retry_Sleep_Seconds, Retry_Sleep_Seconds]

# ################################################################################################################################

    def test_a_destination_gets_no_more_attempts_than_it_is_allowed(self) -> 'None':
        recorder = ConnectionRecorder()
        recorder.always_failing[MLLP_Connection] = Transient_Error

        context = new_test_context(recorder, retry_count=2)
        stored = get_stored_list()[:1]
        config = parse_config(Channel_Name, stored)

        _ = deliver(context, config, new_overrides(), Request_Payload)

        assert len(recorder.deliveries) == 3
        assert len(recorder.sleeps) == 2

# ################################################################################################################################

    def test_a_message_the_destination_will_never_accept_is_not_sent_again(self) -> 'None':
        recorder = ConnectionRecorder()
        recorder.always_failing[MLLP_Connection] = Permanent_Error

        context = new_test_context(recorder, retry_count=5)
        stored = get_stored_list()[:1]
        config = parse_config(Channel_Name, stored)

        _ = deliver(context, config, new_overrides(), Request_Payload)

        assert len(recorder.deliveries) == 1
        assert recorder.sleeps == []

# ################################################################################################################################
# ################################################################################################################################
