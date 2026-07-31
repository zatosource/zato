# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What an MLLP channel does with a message on its way in - the service it hands it to and what it
# tells that service about the channel it came from, or, with no service to hand it to, the
# destinations it delivers to itself and in what order.

# Zato
from zato.common.api import CHANNEL
from zato.common.destination.constants import DeliveryMode, DestinationType
from zato.server.destination.channel import run_for_channel

from service_stub import MLLP_Response, REST_Response
from mllp_test_channel import get_email_calls, get_invoker, get_mllp_calls, get_rest_calls, running_synchronously, \
    Channel_Name, Message_CID, MLLP_Connection, new_channel_item, new_parallel_server, new_stored_list, new_wrapper, \
    Request_Message, REST_Connection, SMTP_Connection

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict

    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

# Where the e-mail destination of the fan-out sends and under what subject line
_email_recipient = 'admissions@example.com'
_email_subject = 'A new admission arrived'

# ################################################################################################################################
# ################################################################################################################################

def _new_email_entry() -> 'stranydict':
    """ Returns an e-mail destination the way the Dashboard stores one, with the recipient
    and the subject line among its options.
    """
    out = {
        'name': SMTP_Connection,
        'type': DestinationType.SMTP,
        'connection': SMTP_Connection,
        'is_active': True,
        'options': {'to': _email_recipient, 'subject': _email_subject},
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestWhatAChannelTellsItsService:

    def test_the_channel_item_carries_everything_the_channel_declares(self) -> 'None':
        stored = new_stored_list()
        wrapper = new_wrapper(destinations=stored, respond_from=MLLP_Connection,
            delivery_mode=DeliveryMode.In_Order)

        channel_item = wrapper._build_channel_item()

        assert channel_item['name'] == Channel_Name
        assert channel_item['destinations'] == stored
        assert channel_item['respond_from'] == MLLP_Connection
        assert channel_item['delivery_mode'] == DeliveryMode.In_Order

# ################################################################################################################################

    def test_a_service_is_invoked_as_the_channel_it_was_invoked_from(self) -> 'None':
        wrapper = new_wrapper(destinations=new_stored_list())

        _ = wrapper._invoke_service(Request_Message, Message_CID)

        _, kwargs = get_invoker(wrapper).invoke.call_args

        assert kwargs['channel'] == CHANNEL.HL7_MLLP
        assert kwargs['zato_ctx']['zato.channel_item']['name'] == Channel_Name

        # The message keeps the correlation id it arrived under, so what the service does with it
        # is part of that one message's trail
        assert kwargs['cid'] == Message_CID

# ################################################################################################################################

    def test_what_the_service_pipeline_produced_is_what_the_channel_answers_with(self) -> 'None':
        wrapper = new_wrapper()
        get_invoker(wrapper).invoke.return_value = MLLP_Response

        out = wrapper._invoke_service(Request_Message, Message_CID)

        assert out == MLLP_Response

# ################################################################################################################################
# ################################################################################################################################

class TestWhichWayAMessageGoes:

    def test_a_channel_that_names_a_service_hands_its_messages_to_it(self) -> 'None':
        wrapper = new_wrapper()

        assert wrapper._get_callback() == wrapper._invoke_service

# ################################################################################################################################

    def test_a_channel_that_names_no_service_delivers_to_its_destinations_itself(self) -> 'None':
        wrapper = new_wrapper(service='', destinations=new_stored_list())

        assert wrapper._get_callback() == wrapper._deliver_to_destinations

# ################################################################################################################################
# ################################################################################################################################

class TestAChannelWithNoService:

    def test_every_destination_receives_the_message_as_it_arrived(self) -> 'None':
        stored = new_stored_list()
        stored.append(_new_email_entry())

        channel_item = new_channel_item(stored, delivery_mode=DeliveryMode.In_Order)

        with running_synchronously():
            result = run_for_channel(new_parallel_server(), channel_item, Request_Message)

        assert result
        assert result.has_response is False

        assert get_mllp_calls()[0][1] == Request_Message
        assert get_rest_calls()[0][2] == (Request_Message,)

        # The e-mail destination received the message as the body, sent to the recipient
        # and under the subject line the destination names.
        connection, to, subject, body = get_email_calls()[0]

        assert connection == SMTP_Connection
        assert to == _email_recipient
        assert subject == _email_subject
        assert body == Request_Message

# ################################################################################################################################

    def test_the_destination_the_channel_replies_from_produces_the_answer(self) -> 'None':
        stored = new_stored_list()[:1]
        channel_item = new_channel_item(stored, respond_from=MLLP_Connection)

        with running_synchronously():
            result = run_for_channel(new_parallel_server(), channel_item, Request_Message)

        assert result
        assert result.has_response is True
        assert result.response == MLLP_Response

# ################################################################################################################################

    def test_the_rest_destination_the_channel_replies_from_produces_the_answer(self) -> 'None':
        stored = new_stored_list()[1:]
        channel_item = new_channel_item(stored, respond_from=REST_Connection)

        with running_synchronously():
            result = run_for_channel(new_parallel_server(), channel_item, Request_Message)

        assert result
        assert result.has_response is True
        assert result.response == REST_Response

        # The delivery really went through the REST connection
        assert get_rest_calls()[0][0] == REST_Connection

# ################################################################################################################################

    def test_a_destination_that_is_paused_receives_nothing(self) -> 'None':
        stored = new_stored_list()
        stored[1]['is_active'] = False

        channel_item = new_channel_item(stored, delivery_mode=DeliveryMode.In_Order)

        with running_synchronously():
            _ = run_for_channel(new_parallel_server(), channel_item, Request_Message)

        assert len(get_mllp_calls()) == 1
        assert get_rest_calls() == []

# ################################################################################################################################

    def test_a_channel_with_every_destination_paused_delivers_nothing(self) -> 'None':
        stored = new_stored_list()

        for entry in stored:
            entry['is_active'] = False

        channel_item = new_channel_item(stored)

        with running_synchronously():
            assert run_for_channel(new_parallel_server(), channel_item, Request_Message) is None

        assert get_mllp_calls() == []
        assert get_rest_calls() == []

# ################################################################################################################################

    def test_delivering_one_after_another_reaches_every_destination_in_turn(self) -> 'None':
        channel_item = new_channel_item(new_stored_list(), delivery_mode=DeliveryMode.In_Order)

        with running_synchronously():
            _ = run_for_channel(new_parallel_server(), channel_item, Request_Message)

        assert get_mllp_calls()[0][0] == MLLP_Connection
        assert get_rest_calls()[0][0] == REST_Connection

# ################################################################################################################################

    def test_delivering_all_at_once_reaches_every_destination_too(self) -> 'None':
        channel_item = new_channel_item(new_stored_list(), delivery_mode=DeliveryMode.Same_Time)

        with running_synchronously():
            _ = run_for_channel(new_parallel_server(), channel_item, Request_Message)

        assert len(get_mllp_calls()) == 1
        assert len(get_rest_calls()) == 1

# ################################################################################################################################

    def test_the_channel_answers_with_what_the_destination_it_replies_from_said(self) -> 'None':
        """ The whole way through the wrapper, which is what the listener turns into the
        acknowledgment the sender receives.
        """
        wrapper = new_wrapper(service='', destinations=new_stored_list(), respond_from=MLLP_Connection)
        wrapper.server = new_parallel_server()

        with running_synchronously():
            out = wrapper._deliver_to_destinations(Request_Message, Message_CID)

        assert out == MLLP_Response

# ################################################################################################################################
# ################################################################################################################################
