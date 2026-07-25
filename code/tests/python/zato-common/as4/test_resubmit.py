# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# Zato
from zato.common.as4.audit import decode_payload_documents
from zato.common.as4.common import AS4Exception
from zato.common.as4.resubmit import find_connection_name, load_event, reprocess, resend
from zato.common.audit_log.api import AuditEvent, AuditLog
from zato.common.json_internal import loads

from .test_audit import audit_db, _read_events
from .test_server_connection import _connect, _make_channel, _make_wrapper, Payload, Test_CID

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist
    from .conftest import TestParties
    TestParties = TestParties

# The fixture is imported for its side effect of pointing the audit log at a database of its own.
audit_db = audit_db

# ################################################################################################################################
# ################################################################################################################################

# The correlation ids the two operator actions run under.
_Resend_CID    = 'cid-resend'
_Reprocess_CID = 'cid-reprocess'

# The correlation id the channel of the loopback pair records under.
_Channel_CID = 'test-cid'

# The party pair of the loopback exchange.
_Pair = 'party-a:party-b'

# ################################################################################################################################
# ################################################################################################################################

def _run_exchange(rsa_parties:'TestParties') -> 'any_':
    """ Runs one push over the loopback pair, both sides recording, and returns the two of them.
    """
    wrapper = _make_wrapper(rsa_parties, 'edelivery1', is_audit_log_active=True)
    channel = _make_channel(rsa_parties, 'edelivery1', is_audit_log_active=True)
    _connect(wrapper, channel)

    _ = wrapper.send(Test_CID, Payload)

    out = wrapper, channel
    return out

# ################################################################################################################################

def _first_event_of_type(event_type:'str') -> 'any_':
    """ Returns the first event of one type, which is the one the operator acts on.
    """
    for event in _read_events():
        if event['event_type'] == event_type:
            out = event
            break
    else:
        raise Exception(f'No `{event_type}` event was recorded')

    return out

# ################################################################################################################################

def _events_of_type(event_type:'str') -> 'anylist':
    """ Returns every event of one type, oldest first.
    """

    # Our response to produce
    out:'anylist' = []

    for event in _read_events():
        if event['event_type'] == event_type:
            out.append(event)

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestResend:
    """ The operator resend - a stored message delivered again as a message of its own.
    """

    def test_the_stored_payload_goes_out_as_a_message_of_its_own(self, rsa_parties:'TestParties',
        audit_db:'None') -> 'None':

        wrapper, channel = _run_exchange(rsa_parties)

        sent = _first_event_of_type(AuditEvent.Message_Sent)
        event = load_event(sent['id'])

        audit_log = AuditLog(wrapper.server.name)

        def send(candidate:'any_') -> 'any_':
            out = wrapper.resubmit(_Resend_CID, candidate)
            return out

        result = resend(event, send, audit_log, _Resend_CID)

        # The delivery went through and arrived as a message the receiving side had not seen before.
        assert result.is_ok
        assert result.message_id != sent['msg_id']

        published = channel.server.pubsub_backend.published
        assert len(published) == 2

# ################################################################################################################################

    def test_the_attempt_is_linked_to_the_message_it_was_made_from(self, rsa_parties:'TestParties',
        audit_db:'None') -> 'None':

        wrapper, _ = _run_exchange(rsa_parties)

        sent = _first_event_of_type(AuditEvent.Message_Sent)
        event = load_event(sent['id'])

        audit_log = AuditLog(wrapper.server.name)

        def send(candidate:'any_') -> 'any_':
            out = wrapper.resubmit(_Resend_CID, candidate)
            return out

        result = resend(event, send, audit_log, _Resend_CID)

        events = _events_of_type(AuditEvent.Message_Sent)
        assert len(events) == 2

        resent = events[1]

        assert resent['cid'] == _Resend_CID
        assert resent['correl_id'] == Test_CID
        assert resent['object_name'] == _Pair
        assert resent['msg_id'] == result.message_id

# ################################################################################################################################

    def test_the_attempt_carries_the_payload_so_it_can_go_out_again(self, rsa_parties:'TestParties',
        audit_db:'None') -> 'None':

        wrapper, _ = _run_exchange(rsa_parties)

        sent = _first_event_of_type(AuditEvent.Message_Sent)
        event = load_event(sent['id'])

        audit_log = AuditLog(wrapper.server.name)

        def send(candidate:'any_') -> 'any_':
            out = wrapper.resubmit(_Resend_CID, candidate)
            return out

        _ = resend(event, send, audit_log, _Resend_CID)

        resent = _events_of_type(AuditEvent.Message_Sent)[1]
        details = loads(resent['data'])

        documents = decode_payload_documents(details)
        data, content_type, _ = documents[0]

        assert data == Payload
        assert content_type == 'application/xml'

        # The business information travels with it, which is what the delivery goes out under.
        assert details['service'] == 'urn:test:service'
        assert details['action'] == 'SubmitInvoice'

# ################################################################################################################################

    def test_only_a_sent_message_can_be_resent(self, rsa_parties:'TestParties', audit_db:'None') -> 'None':

        wrapper, _ = _run_exchange(rsa_parties)

        # The receipt that closed the exchange is an event too, only not a resendable one.
        received = _first_event_of_type(AuditEvent.Receipt_Received)
        event = load_event(received['id'])

        audit_log = AuditLog(wrapper.server.name)

        def send(candidate:'any_') -> 'any_':
            out = wrapper.resubmit(_Resend_CID, candidate)
            return out

        with pytest.raises(AS4Exception, match='can be resent'):
            _ = resend(event, send, audit_log, _Resend_CID)

# ################################################################################################################################
# ################################################################################################################################

class TestReprocess:
    """ The operator reprocess - the payloads of a received message routed again.
    """

    def test_the_payloads_are_routed_again(self, rsa_parties:'TestParties', audit_db:'None') -> 'None':

        _, channel = _run_exchange(rsa_parties)

        received = _first_event_of_type(AuditEvent.Message_Received)
        event = load_event(received['id'])

        audit_log = AuditLog(channel.server.name)

        def route(user_message:'any_', payloads:'any_') -> 'anylist':
            out = channel.route_again(_Reprocess_CID, user_message, payloads)
            return out

        result = reprocess(event, route, audit_log, _Reprocess_CID)

        assert len(result.messages) == 1

        # The routed message is the one a live delivery routes, identifiers included.
        message = result.messages[0]

        assert message['message_id'] == received['msg_id']
        assert message['data'] == Payload.decode('utf8')

        published = channel.server.pubsub_backend.published
        assert len(published) == 2

# ################################################################################################################################

    def test_the_attempt_is_linked_to_the_delivery_it_was_made_from(self, rsa_parties:'TestParties',
        audit_db:'None') -> 'None':

        _, channel = _run_exchange(rsa_parties)

        received = _first_event_of_type(AuditEvent.Message_Received)
        event = load_event(received['id'])

        audit_log = AuditLog(channel.server.name)

        def route(user_message:'any_', payloads:'any_') -> 'anylist':
            out = channel.route_again(_Reprocess_CID, user_message, payloads)
            return out

        _ = reprocess(event, route, audit_log, _Reprocess_CID)

        events = _events_of_type(AuditEvent.Message_Received)
        assert len(events) == 2

        reprocessed = events[1]

        assert reprocessed['cid'] == _Reprocess_CID
        assert reprocessed['correl_id'] == _Channel_CID
        assert reprocessed['object_name'] == _Pair
        assert reprocessed['msg_id'] == received['msg_id']

# ################################################################################################################################

    def test_only_a_received_message_can_be_reprocessed(self, rsa_parties:'TestParties', audit_db:'None') -> 'None':

        _, channel = _run_exchange(rsa_parties)

        sent = _first_event_of_type(AuditEvent.Message_Sent)
        event = load_event(sent['id'])

        audit_log = AuditLog(channel.server.name)

        def route(user_message:'any_', payloads:'any_') -> 'anylist':
            out = channel.route_again(_Reprocess_CID, user_message, payloads)
            return out

        with pytest.raises(AS4Exception, match='can be reprocessed'):
            _ = reprocess(event, route, audit_log, _Reprocess_CID)

# ################################################################################################################################
# ################################################################################################################################

class TestConnectionLookup:
    """ Which connection a stored message goes back out through.
    """

    def test_the_pair_names_the_connection(self) -> 'None':

        configs = [
            {'name': 'Other', 'as4_from_party': 'party-a', 'as4_to_party': 'party-c'},
            {'name': 'Ours',  'as4_from_party': 'party-a', 'as4_to_party': 'party-b'},
        ]

        assert find_connection_name(configs, 'party-a', 'party-b') == 'Ours'

# ################################################################################################################################

    def test_a_pair_no_connection_serves_is_refused(self) -> 'None':

        configs = [{'name': 'Ours', 'as4_from_party': 'party-a', 'as4_to_party': 'party-b'}]

        with pytest.raises(AS4Exception, match='No outgoing AS4 connection matches'):
            _ = find_connection_name(configs, 'party-a', 'party-z')

# ################################################################################################################################
# ################################################################################################################################
