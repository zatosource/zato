# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What a sender is answered with once its message has been through the channel it matched. A
# channel that got its message where it had to go acknowledges it positively, one that could not
# says so, and a channel that replies from one of its destinations answers with what that
# destination said rather than with anything built here.

# Zato
from zato.common.hl7.mllp.settings import RouteSettings

from service_stub import REST_Response
from mllp_test_channel import handle_one_message, new_parallel_server, new_route, new_stored_list, new_wrapper, \
    running_synchronously, Request_Message, REST_Connection

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

# What a destination this channel replies from answered its delivery with
_downstream_ack = 'MSH|^~\\&|RECEIVER|FACILITY|SENDER|FACILITY|20260101120001||ACK^A01|ACK00001|P|2.5\rMSA|AA|MSG00001'

# What a service that is not in the business of answering anything returns
_service_response = {'status': 'handled'}

# ################################################################################################################################
# ################################################################################################################################

class TestWhatTheSenderIsAnswered:

    def test_a_message_that_got_through_is_acknowledged_positively(self) -> 'None':

        def callback(data:'any_', cid:'str') -> 'None':
            pass

        route = new_route(callback, service_name='test.hl7.mllp.echo')

        replies = handle_one_message(route)

        assert len(replies) == 1
        assert 'MSA|AA|' in replies[0]

# ################################################################################################################################

    def test_a_channel_that_could_not_deliver_answers_with_an_application_error(self) -> 'None':
        """ A destination the channel replies from failing raises out of the fan-out, which is
        what the listener's own try/except turns into the negative acknowledgment.
        """

        def callback(data:'any_', cid:'str') -> 'None':
            raise Exception('Channel `x` could not deliver to `y`')

        route = new_route(callback)

        replies = handle_one_message(route)

        assert len(replies) == 1
        assert 'MSA|AE|' in replies[0]

# ################################################################################################################################

    def test_the_answer_of_the_destination_a_channel_replies_from_is_the_answer(self) -> 'None':

        def callback(data:'any_', cid:'str') -> 'str':
            return _downstream_ack

        route = new_route(callback)

        replies = handle_one_message(route)

        assert replies == [_downstream_ack]

# ################################################################################################################################

    def test_a_channel_with_nothing_of_its_own_to_say_is_answered_for(self) -> 'None':
        """ Every channel that does not reply from a destination is here - what its service
        returned is its caller's business, not the sender's.
        """

        def callback(data:'any_', cid:'str') -> 'any_':
            return _service_response

        route = new_route(callback, service_name='test.hl7.mllp.echo', has_destinations=False)

        replies = handle_one_message(route)

        assert len(replies) == 1
        assert 'MSA|AA|' in replies[0]
        assert 'status' not in replies[0]

# ################################################################################################################################

    def test_a_channel_that_answered_with_text_that_is_not_a_message_is_answered_for(self) -> 'None':

        def callback(data:'any_', cid:'str') -> 'str':
            return 'Accepted'

        route = new_route(callback)

        replies = handle_one_message(route)

        assert len(replies) == 1
        assert 'MSA|AA|' in replies[0]

# ################################################################################################################################

    def test_a_channel_that_replies_from_a_rest_destination_is_answered_for(self) -> 'None':
        """ A REST destination answers with plain text rather than with a message of its own,
        so the listener builds the acknowledgment instead of relaying that text.
        """
        stored = new_stored_list()[1:]

        wrapper = new_wrapper(service='', destinations=stored, respond_from=REST_Connection)
        wrapper.server = new_parallel_server()

        route = new_route(wrapper._deliver_to_destinations)

        with running_synchronously():
            replies = handle_one_message(route)

        assert len(replies) == 1
        assert 'MSA|AA|' in replies[0]
        assert REST_Response not in replies[0]

# ################################################################################################################################

    def test_the_error_a_channel_hides_stays_hidden(self) -> 'None':
        """ A channel that does not return errors says only that the delivery failed, which is
        what keeps the reason for a failed hop inside the audit trail.
        """

        def callback(data:'any_', cid:'str') -> 'None':
            raise Exception('Connection refused by the destination')

        route = new_route(callback)
        route.settings = RouteSettings(should_parse_on_input=False, should_return_errors=False)

        replies = handle_one_message(route)

        assert 'MSA|AE|' in replies[0]
        assert 'Connection refused' not in replies[0]

# ################################################################################################################################
# ################################################################################################################################

class TestWhatTheChannelIsGiven:

    def test_a_channel_is_given_the_message_as_it_arrived(self) -> 'None':
        """ A channel that does not parse on input hands the bytes on as text and nothing else,
        which is what makes a channel with no service a pass-through.
        """
        received = []

        def callback(data:'any_', cid:'str') -> 'None':
            received.append(data)

        route = new_route(callback)

        _ = handle_one_message(route)

        assert received == [Request_Message]

# ################################################################################################################################

    def test_a_duplicate_reaches_no_destination_at_all(self) -> 'None':
        """ A control id the channel has already seen is acknowledged positively without anything
        being delivered a second time.
        """
        received = []

        def callback(data:'any_', cid:'str') -> 'None':
            received.append(data)

        route = new_route(callback)
        route.settings = RouteSettings(should_parse_on_input=False, dedup_ttl_value=1, dedup_ttl_unit='hours')

        first_replies = handle_one_message(route)
        second_replies = handle_one_message(route)

        assert len(received) == 1

        assert 'MSA|AA|' in first_replies[0]
        assert 'MSA|AA|' in second_replies[0]

# ################################################################################################################################
# ################################################################################################################################
