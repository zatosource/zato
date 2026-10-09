# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from time import monotonic, sleep

# pytest
import pytest

# Zato
from zato.common.api import SMS
from zato.common.sms.model import Kind_Message, Kind_Status, Status_Delivered

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from conftest import SMSSuite
    from zato.common.typing_ import anylist, strlist

# ################################################################################################################################
# ################################################################################################################################

To_Number = '+12025550101'
From_Number = '+12025550102'

Providers = SMS.ProviderList

# The providers whose poll reads a paged listing
Paging_Providers = (SMS.Provider.Twilio, SMS.Provider.Vonage, SMS.Provider.Infobip)

# The delivered status in each provider's own vocabulary
Delivered_Status = {
    SMS.Provider.Twilio: 'delivered',
    SMS.Provider.Vonage: 'delivered',
    SMS.Provider.Infobip: 'DELIVERED',
    SMS.Provider.Africas_Talking: 'Success',
}

# The providers whose poll reads delivery reports as well as incoming texts
Providers_Polling_Reports = (SMS.Provider.Twilio, SMS.Provider.Vonage, SMS.Provider.Infobip)

# The Reports API filters by the second, so one second separates a window's edges
Window_Gap = 1.1

Header_Channel = 'zato-sms-channel'

# ################################################################################################################################
# ################################################################################################################################

def _message_ids(received:'anylist') -> 'strlist':
    out = []
    for record in received:
        if record['event']['kind'] == Kind_Message:
            out.append(record['event']['id'])
    return out

# ################################################################################################################################

def _polled_records(sms:'SMSSuite', provider:'str') -> 'anylist':
    """ The records delivered by a provider's polling channel. The webhook channel's records are excluded,
    as a send names the webhook channel as its delivery callback.
    """
    out = []
    channel_name = sms.polling_channel(provider)

    for record in sms.get_received():
        if record['headers'][Header_Channel] == channel_name:
            out.append(record)

    return out

# ################################################################################################################################

def _wait_for_polled(sms:'SMSSuite', provider:'str', count:'int', timeout:'float'=15.0) -> 'anylist':
    deadline = monotonic() + timeout

    while True:
        out = _polled_records(sms, provider)

        if len(out) >= count:
            return out

        if monotonic() > deadline:
            raise AssertionError(f'Expected {count} polled record(s) within {timeout}s, found {len(out)}: {out}')

        sleep(0.1)

# ################################################################################################################################

def _record_poll_window(sms:'SMSSuite', provider:'str') -> 'None':
    """ Runs a first poll, which records the start of the channel's window.
    """
    sleep(Window_Gap)
    sms.poll(provider)
    sms.clear()
    sleep(Window_Gap)

# ################################################################################################################################
# ################################################################################################################################

class TestPolling:

    @pytest.fixture(autouse=True)
    def callbacks_unregistered(self, sms:'SMSSuite') -> 'None':
        """ Unregisters the simulators' callback URLs, as these tests exercise the polling channels.
        """
        for item in sms.simulators.all:
            item.register_callback('')

# ################################################################################################################################

    @pytest.mark.parametrize('provider', Providers)
    def test_a_poll_reads_incoming_texts_once(self, sms:'SMSSuite', provider:'str') -> 'None':

        simulator = sms.simulator(provider)
        _record_poll_window(sms, provider)

        first = simulator.add_incoming_text(From_Number, To_Number, 'first')
        second = simulator.add_incoming_text(From_Number, To_Number, 'second')

        sleep(Window_Gap)
        sms.poll(provider)

        received = sms.wait_for_received(2)
        ids = _message_ids(received)
        assert sorted(ids) == sorted([first.message_id, second.message_id]), received

        for record in received:
            assert record['headers'][Header_Channel] == sms.polling_channel(provider), record
            assert record['event']['from_'] == From_Number, record

        # A second poll delivers no event
        sleep(Window_Gap)
        sms.poll(provider)
        sleep(Window_Gap)

        assert len(sms.get_received()) == 2, sms.get_received()

# ################################################################################################################################

    @pytest.mark.parametrize('provider', Providers_Polling_Reports)
    def test_a_poll_reads_the_delivery_report_of_a_sent_message(self, sms:'SMSSuite', provider:'str') -> 'None':

        simulator = sms.simulator(provider)
        _record_poll_window(sms, provider)

        response = sms.send(provider, To_Number, 'report by poll')
        message_id = response['result']['id']

        _ = simulator.set_status(message_id, Delivered_Status[provider])

        sleep(Window_Gap)
        sms.poll(provider)

        received = _wait_for_polled(sms, provider, 1)

        delivered = []
        for record in received:
            event = record['event']
            if event['kind'] == Kind_Status and event['id'] == message_id and event['status'] == Status_Delivered:
                delivered.append(event)

        assert len(delivered) == 1, received

# ################################################################################################################################

    @pytest.mark.parametrize('provider', Paging_Providers)
    def test_a_poll_that_fails_before_completion_loses_nothing_and_repeats_nothing(self, sms:'SMSSuite', provider:'str') -> 'None':
        """ Pages of one entry and a failure on the second request - the first page is delivered before the failure,
        the next poll continues from the recorded state and every text is delivered exactly once.
        """
        simulator = sms.simulator(provider)
        _record_poll_window(sms, provider)

        expected = []
        for seq in range(3):
            incoming = simulator.add_incoming_text(From_Number, To_Number, f'text {seq}')
            expected.append(incoming.message_id)

        simulator.page_size = 1
        simulator.successes_before_failure = 1
        simulator.failures_left = 1

        sleep(Window_Gap)

        with pytest.raises(Exception):
            sms.poll(provider)

        after_failure = sms.wait_for_received(1)
        assert len(_message_ids(after_failure)) == 1, after_failure

        sleep(Window_Gap)
        sms.poll(provider)

        received = sms.wait_for_received(3)
        ids = _message_ids(received)

        assert sorted(ids) == sorted(expected), received
        assert len(ids) == len(set(ids)), ids

# ################################################################################################################################

    @pytest.mark.parametrize('provider', Providers)
    def test_an_event_the_service_rejects_is_handed_over_again_by_a_later_poll(self, sms:'SMSSuite', provider:'str') -> 'None':
        """ With use_queue disabled, the service's exception fails the poll, the event is not recorded as received
        and the next poll delivers it again.
        """
        if provider == SMS.Provider.Infobip:
            pytest.skip('An Infobip pull consumes what it returns, so a rejected event is not readable again')

        simulator = sms.simulator(provider)
        _record_poll_window(sms, provider)

        incoming = simulator.add_incoming_text(From_Number, To_Number, 'rejected once')
        sms.set_refusal_count(1)

        sleep(Window_Gap)

        with pytest.raises(Exception):
            sms.poll(provider)

        refused = sms.wait_for_received(1)
        assert refused[0]['is_accepted'] is False, refused

        sleep(Window_Gap)
        sms.poll(provider)

        received = sms.wait_for_received(2)
        assert received[1]['is_accepted'] is True, received
        assert received[1]['event']['id'] == incoming.message_id, received

# ################################################################################################################################

    def test_a_poll_of_a_webhook_channel_does_nothing(self, sms:'SMSSuite') -> 'None':

        simulator = sms.simulators.twilio
        _ = simulator.add_incoming_text(From_Number, To_Number, 'not for polling')

        request = {SMS.Scheduler.Extra_Conn_Name: sms.webhook_channel(SMS.Provider.Twilio)}
        _ = sms.client.invoke(SMS.Scheduler.Dispatch_Service, request)

        sleep(Window_Gap)
        assert sms.get_received() == []

# ################################################################################################################################
# ################################################################################################################################
