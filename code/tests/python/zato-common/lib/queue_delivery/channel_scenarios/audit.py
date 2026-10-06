# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The audit trail of one queued request, all of it under the cid the acknowledgement quoted - the channel's events,
# the publish, the service's runs and the delivery's outcome.

# Zato
from zato.common.api import CHANNEL
from zato.common.audit_log.common import AuditBody, AuditEvent, AuditOutcome, AuditSource
from zato.common.audit_log.service import Attribute_Channel
from zato.common.pubsub.outgoing import get_outgoing_topic_name

# Test support
from queue_delivery.channel.client import set_behaviour, wait_for_accepted
from queue_delivery.channel.type_under_test import Channel_Hooked, Channel_Orders, Hook_Response_Prefix, Orders_Max_Retries
from queue_delivery.channel_scenarios.base import ChannelScenarioBase, order
from queue_delivery.client import get_audit_attrs, get_audit_bodies, get_audit_events, get_client, is_broker_backend, \
    wait_for_audit_events, wait_for_queue_empty

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist

# ################################################################################################################################
# ################################################################################################################################

# The channel a service's audit events name as the one it ran through, for the hook and the queued run alike
_service_channel = CHANNEL.HTTP_SOAP

# ################################################################################################################################
# ################################################################################################################################

def _of_source(events:'anylist', source:'str') -> 'anylist':
    """ The events of one source, in the order they were written.
    """
    out = []

    for event in events:
        if event['source'] == source:
            out.append(event)

    return out

# ################################################################################################################################

def _of_type(events:'anylist', event_type:'str') -> 'anylist':
    """ The events of one type, in the order they were written.
    """
    out = []

    for event in events:
        if event['event_type'] == event_type:
            out.append(event)

    return out

# ################################################################################################################################
# ################################################################################################################################

class AuditScenarios(ChannelScenarioBase):

    def _check_service_events(self, events:'anylist', key:'str', expected_runs:'int') -> 'None':
        """ The service's own events of one cid - a request and a response per run, each naming the channel as the caller.
        """
        requests = _of_type(events, AuditEvent.Service_Request)
        responses = _of_type(events, AuditEvent.Service_Response)

        assert len(requests) == expected_runs, requests
        assert len(responses) == expected_runs, responses

        for event in requests + responses:
            assert event['source'] == AuditSource.Service
            assert event['object_name'] == self.t.service_of(key)
            assert event['endpoint'] == self.conn(key)

# ################################################################################################################################

    def _check_body_attrs(self, event:'anydict') -> 'None':
        """ A service event records the channel it ran through as an attribute.
        """
        bodies = get_audit_bodies(event['id'])
        assert AuditBody.Request in bodies or AuditBody.Response in bodies, bodies

        attrs = get_audit_attrs(event['id'])
        assert attrs[Attribute_Channel] == _service_channel, attrs

# ################################################################################################################################

    def test_the_audit_log_follows_a_queued_request_from_the_ack_to_the_delivery(self) -> 'None':
        """ One cid, from the request arriving through its publish and the acknowledgement, to the service's run
        from the queue and the delivery that concluded it.
        """
        client = get_client()
        conn_name = self.conn(Channel_Orders)

        response = self.call(Channel_Orders, order(1))
        ack = self.ack_of(response)

        accepted = wait_for_accepted(client, 1)
        cid = accepted[0]['cid']
        assert cid.startswith(ack['cid'])

        _ = wait_for_queue_empty(client, conn_name)

        # The delivery's conclusion is the last event written - on a broker it is written under the cid
        # of the consumer that took the message off the broker, so here it is the service's response that is waited for
        if is_broker_backend():
            _ = wait_for_audit_events(cid, AuditEvent.Service_Response, 1)
        else:
            delivered = wait_for_audit_events(cid, AuditEvent.Delivered, 1)
            assert len(delivered) == 1

        events = get_audit_events(cid)

        # The channel saw the request arrive and the acknowledgement leave ..
        channel_events = _of_source(events, self.t.audit_source)
        assert len(channel_events) == 2, channel_events

        assert channel_events[0]['event_type'] == AuditEvent.Request_Received
        assert channel_events[1]['event_type'] == AuditEvent.Response_Sent
        assert channel_events[1]['data'] == response.text

        for event in channel_events:
            assert event['object_name'] == conn_name
            assert event['endpoint'] == self.t.service_of(Channel_Orders)

        # .. the request was published to the channel's own topic ..
        topic_name = get_outgoing_topic_name(self.t.conn_type, conn_name)

        published = _of_type(events, AuditEvent.Published)
        assert len(published) == 1
        assert published[0]['source'] == AuditSource.PubSub
        assert published[0]['object_name'] == topic_name
        assert published[0]['msg_id']

        # .. the service ran once, from the queue, with the channel as its caller ..
        service_events = _of_source(events, AuditSource.Service)
        self._check_service_events(service_events, Channel_Orders, 1)

        service_response = _of_type(service_events, AuditEvent.Service_Response)[0]
        assert service_response['outcome'] == AuditOutcome.OK
        self._check_body_attrs(service_response)

        # .. and the delivery concluded with the message delivered, on the same topic and with the same id
        if not is_broker_backend():
            delivered = _of_type(events, AuditEvent.Delivered)
            assert len(delivered) == 1
            assert delivered[0]['source'] == AuditSource.PubSub
            assert delivered[0]['object_name'] == topic_name
            assert delivered[0]['msg_id'] == published[0]['msg_id']
            assert delivered[0]['outcome'] == AuditOutcome.OK

        # Nothing failed along the way
        assert _of_type(events, AuditEvent.Delivery_Failed) == []
        assert _of_type(events, AuditEvent.DLQ) == []

# ################################################################################################################################

    def test_every_refused_run_is_in_the_audit_log_under_the_callers_cid(self) -> 'None':
        """ The service's refusals and the run that accepted are all recorded under the cid of the acknowledgement.
        """
        client = get_client()
        conn_name = self.conn(Channel_Orders)

        set_behaviour(client, Orders_Max_Retries)

        response = self.call(Channel_Orders, order(1))
        ack = self.ack_of(response)

        accepted = wait_for_accepted(client, 1)
        cid = accepted[0]['cid']
        assert cid.startswith(ack['cid'])

        _ = wait_for_queue_empty(client, conn_name)

        expected_runs = Orders_Max_Retries + 1

        responses = wait_for_audit_events(cid, AuditEvent.Service_Response, expected_runs)
        assert len(responses) == expected_runs

        outcomes = []
        for event in responses:
            outcomes.append(event['outcome'])

        assert outcomes == [AuditOutcome.Error] * Orders_Max_Retries + [AuditOutcome.OK], outcomes

        # A refused run records the error it raised as a body of its own
        bodies = get_audit_bodies(responses[0]['id'])
        assert AuditBody.Error in bodies, bodies

        events = get_audit_events(cid)
        self._check_service_events(_of_source(events, AuditSource.Service), Channel_Orders, expected_runs)

        if not is_broker_backend():
            delivered = _of_type(events, AuditEvent.Delivered)
            assert len(delivered) == 1

# ################################################################################################################################

    def test_the_hook_is_a_run_of_its_own_under_the_same_cid(self) -> 'None':
        """ A hooked channel's cid has two runs of the service - the hook that built the response and the run from the queue.
        """
        client = get_client()
        conn_name = self.conn(Channel_Hooked)

        response = self.call(Channel_Hooked, order(1))
        assert response.status == 200, (response.status, response.text)

        text = self.t.read_hook_response(response)
        assert text.startswith(Hook_Response_Prefix), text

        accepted = wait_for_accepted(client, 1)
        cid = accepted[0]['cid']

        _ = wait_for_queue_empty(client, conn_name)

        responses = wait_for_audit_events(cid, AuditEvent.Service_Response, 2)
        assert len(responses) == 2

        events = get_audit_events(cid)
        self._check_service_events(_of_source(events, AuditSource.Service), Channel_Hooked, 2)

        # The hook's response is what the caller got and it was recorded as the channel's response too
        channel_responses = _of_type(_of_source(events, self.t.audit_source), AuditEvent.Response_Sent)
        assert len(channel_responses) == 1
        assert channel_responses[0]['data'] == response.text

# ################################################################################################################################
# ################################################################################################################################
