# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import FORBIDDEN, INTERNAL_SERVER_ERROR, NOT_FOUND, OK

# pytest
import pytest

# requests
import requests

# Zato
from zato.common.api import SMS
from zato.common.sms.model import Kind_Message, Kind_Status, Status_Delivered, Status_Failed

# Live SMS
from live_sms.base import Callback_Resend_Intervals

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from conftest import SMSSuite

# ################################################################################################################################
# ################################################################################################################################

To_Number = '+12025550101'
From_Number = '+12025550102'

Providers = SMS.ProviderList

# The delivered and failed statuses in each provider's own vocabulary
Delivered_Status = {
    SMS.Provider.Twilio: 'delivered',
    SMS.Provider.Vonage: 'delivered',
    SMS.Provider.Infobip: 'DELIVERED',
    SMS.Provider.Africas_Talking: 'Success',
}

Failed_Status = {
    SMS.Provider.Twilio: 'undelivered',
    SMS.Provider.Vonage: 'undeliverable',
    SMS.Provider.Infobip: 'UNDELIVERABLE',
    SMS.Provider.Africas_Talking: 'Failed',
}

# The error code a failed delivery is reported with
Error_Code = {
    SMS.Provider.Twilio: '30003',
    SMS.Provider.Vonage: 'https://developer.vonage.com/api-errors/messages#1000',
    SMS.Provider.Infobip: 'EC_ABSENT_SUBSCRIBER',
    SMS.Provider.Africas_Talking: 'UnsupportedNumberType',
}

# Each provider's expected response to an accepted callback
Callback_Response_Body = {
    SMS.Provider.Twilio: '<Response/>',
    SMS.Provider.Vonage: '',
    SMS.Provider.Infobip: '',
    SMS.Provider.Africas_Talking: 'OK',
}

# The providers whose callbacks are signed
Signed_Providers = (SMS.Provider.Twilio, SMS.Provider.Vonage)

# The headers the channel sets on each delivered event
Header_Channel = 'zato-sms-channel'
Header_Provider = 'zato-sms-provider'
Header_Kind = 'zato-sms-kind'
Header_ID = 'zato-sms-id'
Header_Status = 'zato-sms-status'

# The number of pushes of a callback the receiver rejects
Attempts_Until_Given_Up = 1 + len(Callback_Resend_Intervals)

# ################################################################################################################################
# ################################################################################################################################

class TestWebhook:

    @pytest.mark.parametrize('provider', Providers)
    def test_a_delivery_report_reaches_the_service_with_the_channel_headers(self, sms:'SMSSuite', provider:'str') -> 'None':

        simulator = sms.simulator(provider)
        channel_name = sms.webhook_channel(provider)

        response = sms.send(provider, To_Number, 'report on me')
        message_id = response['result']['id']

        attempts = simulator.set_status(message_id, Delivered_Status[provider])

        assert len(attempts) == 1, attempts
        attempt = attempts[0]

        assert attempt.status == OK, attempt
        assert attempt.body.endswith(Callback_Response_Body[provider]), attempt
        assert attempt.headers[SMS.Header_Callback_CID.lower()], attempt

        received = sms.wait_for_received(1)
        assert len(received) == 1, received

        record = received[0]
        event = record['event']

        assert event['kind'] == Kind_Status
        assert event['id'] == message_id
        assert event['status'] == Status_Delivered
        assert event['to'] == To_Number
        assert event['error_code'] == ''
        assert event['raw'], event

        headers = record['headers']
        assert headers[Header_Channel] == channel_name
        assert headers[Header_Provider] == provider
        assert headers[Header_Kind] == Kind_Status
        assert headers[Header_ID] == message_id
        assert headers[Header_Status] == Status_Delivered

        # The callback's correlation ID is the one the service ran under
        assert attempt.headers[SMS.Header_Callback_CID.lower()] == record['cid'], (attempt, record)

# ################################################################################################################################

    @pytest.mark.parametrize('provider', Providers)
    def test_a_failed_delivery_reports_its_error_code(self, sms:'SMSSuite', provider:'str') -> 'None':

        simulator = sms.simulator(provider)

        response = sms.send(provider, To_Number, 'fail on me')
        message_id = response['result']['id']

        attempts = simulator.set_status(message_id, Failed_Status[provider], Error_Code[provider])
        assert attempts[0].status == OK, attempts

        received = sms.wait_for_received(1)
        event = received[0]['event']

        assert event['kind'] == Kind_Status
        assert event['id'] == message_id
        assert event['status'] == Status_Failed
        assert event['error_code'] == Error_Code[provider], event

# ################################################################################################################################

    @pytest.mark.parametrize('provider', Providers)
    def test_an_incoming_text_reaches_the_service(self, sms:'SMSSuite', provider:'str') -> 'None':

        simulator = sms.simulator(provider)

        incoming = simulator.add_incoming_text(From_Number, To_Number, 'a reply')

        accepted = simulator.accepted_callbacks()
        assert len(accepted) == 1, simulator.callbacks

        received = sms.wait_for_received(1)
        record = received[0]
        event = record['event']

        assert event['kind'] == Kind_Message
        assert event['id'] == incoming.message_id
        assert event['from_'] == From_Number
        assert event['to'] == To_Number
        assert event['body'] == 'a reply'
        assert event['status'] == ''

        assert record['headers'][Header_Kind] == Kind_Message
        assert record['headers'][Header_Status] == ''

# ################################################################################################################################

    @pytest.mark.parametrize('provider', Signed_Providers)
    def test_a_callback_with_an_invalid_signature_is_refused_and_nothing_reaches_the_service(self, sms:'SMSSuite',
        provider:'str') -> 'None':
        """ The simulator signs with a secret the connection does not have, every push is refused with 403
        and the simulator stops after its resend intervals.
        """
        # Twilio signs with the auth token, Vonage with its separate signature secret
        if provider == SMS.Provider.Twilio:
            simulator = sms.simulators.twilio
            secret = simulator.password
            simulator.password = secret + '-changed'
        else:
            simulator = sms.simulators.vonage
            secret = simulator.signature_secret
            simulator.signature_secret = secret + '-changed'

        try:
            _ = simulator.add_incoming_text(From_Number, To_Number, 'signed wrongly')
        finally:
            if provider == SMS.Provider.Twilio:
                sms.simulators.twilio.password = secret
            else:
                sms.simulators.vonage.signature_secret = secret

        assert len(simulator.callbacks) == Attempts_Until_Given_Up, simulator.callbacks

        for attempt in simulator.callbacks:
            assert attempt.status == FORBIDDEN, attempt

        assert sms.get_received() == []

# ################################################################################################################################

    @pytest.mark.parametrize('provider', Providers)
    def test_a_resent_callback_is_accepted_but_not_handed_over_again(self, sms:'SMSSuite', provider:'str') -> 'None':

        simulator = sms.simulator(provider)

        incoming = simulator.add_incoming_text(From_Number, To_Number, 'once only')
        _ = sms.wait_for_received(1)

        # The provider sends the same callback again
        attempts = simulator.push_callback(simulator.callback_url, incoming)

        assert len(attempts) == 1, attempts
        assert attempts[0].status == OK, attempts

        received = sms.get_received()
        assert len(received) == 1, received

# ################################################################################################################################

    @pytest.mark.parametrize('provider', Providers)
    def test_a_callback_the_service_rejects_fails_and_the_resend_goes_through(self, sms:'SMSSuite', provider:'str') -> 'None':
        """ With use_queue disabled, the service's exception fails the callback, the provider resends it and the second
        attempt delivers the same event.
        """
        simulator = sms.simulator(provider)
        sms.set_refusal_count(1)

        incoming = simulator.add_incoming_text(From_Number, To_Number, 'refused once')

        assert len(simulator.callbacks) == 2, simulator.callbacks
        assert simulator.callbacks[0].status == INTERNAL_SERVER_ERROR, simulator.callbacks
        assert simulator.callbacks[1].status == OK, simulator.callbacks

        received = sms.wait_for_received(2)
        assert len(received) == 2, received

        assert received[0]['is_accepted'] is False
        assert received[1]['is_accepted'] is True

        for record in received:
            assert record['event']['id'] == incoming.message_id, record

# ################################################################################################################################

    def test_a_polling_channel_has_no_webhook(self, sms:'SMSSuite') -> 'None':

        url = sms.webhook_url(sms.polling_channel(SMS.Provider.Twilio))
        response = requests.post(url, data={'MessageSid': 'SM0'}, timeout=10)

        assert response.status_code == NOT_FOUND, (response.status_code, response.text)

# ################################################################################################################################

    def test_an_unknown_channel_has_no_webhook(self, sms:'SMSSuite') -> 'None':

        url = sms.webhook_url('test.sms.in.does-not-exist')
        response = requests.post(url, data={'MessageSid': 'SM0'}, timeout=10)

        assert response.status_code == NOT_FOUND, (response.status_code, response.text)

# ################################################################################################################################
# ################################################################################################################################
