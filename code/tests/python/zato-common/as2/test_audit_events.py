# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import timedelta

# cryptography
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat

# httpx
import httpx

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.common.as2.audit import decode_raw_mime
from zato.common.as2.inbound import handle
from zato.common.as2.mdn import normalize_message_id
from zato.common.as2.outbound import build_message
from zato.common.as2.partnership import new_partnership
from zato.common.as2.reconcile import MDNReconciler
from zato.common.as2.resubmit import load_event, resend
from zato.common.audit_log.api import AuditEvent, AuditOutcome, AuditSource, event_table, get_audit_engine
from zato.common.ext.bunch import Bunch
from zato.common.json_internal import loads
from zato.common.typing_ import cast_
from zato.common.util.api import utcnow
from zato.server.connection.as2 import AS2ChannelRuntime
from zato.server.generic.api.outconn_as2 import _AS2Connection

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    from zato.server.base.parallel import ParallelServer
    from .conftest import TestParties
    ParallelServer = ParallelServer
    TestParties = TestParties

# ################################################################################################################################
# ################################################################################################################################

_sender_identifier   = 'ZatoRetail'
_receiver_identifier = 'PartnerCorp'

_payload = (
    b'ISA*00*          *00*          *ZZ*ZATORETAIL     *ZZ*PARTNERCORP    '
    + b'*260709*1200*U*00401*000000001*0*P*>~GS*PO*ZATORETAIL*PARTNERCORP*20260709*1200*1*X*004010~'
    + b'ST*850*0001~BEG*00*NE*4523891**20260709~SE*3*0001~GE*1*1~IEA*1*000000001~'
)

# ################################################################################################################################
# ################################################################################################################################

def _key_to_pem(key:'any_') -> 'any_':
    out = key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption()).decode('ascii')
    return out

# ################################################################################################################################

def _certificate_to_pem(certificate:'any_') -> 'any_':
    out = certificate.public_bytes(Encoding.PEM).decode('ascii')
    return out

# ################################################################################################################################

def _load_events(event_type:'any_'=None) -> 'any_':
    """ Reads all the AS2 audit events back from the per-test database, oldest first.
    """
    statement = select(
        event_table.c.event_type,
        event_table.c.object_name,
        event_table.c.msg_id,
        event_table.c.cid,
        event_table.c.correl_id,
        event_table.c.outcome,
        event_table.c.data,
    ).where(event_table.c.source == AuditSource.AS2).order_by(event_table.c.id)

    engine = get_audit_engine()

    with engine.connect() as connection:
        result = connection.execute(statement)
        rows = result.fetchall()

    out = []

    for row in rows:
        item = Bunch()
        item.event_type = row[0]
        item.object_name = row[1]
        item.msg_id = row[2]
        item.cid = row[3]
        item.correl_id = row[4]
        item.outcome = row[5]
        item.details = loads(row[6])

        if event_type:
            if item.event_type != event_type:
                continue

        out.append(item)

    return out

# ################################################################################################################################
# ################################################################################################################################

class _FakeOutconnServer:
    """ Just enough of a server for the outgoing connection - decryption is the identity
    function because the test configuration stores its PEMs in the clear.
    """
    name = 'test-server'

    def decrypt(self, value:'any_') -> 'any_':
        return value

# ################################################################################################################################

def _connection_config(parties:'TestParties', **overrides:'any_') -> 'any_':
    """ The flat configuration dict of one Dashboard-managed AS2 connection.
    """
    sender_key_pem = _key_to_pem(parties.sender.signing_key)
    sender_certificate_pem = _certificate_to_pem(parties.sender.signing_certificate_chain[0])
    receiver_certificate_pem = _certificate_to_pem(parties.receiver.signing_certificate_chain[0])

    out = Bunch()

    out['id'] = 1
    out['name'] = 'PartnerCorp AS2'
    out['is_active'] = True
    out['type_'] = 'outconn-as2'
    out['username'] = ''
    out['secret'] = ''
    out['pool_size'] = 1
    out['queue_build_cap'] = 30

    out['as2_from'] = _sender_identifier
    out['as2_to'] = _receiver_identifier
    out['endpoint_url'] = 'https://partnercorp.example.com/as2'

    out['isa_qualifier'] = ''
    out['isa_id'] = ''
    out['gs_id'] = ''
    out['unb_id'] = ''

    out['sign_algorithm'] = ''
    out['encryption_algorithm'] = ''
    out['mdn_mode'] = ''
    out['async_mdn_url'] = ''
    out['subject'] = ''
    out['content_type'] = ''
    out['as2_version'] = ''
    out['content_transfer_encoding'] = ''
    out['http_transfer_mode'] = ''
    out['inbound_topic'] = ''
    out['inbound_service'] = ''

    out['sign'] = True
    out['encrypt'] = True
    out['compress'] = False
    out['compress_before_signing'] = True
    out['mdn_signed'] = True
    out['preserve_filename'] = False
    out['verify_tls'] = True
    out['force_base64'] = False
    out['prevent_canonicalization'] = False
    out['warn_on_duplicate_filename'] = False
    out['is_audit_log_active'] = True

    out['http_timeout_seconds'] = 0
    out['chunked_threshold_bytes'] = 0
    out['ack_overdue_after'] = 0
    out['resend_max_retries'] = 0

    out['as2_partner_cert'] = receiver_certificate_pem
    out['as2_partner_next_cert'] = ''
    out['as2_partner_next_cert_from'] = ''

    out['as2_signing_key'] = sender_key_pem
    out['as2_signing_cert_chain'] = sender_certificate_pem
    out['as2_decryption_key'] = sender_key_pem
    out['as2_next_decryption_key'] = ''
    out['as2_next_decryption_cert'] = ''
    out['as2_peer_signing_cert'] = ''
    out['as2_peer_encryption_cert'] = ''
    out['as2_trust_anchors'] = ''

    out.update(overrides)

    return out

# ################################################################################################################################

def _new_mock_client(parties:'TestParties') -> 'any_':
    """ Wires the receiving side's real inbound pipeline behind an HTTP mock transport.
    """
    receiver_partnership = new_partnership()
    receiver_partnership.as2_from = _receiver_identifier
    receiver_partnership.as2_to = _sender_identifier

    def _handler(request:'httpx.Request') -> 'any_':

        body = request.read()

        result = handle(body, dict(request.headers), [receiver_partnership], parties.receiver)

        response = httpx.Response(result.status_code, content=result.body, headers=result.headers)
        return response

    transport = httpx.MockTransport(_handler)

    out = httpx.Client(transport=transport)
    return out

# ################################################################################################################################

def _make_connection(parties:'TestParties', **overrides:'any_') -> 'any_':
    """ Builds one AS2 connection over a mock wire.
    """
    server = _FakeOutconnServer()
    config = _connection_config(parties, **overrides)

    out = _AS2Connection(config, server)

    # The mock wire replaces the connection's own HTTP client.
    out.http_client.close()
    out.http_client = _new_mock_client(parties)

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestOutboundEvidence:

    def test_send_records_the_full_evidence_tuple(self, parties:'TestParties') -> 'None':

        connection = _make_connection(parties)
        result = connection.send('cid-1', _payload, 'orders-850.edi')

        assert result.is_ok

        # The delivery landed as one message-sent event ..
        sent_events = _load_events(AuditEvent.Message_Sent)
        assert len(sent_events) == 1

        event = sent_events[0]

        # .. filed under the identity pair with the normalized Message-ID ..
        assert event.object_name == f'{_sender_identifier}:{_receiver_identifier}'
        assert event.msg_id == normalize_message_id(result.message_id)
        assert event.cid == 'cid-1'

        # .. carrying the MIC computed at send time, algorithm included ..
        assert event.details['mic'] == result.mic
        assert 'sha-256' in event.details['mic']

        # .. the complete raw MIME body that went over the wire ..
        raw_mime = decode_raw_mime(event.details['raw_mime'])
        assert raw_mime == result.request_body

        # .. and the clear payload with its filename, for a later resend.
        assert event.details['payload'] == _payload.decode('utf8')
        assert event.details['filename'] == 'orders-850.edi'

# ################################################################################################################################

    def test_the_sync_mdn_is_recorded_and_closes_the_exchange(self, parties:'TestParties') -> 'None':

        connection = _make_connection(parties)
        result = connection.send('cid-1', _payload)

        assert result.is_ok

        # The receipt landed as one mdn-received event ..
        mdn_events = _load_events(AuditEvent.MDN_Received)
        assert len(mdn_events) == 1

        event = mdn_events[0]

        # .. reporting clean processing, with the raw MDN bytes as the evidence ..
        assert event.outcome == AuditOutcome.OK
        assert event.details['disposition'] == 'processed'

        raw_mime = decode_raw_mime(event.details['raw_mime'])
        assert raw_mime == result.response_body

        # .. and the exchange is closed for reconciliation.
        reconciler = MDNReconciler('test-server')
        cutoff = utcnow() + timedelta(seconds=1)

        assert reconciler.outstanding(cutoff) == []

# ################################################################################################################################

    def test_an_unconfirmed_delivery_records_an_error_mdn(self, parties:'TestParties') -> 'None':

        # The receiver does not know this sender, so its MDN reports an error disposition.
        connection = _make_connection(parties, as2_from='UnknownSender')
        result = connection.send('cid-1', _payload)

        assert not result.is_ok

        mdn_events = _load_events(AuditEvent.MDN_Received)
        assert len(mdn_events) == 1

        event = mdn_events[0]

        assert event.outcome == AuditOutcome.Error
        assert event.details['modifier_kind'] == 'error'

# ################################################################################################################################

    def test_needs_audit_off_records_nothing(self, parties:'TestParties') -> 'None':

        connection = _make_connection(parties)
        result = connection.send('cid-1', _payload, needs_audit=False)

        assert result.is_ok
        assert _load_events() == []

# ################################################################################################################################
# ################################################################################################################################

class TestResendEvidence:

    def test_resend_records_one_linked_attempt_without_duplicates(self, parties:'TestParties') -> 'None':

        connection = _make_connection(parties)

        # The original delivery records itself ..
        original = connection.send('cid-original', _payload)
        assert original.is_ok

        sent_events = _load_events(AuditEvent.Message_Sent)
        assert len(sent_events) == 1

        # .. the stored event is what the operator resend runs on ..
        engine = get_audit_engine()

        with engine.connect() as db_connection:
            statement = select(event_table.c.id).where(event_table.c.event_type == AuditEvent.Message_Sent)
            db_result = db_connection.execute(statement)
            event_id = db_result.scalar()

        event = load_event(event_id)

        # .. the resend turns the connection's own recording off, the way the resend service does.
        def send(payload:'any_', filename:'any_') -> 'any_':
            out = connection.send('cid-resend', payload, filename, needs_audit=False)
            return out

        reconciler = MDNReconciler('test-server')
        result = resend(event, send, reconciler, 'cid-resend')

        assert result.is_ok

        # Exactly one new message-sent event exists, linked to the original by its CID ..
        sent_events = _load_events(AuditEvent.Message_Sent)
        assert len(sent_events) == 2

        resend_event = sent_events[1]
        assert resend_event.cid == 'cid-resend'
        assert resend_event.correl_id == 'cid-original'

        # .. with the raw MIME of the new attempt stored as evidence ..
        raw_mime = decode_raw_mime(resend_event.details['raw_mime'])
        assert raw_mime == result.request_body

        # .. and both exchanges closed by their synchronous MDNs.
        mdn_events = _load_events(AuditEvent.MDN_Received)
        assert len(mdn_events) == 2

# ################################################################################################################################
# ################################################################################################################################

class _FakeConfigManager:
    def __init__(self) -> 'None':

        # The live per-type dict of AS2 outgoing connection configs, keyed by name
        self.outconn_as2 = {}

# ################################################################################################################################

class _FakePubSub:
    def __init__(self) -> 'None':
        self.published = []

# ################################################################################################################################

    def publish(self, topic:'any_', message:'any_', cid:'any_'='', correl_id:'any_'='') -> 'None':
        self.published.append((topic, message))

# ################################################################################################################################

class _FakeChannelServer:
    """ Just enough of a server for the channel runtime.
    """
    name = 'test-server'

    def __init__(self) -> 'None':
        self.invoked = []
        self.config_manager = _FakeConfigManager()
        self.pubsub_backend = _FakePubSub()

# ################################################################################################################################

    def decrypt(self, value:'any_') -> 'any_':
        return value

# ################################################################################################################################

    def invoke(self, service_name:'any_', message:'any_') -> 'None':
        self.invoked.append((service_name, message))

# ################################################################################################################################

def _partnership_config() -> 'any_':
    """ The flat configuration dict of one Dashboard-managed AS2 connection,
    as the receiving side sees the relationship.
    """
    out = {
        'type_': 'outconn-as2',

        # The identities compare crosswise on inbound - as2_from is our own identifier.
        'as2_from': _receiver_identifier,
        'as2_to': _sender_identifier,

        'isa_qualifier': '',
        'isa_id': '',
        'gs_id': '',
        'unb_id': '',

        'endpoint_url': 'https://zatoretail.example.com/zato/as2',
        'sign_algorithm': '',
        'encryption_algorithm': '',
        'mdn_mode': '',
        'async_mdn_url': '',
        'subject': '',
        'content_type': '',
        'as2_version': '',
        'content_transfer_encoding': '',
        'http_transfer_mode': '',
        'inbound_topic': '',
        'inbound_service': '',

        'sign': True,
        'encrypt': True,
        'compress': False,
        'compress_before_signing': True,
        'mdn_signed': True,
        'preserve_filename': False,
        'verify_tls': True,
        'force_base64': False,
        'prevent_canonicalization': False,
        'warn_on_duplicate_filename': False,
        'is_audit_log_active': True,

        'http_timeout_seconds': 0,
        'chunked_threshold_bytes': 0,
        'ack_overdue_after': 0,
        'resend_max_retries': 0,

        'as2_partner_cert': '',
        'as2_partner_next_cert': '',
        'as2_partner_next_cert_from': '',
    }

    return out

# ################################################################################################################################

def _channel_config(parties:'TestParties') -> 'any_':
    """ The channel item of one AS2 channel, with the receiver's keys pasted in as PEMs.
    """
    receiver_key_pem = _key_to_pem(parties.receiver.signing_key)
    receiver_certificate_pem = _certificate_to_pem(parties.receiver.signing_certificate_chain[0])

    out = {
        'name': 'zato.channel.as2',
        'service_name': None,
        'as2_inbound_topic': None,
        'as2_duplicate_window_days': None,

        'as2_signing_key': receiver_key_pem,
        'as2_signing_cert_chain': receiver_certificate_pem,
        'as2_decryption_key': receiver_key_pem,
        'as2_next_decryption_key': '',
        'as2_next_decryption_cert': '',
        'as2_peer_signing_cert': _certificate_to_pem(parties.sender.signing_certificate_chain[0]),
        'as2_peer_encryption_cert': _certificate_to_pem(parties.sender.signing_certificate_chain[0]),
        'as2_trust_anchors': '',
    }

    return out

# ################################################################################################################################

def _make_runtime(parties:'TestParties', with_partnership:'any_'=True) -> 'any_':
    """ Builds a channel runtime on a fake server.
    """
    server = cast_('ParallelServer', _FakeChannelServer())

    if with_partnership:
        server.config_manager.outconn_as2['PartnerCorp AS2'] = _partnership_config()

    out = AS2ChannelRuntime(server, _channel_config(parties))
    return out

# ################################################################################################################################

def _build_wire_message(parties:'TestParties') -> 'any_':
    """ Builds one real AS2 message the way the sending side would.
    """
    partnership = new_partnership()
    partnership.as2_from = _sender_identifier
    partnership.as2_to = _receiver_identifier

    body, headers, message_id, mic = build_message(partnership, parties.sender, _payload)

    out = body, headers, message_id, mic
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestInboundEvidence:

    def test_an_accepted_message_records_message_received_and_mdn_sent(self, parties:'TestParties') -> 'None':

        runtime = _make_runtime(parties)

        body, headers, message_id, _ = _build_wire_message(parties)
        result = runtime.handle('cid-1', body, headers)

        assert not result.is_error

        # The arrival landed as one message-received event ..
        received_events = _load_events(AuditEvent.Message_Received)
        assert len(received_events) == 1

        event = received_events[0]

        # .. filed under the pair as it arrived on the wire ..
        assert event.object_name == f'{_sender_identifier}:{_receiver_identifier}'
        assert event.msg_id == normalize_message_id(message_id)
        assert event.outcome == AuditOutcome.OK

        # .. with the complete raw MIME body exactly as received ..
        raw_mime = decode_raw_mime(event.details['raw_mime'])
        assert raw_mime == body

        # .. the MIC computed over the received content ..
        assert event.details['mic'] == result.mic
        assert event.details['mic']

        # .. and the clear payload for a later reprocess.
        assert event.details['payload'] == _payload.decode('utf8')

        # The receipt that went back landed as one mdn-sent event, with its own raw bytes.
        mdn_events = _load_events(AuditEvent.MDN_Sent)
        assert len(mdn_events) == 1

        mdn_event = mdn_events[0]

        assert mdn_event.details['disposition'] == 'processed'
        assert mdn_event.details['modifier_kind'] == ''

        mdn_raw_mime = decode_raw_mime(mdn_event.details['raw_mime'])
        assert mdn_raw_mime == result.body

# ################################################################################################################################

    def test_a_rejected_message_records_the_error_disposition(self, parties:'TestParties') -> 'None':

        # No partnership is configured, so the message is rejected.
        runtime = _make_runtime(parties, with_partnership=False)

        body, headers, _, _ = _build_wire_message(parties)
        result = runtime.handle('cid-1', body, headers)

        assert result.is_error

        # The arrival was still recorded, with the error modifier as its outcome detail ..
        received_events = _load_events(AuditEvent.Message_Received)
        assert len(received_events) == 1

        event = received_events[0]

        assert event.outcome == AuditOutcome.Error
        assert event.details['error'] == 'unknown-trading-relationship'

        # .. and so was the explanatory MDN that went back.
        mdn_events = _load_events(AuditEvent.MDN_Sent)
        assert len(mdn_events) == 1

        mdn_event = mdn_events[0]

        assert mdn_event.outcome == AuditOutcome.Error
        assert mdn_event.details['modifier_kind'] == 'error'
        assert mdn_event.details['modifier'] == 'unknown-trading-relationship'

# ################################################################################################################################

    def test_a_replay_records_no_new_events(self, parties:'TestParties') -> 'None':

        runtime = _make_runtime(parties)

        body, headers, _, _ = _build_wire_message(parties)

        first = runtime.handle('cid-1', body, headers)
        assert not first.is_duplicate

        # The replay reuses the same body and headers, Message-ID included.
        second = runtime.handle('cid-2', body, headers)
        assert second.is_duplicate

        # Only the first delivery left its pair of events behind.
        received_events = _load_events(AuditEvent.Message_Received)
        assert len(received_events) == 1

        mdn_events = _load_events(AuditEvent.MDN_Sent)
        assert len(mdn_events) == 1

# ################################################################################################################################
# ################################################################################################################################
