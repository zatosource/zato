# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The three shapes of a queued channel's response - the default acknowledgement, a static response and the one
# a service's hook builds - along with what the hook does and does not cost.

# stdlib
import time

# Zato
from zato.common.api import PubSub
from zato.common.audit_log.common import AuditEvent

# Test support
from queue_delivery.channel.client import accept_all, content_type_of, get_counts, redeploy_counting, Refuse_Everything, \
    set_behaviour, wait_for_accepted, wait_for_received
from queue_delivery.channel.session import Counting_Hooked_Source, Counting_Source
from queue_delivery.channel.type_under_test import Channel_Counting, Channel_Hooked, Channel_Hooked_Static, Channel_Slow_Hook, \
    Channel_Static, Channel_Static_Text, Channel_Static_XML, Hook_Response_Prefix, Slow_Hook_Delay, Static_Response_JSON, \
    Static_Response_Text, Static_Response_XML
from queue_delivery.channel_scenarios.base import ChannelScenarioBase, order
from queue_delivery.client import get_client, is_broker_backend, wait_for_audit_events, wait_for_queue_empty

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.client import AdminClient
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

# A message the target refused waits this long at most for the round that delivers it once the target accepts
_round_timeout = PubSub.Delivery.Retry_Round_Wait + 10.0

# How much earlier than the hook's delay a slow response may come back, for clocks that are not the same one
_slack = 0.2

# How many requests the shortcut scenario sends to each of its channels
_shortcut_count = 10

# A redeploy takes effect within this long
_redeploy_timeout = 60.0
_poll_interval_seconds = 0.5

# What every pub/sub message id opens with
_msg_id_prefix = PubSub.Prefix.Msg_ID

# ################################################################################################################################
# ################################################################################################################################

class ResponseScenarios(ChannelScenarioBase):

    def _check_static(self, client:'AdminClient', key:'str', expected_text:'str') -> 'None':
        """ A static channel answers with its string verbatim, in its Content-Type, and the request is in the queue.
        """
        set_behaviour(client, Refuse_Everything)

        try:
            response = self.call(key, order(1))

            assert response.status == 200, (response.status, response.text)
            assert response.text == expected_text, response.text
            assert content_type_of(response) == self.t.static_content_types[key], response.headers

            # The queued run has started while the target refuses, so the message is in the queue
            received = wait_for_received(client, 1)
            assert len(received) == 1

            if not is_broker_backend():
                assert len(self.queued_msg_ids(client, key)) == 1

        finally:
            accept_all(client)

        _ = wait_for_accepted(client, 1, timeout=_round_timeout)
        _ = wait_for_queue_empty(client, self.conn(key))

# ################################################################################################################################

    def test_a_static_json_response_is_returned_verbatim(self) -> 'None':
        """ The JSON string of the template, as it is.
        """
        self._check_static(get_client(), Channel_Static, Static_Response_JSON)

# ################################################################################################################################

    def test_a_static_xml_response_is_returned_verbatim(self) -> 'None':
        """ The XML string of the template, as it is.
        """
        self._check_static(get_client(), Channel_Static_XML, Static_Response_XML)

# ################################################################################################################################

    def test_a_static_text_response_is_returned_verbatim(self) -> 'None':
        """ The plain string of the template, as it is.
        """
        self._check_static(get_client(), Channel_Static_Text, Static_Response_Text)

# ################################################################################################################################

    def _hook_response_of(self, client:'AdminClient', key:'str') -> 'anydict':
        """ Calls a hooked channel while the target refuses and returns the hook's text along with the id of the message
        the hook saw, read from the queue where it can be browsed and from the audit log of the publish everywhere.
        """
        set_behaviour(client, Refuse_Everything)

        try:
            response = self.call(key, order(1))
            assert response.status == 200, (response.status, response.text)

            text = self.t.read_hook_response(response)
            assert text.startswith(Hook_Response_Prefix), text

            msg_id = text[len(Hook_Response_Prefix):]
            assert msg_id, text

            received = wait_for_received(client, 1)
            cid = received[0]['cid']

            # The id the hook saw is the id of the message the channel published ..
            published = wait_for_audit_events(cid, AuditEvent.Published, 1)
            assert len(published) == 1
            assert published[0]['msg_id'] == msg_id, (published[0]['msg_id'], msg_id)

            # .. and the one the delivery page lists, where the queue can be browsed
            if not is_broker_backend():
                assert self.queued_msg_ids(client, key) == [msg_id]

                page = self.browse(client, key)
                assert len(page['items']) == 1
                assert page['items'][0]['msg_id'] == msg_id

            out = {
                'text': text,
                'msg_id': msg_id,
            }

        finally:
            accept_all(client)

        _ = wait_for_accepted(client, 1, timeout=_round_timeout)
        _ = wait_for_queue_empty(client, self.conn(key))

        return out

# ################################################################################################################################

    def test_the_hook_answers_with_the_id_of_the_queued_message(self) -> 'None':
        """ The hooked channel's response is the hook's, carrying the id of the message in the queue.
        """
        _ = self._hook_response_of(get_client(), Channel_Hooked)

# ################################################################################################################################

    def test_the_hook_wins_over_a_static_response(self) -> 'None':
        """ With both a hook and a static response, the hook's payload goes back.
        """
        result = self._hook_response_of(get_client(), Channel_Hooked_Static)
        assert result['text'] != Static_Response_JSON

# ################################################################################################################################

    def test_the_hook_and_handle_run_side_by_side(self) -> 'None':
        """ A slow hook delays the response, not the delivery - handle started before the response came back.
        """
        client = get_client()

        called_at = time.monotonic()
        response = self.call(Channel_Slow_Hook, order(1))
        assert response.status == 200, (response.status, response.text)

        elapsed = response.returned_at - called_at
        assert elapsed >= Slow_Hook_Delay - _slack, elapsed

        text = self.t.read_hook_response(response)
        assert text.startswith(Hook_Response_Prefix), text

        accepted = wait_for_accepted(client, 1)
        assert len(accepted) == 1

        # The service's run from the queue began while the hook was still asleep
        handle_started_at = accepted[0]['handle_started_at']
        assert handle_started_at < response.returned_at, (handle_started_at, response.returned_at)

        _ = wait_for_queue_empty(client, self.conn(Channel_Slow_Hook))

# ################################################################################################################################

    def test_a_service_without_the_hook_is_instantiated_only_by_its_queued_run(self) -> 'None':
        """ Ten requests to the counting channel are ten instantiations once the ten runs completed, none from the channel side,
        and ten to the hooked channel are twenty - one for the hook, one for the run.
        """
        client = get_client()

        for seq in range(1, _shortcut_count + 1):
            _ = self.ack_of(self.call(Channel_Counting, order(seq)))

        _ = wait_for_queue_empty(client, self.conn(Channel_Counting))

        for seq in range(1, _shortcut_count + 1):
            response = self.call(Channel_Hooked, order(seq))
            assert response.status == 200, (response.status, response.text)

        _ = wait_for_accepted(client, _shortcut_count)
        _ = wait_for_queue_empty(client, self.conn(Channel_Hooked))

        counts = get_counts(client)
        assert counts['counting'] == _shortcut_count, counts
        assert counts['hooked'] == _shortcut_count * 2, counts

# ################################################################################################################################

    def _wait_for_counting_response(self, is_hooked:'bool') -> 'None':
        """ Blocks until the counting channel answers the way a service with the hook does, or the way one without it does.
        """
        deadline = time.monotonic() + _redeploy_timeout

        while time.monotonic() < deadline:

            response = self.call(Channel_Counting, order(1))
            assert response.status == 200, (response.status, response.text)

            if is_hooked == self.t.is_hook_response(response):
                return

            time.sleep(_poll_interval_seconds)

        raise AssertionError(f'The counting channel did not answer with is_hooked={is_hooked} within {_redeploy_timeout}s')

# ################################################################################################################################

    def test_a_redeploy_picks_the_hook_up(self) -> 'None':
        """ Once the counting service's source is replaced with one that defines the hook, the hook answers the next request,
        and once it is replaced back, the default acknowledgement does.
        """
        client = get_client()

        _ = self.ack_of(self.call(Channel_Counting, order(1)))

        redeploy_counting(client, Counting_Hooked_Source)

        try:
            self._wait_for_counting_response(is_hooked=True)

            # The counting hook answers with plain text on both transports, the body is the prefix and the message id
            response = self.call(Channel_Counting, order(2))
            assert self.t.is_hook_response(response), response.text

            text = response.text
            msg_id = text[text.index(Hook_Response_Prefix) + len(Hook_Response_Prefix):]
            assert msg_id.startswith(_msg_id_prefix), text

        finally:
            redeploy_counting(client, Counting_Source)
            self._wait_for_counting_response(is_hooked=False)

        _ = wait_for_queue_empty(client, self.conn(Channel_Counting))

# ################################################################################################################################
# ################################################################################################################################
