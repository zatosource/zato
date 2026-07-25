# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# lxml
from lxml import etree

# SQLAlchemy
from sqlalchemy import select

# pytest
import pytest

# Zato
from zato.common.as4.audit import decode_payload_documents, decode_wire_bytes
from zato.common.as4.common import AS4Exception
from zato.common.as4.ebms import build_envelope, build_receipt
from zato.common.as4.outbound import build_push_message, new_part
from zato.common.as4.profiles import new_edelivery1_pmode
from zato.common.as4.security.sign import sign_envelope
from zato.common.audit_log.api import event_table, get_audit_engine, AuditEvent, AuditOutcome, AuditSource, \
    ModuleCtx as AuditLogCtx
from zato.common.json_internal import loads

from .conftest import set_party_ids
from .test_server_connection import _connect, _make_channel, _make_wrapper, Payload, Test_CID

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from zato.common.typing_ import any_, anylist, stranydict
    from .conftest import TestParties
    TestParties = TestParties

    auditgen = Iterator[None]

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture
def audit_db(tmp_path:'os.PathLike') -> 'auditgen':
    """ Points the audit log at a SQLite file of this test's own for the duration of the test.
    """
    db_path = os.path.join(str(tmp_path), 'audit.db')

    previous = {}

    values = {
        AuditLogCtx.Env_Type: AuditLogCtx.Type_SQLite,
        AuditLogCtx.Env_Name: db_path,
    }

    for name, value in values.items():
        previous[name] = os.environ.get(name)
        os.environ[name] = value

    yield

    for name, value in previous.items():
        if value is None:
            _ = os.environ.pop(name, None)
        else:
            os.environ[name] = value

# ################################################################################################################################
# ################################################################################################################################

def _read_events(source:'str'=AuditSource.AS4) -> 'anylist':
    """ Returns every event one source wrote, oldest first, each as a dictionary
    of the columns the AS4 recording sets.
    """
    engine = get_audit_engine()

    query = select(
        event_table.c.id,
        event_table.c.event_type,
        event_table.c.object_name,
        event_table.c.cid,
        event_table.c.msg_id,
        event_table.c.correl_id,
        event_table.c.outcome,
        event_table.c.size,
        event_table.c.data,
    )
    query = query.where(event_table.c.source == source)
    query = query.order_by(event_table.c.id.asc())

    # Our response to produce
    out:'anylist' = []

    with engine.connect() as connection:
        for row in connection.execute(query):
            out.append(row._asdict())

    return out

# ################################################################################################################################

def _by_event_type(events:'anylist') -> 'stranydict':
    """ Indexes the events of one exchange by their type - one exchange writes each type once.
    """

    # Our response to produce
    out:'stranydict' = {}

    for event in events:
        out[event['event_type']] = event

    return out

# ################################################################################################################################

def _run_exchange(rsa_parties:'TestParties', *, is_audit_log_active:'any_'=True) -> 'any_':
    """ Runs one push over the loopback pair, with both sides recording or both silent.
    """
    wrapper = _make_wrapper(rsa_parties, 'edelivery1', is_audit_log_active=is_audit_log_active)
    channel = _make_channel(rsa_parties, 'edelivery1', is_audit_log_active=is_audit_log_active)
    _connect(wrapper, channel)

    out = wrapper.send(Test_CID, Payload)
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestOneExchange:
    """ What one complete push leaves in the audit log, on both sides of it.
    """

    def test_all_four_events_are_written(self, rsa_parties:'TestParties', audit_db:'any_') -> 'None':
        result = _run_exchange(rsa_parties)
        assert result.is_ok

        events = _read_events()
        by_type = _by_event_type(events)

        # The sending side wrote the message and the receipt that came back for it ..
        assert AuditEvent.Message_Sent in by_type
        assert AuditEvent.Receipt_Received in by_type

        # .. and the receiving side wrote the message and the receipt it answered with.
        assert AuditEvent.Message_Received in by_type
        assert AuditEvent.Receipt_Sent in by_type

        event_count = len(events)
        assert event_count == 4

# ################################################################################################################################

    def test_every_event_is_recorded_under_the_party_pair(self, rsa_parties:'TestParties', audit_db:'any_') -> 'None':
        _ = _run_exchange(rsa_parties)

        events = _read_events()

        for event in events:
            assert event['object_name'] == 'party-a:party-b'

# ################################################################################################################################

    def test_the_send_and_its_receipt_share_the_message_id(self, rsa_parties:'TestParties', audit_db:'any_') -> 'None':
        """ The pair the outstanding indicator works off - a receipt is stored under the id of the
        message it acknowledges rather than under its own.
        """
        result = _run_exchange(rsa_parties)

        by_type = _by_event_type(_read_events())

        message_sent = by_type[AuditEvent.Message_Sent]
        receipt_received = by_type[AuditEvent.Receipt_Received]

        assert message_sent['msg_id'] == result.message_id
        assert receipt_received['msg_id'] == result.message_id

        # The receipt has an id of its own, which is stored alongside rather than as the event's.
        details = loads(receipt_received['data'])
        assert details['receipt_message_id']
        assert details['receipt_message_id'] != result.message_id

# ################################################################################################################################

    def test_the_inbound_pair_shares_the_message_id(self, rsa_parties:'TestParties', audit_db:'any_') -> 'None':
        result = _run_exchange(rsa_parties)

        by_type = _by_event_type(_read_events())

        assert by_type[AuditEvent.Message_Received]['msg_id'] == result.message_id
        assert by_type[AuditEvent.Receipt_Sent]['msg_id'] == result.message_id

# ################################################################################################################################

    def test_every_event_carries_the_correlation_id(self, rsa_parties:'TestParties', audit_db:'any_') -> 'None':
        _ = _run_exchange(rsa_parties)

        by_type = _by_event_type(_read_events())

        # The sending side records under the cid the caller supplied ..
        assert by_type[AuditEvent.Message_Sent]['cid'] == Test_CID
        assert by_type[AuditEvent.Receipt_Received]['cid'] == Test_CID

        # .. and the receiving side under the one its own request was assigned.
        assert by_type[AuditEvent.Message_Received]['cid'] == 'test-cid'
        assert by_type[AuditEvent.Receipt_Sent]['cid'] == 'test-cid'

# ################################################################################################################################

    def test_a_successful_exchange_records_no_failures(self, rsa_parties:'TestParties', audit_db:'any_') -> 'None':
        _ = _run_exchange(rsa_parties)

        for event in _read_events():
            assert event['outcome'] == AuditOutcome.OK

# ################################################################################################################################
# ################################################################################################################################

class TestEvidence:
    """ What is kept with each event - the payloads and the bytes an exchange is reconstructed from.
    """

    def test_the_payload_is_stored_losslessly_on_both_sides(self, rsa_parties:'TestParties', audit_db:'any_') -> 'None':
        _ = _run_exchange(rsa_parties)

        by_type = _by_event_type(_read_events())

        for event_type in (AuditEvent.Message_Sent, AuditEvent.Message_Received):

            details = loads(by_type[event_type]['data'])
            documents = decode_payload_documents(details)

            assert len(documents) == 1

            data, content_type, content_id = documents[0]

            assert data == Payload
            assert content_type == 'application/xml'
            assert content_id

# ################################################################################################################################

    def test_the_readable_payload_is_stored_for_display(self, rsa_parties:'TestParties', audit_db:'any_') -> 'None':
        _ = _run_exchange(rsa_parties)

        by_type = _by_event_type(_read_events())

        details = loads(by_type[AuditEvent.Message_Sent]['data'])
        assert details['payload'] == Payload.decode('utf8')

# ################################################################################################################################

    def test_the_wire_bytes_are_kept_with_every_event(self, rsa_parties:'TestParties', audit_db:'any_') -> 'None':
        _ = _run_exchange(rsa_parties)

        for event in _read_events():

            details = loads(event['data'])
            raw_message = decode_wire_bytes(details['raw_message'])

            # Every one of the four is a SOAP envelope, either on its own or inside a multipart body.
            assert b'Envelope' in raw_message

# ################################################################################################################################

    def test_the_size_is_the_payload_size(self, rsa_parties:'TestParties', audit_db:'any_') -> 'None':
        _ = _run_exchange(rsa_parties)

        by_type = _by_event_type(_read_events())

        assert by_type[AuditEvent.Message_Sent]['size'] == len(Payload)
        assert by_type[AuditEvent.Message_Received]['size'] == len(Payload)

# ################################################################################################################################

    def test_the_service_the_action_and_the_conversation_are_stored(
        self,
        rsa_parties:'TestParties',
        audit_db:'any_',
        ) -> 'None':
        result = _run_exchange(rsa_parties)

        by_type = _by_event_type(_read_events())

        for event_type in (AuditEvent.Message_Sent, AuditEvent.Message_Received):

            event = by_type[event_type]
            details = loads(event['data'])

            assert details['service'] == 'urn:test:service'
            assert details['action'] == 'SubmitInvoice'
            assert details['conversation_id'] == result.conversation_id

            # The conversation is also what the event correlates by.
            assert event['correl_id'] == result.conversation_id

# ################################################################################################################################
# ################################################################################################################################

class TestFailures:
    """ What a refused exchange leaves behind - the evidence of a failure is evidence too.
    """

    def test_a_refused_message_is_recorded_as_an_error_on_both_sides(
        self,
        rsa_parties:'TestParties',
        audit_db:'any_',
        ) -> 'None':
        """ The channel is configured for one action and the message names another, so the channel
        answers with an error signal instead of a receipt.
        """
        wrapper = _make_wrapper(rsa_parties, 'edelivery1', is_audit_log_active=True)
        channel = _make_channel(rsa_parties, 'peppol', is_audit_log_active=True)
        _connect(wrapper, channel)

        with pytest.raises(AS4Exception):
            _ = wrapper.send(Test_CID, Payload)

        by_type = _by_event_type(_read_events())

        # The send is on record as having failed, with what the responder said about it ..
        message_sent = by_type[AuditEvent.Message_Sent]
        assert message_sent['outcome'] == AuditOutcome.Error

        details = loads(message_sent['data'])
        errors = details['errors']

        assert len(errors) == 1
        assert errors[0]['error_code'] == 'EBMS:0010'

        # .. the failure closes the pair, so the message does not read as still outstanding ..
        errors_received = by_type[AuditEvent.Receipt_Received]
        assert errors_received['outcome'] == AuditOutcome.Error
        assert errors_received['msg_id'] == message_sent['msg_id']

        # .. and the receiving side has no message of its own to show, only the signal it answered with.
        assert AuditEvent.Message_Received not in by_type
        assert AuditEvent.Receipt_Sent not in by_type

# ################################################################################################################################

    def test_a_replay_is_recorded_once(self, rsa_parties:'TestParties', audit_db:'any_') -> 'None':
        """ A replay was recorded when the message first arrived, so the second delivery of the same
        bytes adds nothing on the receiving side.
        """
        channel = _make_channel(rsa_parties, 'edelivery1', is_audit_log_active=True)

        pmode = new_edelivery1_pmode()
        set_party_ids(pmode, rsa_parties)
        pmode.service = 'urn:test:service'
        pmode.action = 'SubmitInvoice'

        body, content_type, _, _ = build_push_message(pmode, rsa_parties.sender, [new_part(Payload)])

        first = channel.handle('cid-1', body, content_type)
        second = channel.handle('cid-2', body, content_type)

        assert not first.is_duplicate
        assert second.is_duplicate

        event_count = len(_read_events())
        assert event_count == 2

# ################################################################################################################################
# ################################################################################################################################

class TestAsyncSignals:
    """ A signal that arrives on its own belongs to a message sent from here, so it closes
    the pair the sending direction opened rather than opening one of its own.
    """

    def test_an_async_receipt_closes_the_sending_pair(self, rsa_parties:'TestParties', audit_db:'any_') -> 'None':
        channel = _make_channel(rsa_parties, 'edelivery1', is_audit_log_active=True)

        pmode = new_edelivery1_pmode()

        envelope = build_envelope()
        _ = build_receipt(envelope, 'earlier-message@test', [])
        _ = sign_envelope(envelope, [], rsa_parties.sender, pmode.security)

        body = etree.tostring(envelope, xml_declaration=True, encoding='UTF-8')

        result = channel.handle('cid-1', body, 'application/soap+xml')
        assert len(result.signals) == 1

        events = _read_events()
        assert len(events) == 1

        event = events[0]

        assert event['event_type'] == AuditEvent.Receipt_Received
        assert event['outcome'] == AuditOutcome.OK

        # The message it refers to went out from here, so the pair reads in that direction -
        # the channel's own party first, the partner second.
        assert event['object_name'] == 'party-b:party-a'
        assert event['msg_id'] == 'earlier-message@test'

# ################################################################################################################################
# ################################################################################################################################

class TestToggle:
    """ The per-item switch that decides whether either side records at all.
    """

    def test_nothing_is_written_when_both_sides_are_off(self, rsa_parties:'TestParties', audit_db:'any_') -> 'None':
        result = _run_exchange(rsa_parties, is_audit_log_active=False)

        # The exchange itself is unaffected ..
        assert result.is_ok

        # .. and neither side left anything behind.
        assert _read_events() == []

# ################################################################################################################################

    def test_one_side_records_while_the_other_does_not(self, rsa_parties:'TestParties', audit_db:'any_') -> 'None':
        wrapper = _make_wrapper(rsa_parties, 'edelivery1', is_audit_log_active=True)
        channel = _make_channel(rsa_parties, 'edelivery1', is_audit_log_active=False)
        _connect(wrapper, channel)

        result = wrapper.send(Test_CID, Payload)
        assert result.is_ok

        by_type = _by_event_type(_read_events())

        # Only the sending side's half of the exchange is there.
        assert AuditEvent.Message_Sent in by_type
        assert AuditEvent.Receipt_Received in by_type
        assert AuditEvent.Message_Received not in by_type
        assert AuditEvent.Receipt_Sent not in by_type

# ################################################################################################################################

    def test_an_item_saved_before_the_flag_existed_records(self, rsa_parties:'TestParties', audit_db:'any_') -> 'None':
        """ The flag lives in an opaque attribute, so an item saved before it existed carries a null,
        which reads as never having been turned off.
        """
        result = _run_exchange(rsa_parties, is_audit_log_active=None)

        assert result.is_ok

        event_count = len(_read_events())
        assert event_count == 4

# ################################################################################################################################
# ################################################################################################################################
