# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# Zato
from zato.common.api import SMS
from zato.common.sms.model import Status_Sent

# Live SMS
from live_sms.twilio import Error_From_Invalid, Error_To_Invalid, Magic_From_Invalid, Magic_To_Invalid

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from conftest import SMSSuite

# ################################################################################################################################
# ################################################################################################################################

# The numbers of the suite
To_Number = '+12025550101'
Rejected_Number = '+12025550199'

# The reason the three simulators that take one are told to reject the number with
Rejection_Reason = 'InvalidPhoneNumber'

# What a slow simulator takes over a request, beyond the connections' timeout of two seconds
Delay_Beyond_Timeout = 5.0

Providers = SMS.ProviderList

# The providers whose send request names the delivery callback URL
Providers_With_Callback_In_Send = (SMS.Provider.Twilio, SMS.Provider.Infobip)

# What each provider's authentication failure is reported with - Twilio names its error code, the others their HTTP status
Auth_Error_Text = {
    SMS.Provider.Twilio: '20003',
    SMS.Provider.Vonage: '401',
    SMS.Provider.Infobip: '401',
    SMS.Provider.Africas_Talking: '401',
}

# ################################################################################################################################
# ################################################################################################################################

class TestSend:

    @pytest.mark.parametrize('provider', Providers)
    def test_a_message_is_sent_and_the_provider_answers_with_its_id(self, sms:'SMSSuite', provider:'str') -> 'None':
        """ The provider accepts the message, the result has the ID the provider assigned and the simulator
        recorded exactly what the connection sent.
        """
        simulator = sms.simulator(provider)

        response = sms.send(provider, To_Number, 'hello from the suite')
        assert response['is_ok'] is True, response

        result = response['result']
        assert result['status'] == Status_Sent, result

        assert len(simulator.sends) == 1, simulator.sends
        send = simulator.sends[0]

        assert send.message_id == result['id']
        assert send.to == To_Number
        assert send.body == 'hello from the suite'

        if provider in Providers_With_Callback_In_Send:
            assert send.callback_url == sms.webhook_url(sms.webhook_channel(provider)), send
        else:
            assert send.callback_url == '', send

# ################################################################################################################################

    @pytest.mark.parametrize('provider', Providers)
    def test_an_explicit_sender_replaces_the_connection_default(self, sms:'SMSSuite', provider:'str') -> 'None':

        simulator = sms.simulator(provider)
        sender = '+12025550150'

        response = sms.send(provider, To_Number, 'with a sender', from_=sender)
        assert response['is_ok'] is True, response

        assert simulator.sends[0].from_ == sender, simulator.sends

# ################################################################################################################################

    def test_twilio_rejects_an_invalid_recipient_with_its_own_error_code(self, sms:'SMSSuite') -> 'None':

        response = sms.send(SMS.Provider.Twilio, Magic_To_Invalid, 'to nowhere')

        assert response['is_ok'] is False, response
        assert str(Error_To_Invalid) in response['error'], response

        assert sms.simulator(SMS.Provider.Twilio).sends == []

# ################################################################################################################################

    def test_twilio_rejects_an_invalid_sender_with_its_own_error_code(self, sms:'SMSSuite') -> 'None':

        response = sms.send(SMS.Provider.Twilio, To_Number, 'from nowhere', from_=Magic_From_Invalid)

        assert response['is_ok'] is False, response
        assert str(Error_From_Invalid) in response['error'], response

# ################################################################################################################################

    @pytest.mark.parametrize('provider', (SMS.Provider.Vonage, SMS.Provider.Infobip, SMS.Provider.Africas_Talking))
    def test_a_rejected_recipient_is_reported_with_the_provider_reason(self, sms:'SMSSuite', provider:'str') -> 'None':

        simulator = sms.simulator(provider)
        simulator.rejected_numbers[Rejected_Number] = Rejection_Reason

        try:
            response = sms.send(provider, Rejected_Number, 'to a rejected number')
        finally:
            del simulator.rejected_numbers[Rejected_Number]

        assert response['is_ok'] is False, response
        assert Rejection_Reason in response['error'], response

        assert simulator.sends == []

# ################################################################################################################################

    @pytest.mark.parametrize('provider', Providers)
    def test_a_provider_that_does_not_answer_in_time_fails_the_send(self, sms:'SMSSuite', provider:'str') -> 'None':

        simulator = sms.simulator(provider)
        simulator.delay = Delay_Beyond_Timeout

        response = sms.send(provider, To_Number, 'too slow')

        assert response['is_ok'] is False, response
        assert 'timed out' in response['error'].lower(), response

# ################################################################################################################################

    @pytest.mark.parametrize('provider', Providers)
    def test_a_wrong_credential_is_reported_as_the_provider_reports_it(self, sms:'SMSSuite', provider:'str') -> 'None':
        """ The simulator is told a different password, so the connection's credential is wrong from then on.
        """
        simulator = sms.simulator(provider)
        password = simulator.password
        simulator.password = password + '-changed'

        try:
            response = sms.send(provider, To_Number, 'with a wrong credential')
        finally:
            simulator.password = password

        assert response['is_ok'] is False, response
        assert Auth_Error_Text[provider] in response['error'], response
        assert len(simulator.rejections) == 1, simulator.rejections

# ################################################################################################################################
# ################################################################################################################################
