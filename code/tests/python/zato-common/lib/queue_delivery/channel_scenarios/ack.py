# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What a caller gets back from a channel with the queue on, what the queued run of the service sees of the request,
# and that a channel with the switch off is the channel it always was.

# Zato
from zato.common.api import CHANNEL
from zato.common.audit_log.common import AuditEvent, AuditOutcome
from zato.common.util.api import make_cid_public

# Test support
from queue_delivery.channel.client import Call_Timeout, content_type_of, get_received, Refuse_Everything, set_behaviour, \
    wait_for_accepted, wait_for_received
from queue_delivery.channel.type_under_test import Channel_Orders, Channel_Plain
from queue_delivery.channel_scenarios.base import ChannelScenarioBase, order, Order_ID, sequences_of
from queue_delivery.client import get_client, wait_for_audit_events, wait_for_queue_empty

# ################################################################################################################################
# ################################################################################################################################

# The hooks of a full run of the service, in the order they ran
_full_run_hooks = ['before_handle', 'handle', 'after_handle']

# A header a caller adds and the query string it sends, both of which the queued run has to see
_caller_header = 'X-Caller'
_caller_header_value = 'queue-delivery-scenarios'
_caller_params = {'priority': 'high', 'source': 'scenario'}

# How many requests the intake scenario sends while the target refuses them all
_intake_count = 50

# What one call may take at most for the intake to count as never waiting
_intake_call_limit = Call_Timeout

# ################################################################################################################################
# ################################################################################################################################

class AckScenarios(ChannelScenarioBase):

    def test_a_queued_request_is_acknowledged_at_once_and_the_ack_is_in_the_audit_log(self) -> 'None':
        """ A call to a channel with the queue on answers 200 with the acknowledgement, which the channel's audit event records.
        """
        client = get_client()

        response = self.call(Channel_Orders, order(1))
        ack = self.ack_of(response)

        assert ack['cid'], ack
        assert content_type_of(response) == self.t.ack_content_type, response.headers

        # The queued run of the service runs under the cid the ack quotes
        received = wait_for_received(client, 1)
        assert len(received) == 1

        cid = received[0]['cid']
        assert make_cid_public(cid) == ack['cid'], (cid, ack)

        # The channel's own events - the request as it arrived and the acknowledgement that went back
        request_events = wait_for_audit_events(cid, AuditEvent.Request_Received, 1)
        assert len(request_events) == 1

        request_event = request_events[0]
        assert request_event['source'] == self.t.audit_source
        assert request_event['object_name'] == self.conn(Channel_Orders)
        assert request_event['endpoint'] == self.t.service_of(Channel_Orders)

        response_events = wait_for_audit_events(cid, AuditEvent.Response_Sent, 1)
        assert len(response_events) == 1

        response_event = response_events[0]
        assert response_event['source'] == self.t.audit_source
        assert response_event['object_name'] == self.conn(Channel_Orders)
        assert response_event['outcome'] == AuditOutcome.OK
        assert response_event['status'] == self.t.ack_status
        assert response_event['data'] == response.text, (response_event['data'], response.text)

        _ = wait_for_queue_empty(client, self.conn(Channel_Orders))

# ################################################################################################################################

    def test_the_queued_run_sees_the_request_as_it_arrived(self) -> 'None':
        """ The service's run from the queue has the method, path parameters, query string, headers and payload of the request.
        """
        client = get_client()
        document = order(1)

        response = self.call(Channel_Orders, document, headers={_caller_header: _caller_header_value}, params=_caller_params)
        ack = self.ack_of(response)

        received = wait_for_accepted(client, 1)
        assert len(received) == 1

        invocation = received[0]

        assert make_cid_public(invocation['cid']) == ack['cid'], invocation
        assert invocation['method'] == self.t.request_method, invocation
        assert invocation['path'] == self.t.url_paths[Channel_Orders], invocation
        # The channel lets query parameters override path ones, so the service's params carry both, as on a direct run
        expected_params = dict(self.t.path_params_of(Order_ID))
        expected_params.update(_caller_params)

        assert invocation['path_params'] == expected_params, invocation
        assert invocation['query'] == _caller_params, invocation
        assert invocation['headers'][_caller_header.lower()] == _caller_header_value, invocation
        assert invocation['channel_type'] == CHANNEL.HTTP_SOAP, invocation
        assert invocation['channel_name'] == self.conn(Channel_Orders), invocation
        assert invocation['hooks'] == _full_run_hooks, invocation

        self.t.check_received_request(invocation, Channel_Orders, document)

        _ = wait_for_queue_empty(client, self.conn(Channel_Orders))

# ################################################################################################################################

    def test_the_intake_never_waits_on_the_target(self) -> 'None':
        """ With the target refusing everything, every request is still acknowledged at once and all of them arrive
        in order once the target accepts.
        """
        client = get_client()
        set_behaviour(client, Refuse_Everything)

        acks = []

        for seq in range(1, _intake_count + 1):
            response = self.call(Channel_Orders, order(seq))
            ack = self.ack_of(response)
            acks.append(ack['cid'])

        # Every call returned within the client's timeout, which is what the ack being read proves,
        # and no two requests share a cid
        assert len(set(acks)) == _intake_count

        # Nothing has been accepted while the target refuses ..
        for invocation in get_received(client):
            assert invocation['is_accepted'] is False, invocation

        # .. and once it accepts, all the requests arrive, in order and once each
        set_behaviour(client, 0)

        accepted = wait_for_accepted(client, _intake_count, timeout=self.t.intake_timeout)
        assert len(accepted) == _intake_count, len(accepted)

        assert sequences_of(accepted) == list(range(1, _intake_count + 1))

        _ = wait_for_queue_empty(client, self.conn(Channel_Orders))

# ################################################################################################################################

    def test_with_the_switch_off_the_service_answers_itself(self) -> 'None':
        """ The plain channel invokes its service as the request arrives and returns the service's own response.
        """
        client = get_client()
        document = order(1)

        response = self.call(Channel_Plain, document)
        assert response.status == 200, (response.status, response.text)

        answer = self.t.read_plain_response(response)

        assert answer['is_ok'] is True
        assert answer['echo'] == Order_ID

        # The response carries the full cid, the one the service ran under
        received = get_received(client)
        assert len(received) == 1

        invocation = received[0]
        assert invocation['cid'] == answer['cid']
        assert invocation['hooks'] == _full_run_hooks

        self.t.check_received_request(invocation, Channel_Plain, document)

        # Nothing reached any queue
        assert self.queued_msg_ids(client, Channel_Plain) == []

# ################################################################################################################################
# ################################################################################################################################
