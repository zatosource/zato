# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The provider registry, the status vocabulary and the parsing of a callback body, for every provider class.

# stdlib
from unittest import main, TestCase
from urllib.parse import parse_qs, urlencode

# Zato
from zato.common.api import SMS
from zato.common.sms.model import Status_Delivered, Status_Failed, Status_Sent
from zato.server.connection.sms.africas_talking import AfricasTalkingProvider
from zato.server.connection.sms.base import get_provider_class, ProviderError
from zato.server.connection.sms.infobip import InfobipProvider
from zato.server.connection.sms.twilio import TwilioProvider
from zato.server.connection.sms.vonage import VonageProvider

# Test support
from test.zato.connection.sms.common import ctx, new_provider, Sender, To

# ################################################################################################################################
# ################################################################################################################################

class RegistryTestCase(TestCase):

    def test_every_provider_is_registered_under_its_name(self) -> 'None':

        self.assertIs(get_provider_class(SMS.Provider.Twilio), TwilioProvider)
        self.assertIs(get_provider_class(SMS.Provider.Vonage), VonageProvider)
        self.assertIs(get_provider_class(SMS.Provider.Infobip), InfobipProvider)
        self.assertIs(get_provider_class(SMS.Provider.Africas_Talking), AfricasTalkingProvider)

        with self.assertRaises(ProviderError):
            get_provider_class('no-such-provider')

# ################################################################################################################################
# ################################################################################################################################

class StatusMappingTestCase(TestCase):

    def test_an_undocumented_status_is_in_flight(self) -> 'None':

        for provider_class in (TwilioProvider, VonageProvider, InfobipProvider, AfricasTalkingProvider):
            provider = new_provider(provider_class)
            self.assertEqual(provider.map_status('something-new'), Status_Sent)

        # Each provider's status words for a delivery and a failure, in either letter case
        self.assertEqual(new_provider(TwilioProvider).map_status('Delivered'), Status_Delivered)
        self.assertEqual(new_provider(TwilioProvider).map_status('Undelivered'), Status_Failed)
        self.assertEqual(new_provider(VonageProvider).map_status('DELIVERED'), Status_Delivered)
        self.assertEqual(new_provider(VonageProvider).map_status('REJECTED'), Status_Failed)
        self.assertEqual(new_provider(InfobipProvider).map_status('DELIVERED'), Status_Delivered)
        self.assertEqual(new_provider(InfobipProvider).map_status('EXPIRED'), Status_Failed)
        self.assertEqual(new_provider(AfricasTalkingProvider).map_status('Success'), Status_Delivered)
        self.assertEqual(new_provider(AfricasTalkingProvider).map_status('Failed'), Status_Failed)

# ################################################################################################################################

    def test_a_form_body_round_trips_through_the_callback_parser(self) -> 'None':

        # A text with form-encoded characters is decoded in the event
        text = 'Order 1234 shipped & arrives tomorrow at 10:00, see https://example.test/?id=1'
        params = {'MessageSid': 'SM1', 'From': To, 'To': Sender, 'Body': text}
        raw_body = urlencode(params).encode('utf8')

        self.assertEqual(parse_qs(raw_body.decode('utf8'))['Body'], [text])

        provider = new_provider(TwilioProvider)
        event = provider.read_callback(ctx({}), raw_body)[0]

        self.assertEqual(event.body, text)

# ################################################################################################################################
# ################################################################################################################################

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
