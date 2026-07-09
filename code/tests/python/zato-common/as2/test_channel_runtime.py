# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from http.client import OK

# cryptography
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat

# Zato
from zato.common.api import AS2
from zato.common.as2.common import AS2Error
from zato.common.as2.outbound import build_message
from zato.common.as2.partnership import new_partnership
from zato.common.audit_log.api import ModuleCtx as AuditLogCtx
from zato.server.connection.as2 import AS2ChannelRuntime

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

def _key_to_pem(key):
    out = key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption()).decode('ascii')
    return out

# ################################################################################################################################

def _certificate_to_pem(certificate):
    out = certificate.public_bytes(Encoding.PEM).decode('ascii')
    return out

# ################################################################################################################################
# ################################################################################################################################

class _FakeConfigStore:
    def __init__(self):
        self.generic_connection = {}

# ################################################################################################################################

class _FakeConfigManager:
    def __init__(self):
        self.config_store = _FakeConfigStore()

# ################################################################################################################################

class _FakePubSub:
    def __init__(self):
        self.published = []

    def publish(self, topic, message, cid='', correl_id=''):
        self.published.append((topic, message))

# ################################################################################################################################

class _FakeServer:
    """ Just enough of a server for the channel runtime - decryption is the identity function
    because the test configuration stores its PEMs in the clear.
    """
    name = 'test-server'

    def __init__(self):
        self.invoked = []
        self.config_manager = _FakeConfigManager()
        self.pubsub_redis = _FakePubSub()

    def decrypt(self, value):
        return value

    def invoke(self, service_name, message):
        self.invoked.append((service_name, message))

# ################################################################################################################################
# ################################################################################################################################

def _partnership_config(inbound_topic='', inbound_service=''):
    """ The flat configuration dict of one Dashboard-managed AS2 connection,
    as the receiving side sees the relationship.
    """
    out = {
        'type_': 'outconn-as2',

        # The identities compare crosswise on inbound - as2_from is our own identifier.
        'as2_from': _receiver_identifier,
        'as2_to': _sender_identifier,

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
        'inbound_topic': inbound_topic,
        'inbound_service': inbound_service,

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

        'http_timeout_seconds': 0,
        'chunked_threshold_bytes': 0,
        'ack_overdue_after': 0,
        'resend_max_retries': 0,
    }

    return out

# ################################################################################################################################

def _channel_config(parties, service_name=None, inbound_topic=None):
    """ The channel item of one AS2 channel, with the receiver's keys pasted in as PEMs.
    """
    receiver_key_pem = _key_to_pem(parties.receiver.signing_key)
    receiver_certificate_pem = _certificate_to_pem(parties.receiver.signing_certificate_chain[0])

    out = {
        'name': 'zato.channel.as2',
        'service_name': service_name,
        'as2_inbound_topic': inbound_topic,
        'as2_duplicate_window_days': None,

        'as2_signing_key': receiver_key_pem,
        'as2_signing_cert_chain': receiver_certificate_pem,
        'as2_decryption_key': receiver_key_pem,
        'as2_peer_signing_cert': _certificate_to_pem(parties.sender.signing_certificate_chain[0]),
        'as2_peer_encryption_cert': _certificate_to_pem(parties.sender.signing_certificate_chain[0]),
        'as2_trust_anchors': '',
    }

    return out

# ################################################################################################################################

def _make_runtime(
    tmp_path,
    parties,
    service_name=None,
    channel_topic=None,
    with_partnership=True,
    partner_topic='',
    partner_service='',
    ):
    """ Builds a channel runtime on a fake server with a per-test SQLite audit database.
    """
    db_path = os.path.join(str(tmp_path), 'audit.db')

    os.environ[AuditLogCtx.Env_Type] = AuditLogCtx.Type_SQLite
    os.environ[AuditLogCtx.Env_Name] = db_path

    server = _FakeServer()

    if with_partnership:
        config = _partnership_config(inbound_topic=partner_topic, inbound_service=partner_service)
        server.config_manager.config_store.generic_connection['PartnerCorp AS2'] = {'config': config}

    runtime = AS2ChannelRuntime(server, _channel_config(parties, service_name, channel_topic))

    out = server, runtime
    return out

# ################################################################################################################################

def _cleanup_env() -> 'None':
    _ = os.environ.pop(AuditLogCtx.Env_Type, None)
    _ = os.environ.pop(AuditLogCtx.Env_Name, None)

# ################################################################################################################################

def _build_wire_message(parties, message_id=None):
    """ Builds one real AS2 message the way the sending side would.
    """
    partnership = new_partnership()
    partnership.as2_from = _sender_identifier
    partnership.as2_to = _receiver_identifier

    body, headers, message_id, mic = build_message(partnership, parties.sender, _payload, message_id=message_id)

    out = body, headers, message_id, mic
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestRouting:

    def test_default_topic_when_nothing_else_is_configured(self, parties, tmp_path):
        try:
            server, runtime = _make_runtime(tmp_path, parties)

            body, headers, message_id, _ = _build_wire_message(parties)
            result = runtime.handle('cid-1', body, headers)

            assert not result.is_error
            assert result.status_code == OK

            # The one document went to the default AS2 topic ..
            assert server.invoked == []
            assert len(server.pubsub_redis.published) == 1

            topic, message = server.pubsub_redis.published[0]
            assert topic == AS2.Default.Inbound_Topic

            # .. carrying the AS2 identities and the payload ..
            assert message['message_id'] == result.message_id
            assert message['as2_from'] == _sender_identifier
            assert message['as2_to'] == _receiver_identifier
            assert message['data'] == _payload.decode('utf8')

            # .. plus the EDI envelope identifiers routing and reporting key on.
            assert message['edi']['format'] == 'x12'
            assert message['edi']['doc_type'] == '850'
            assert message['edi']['sender_id'] == 'ZATORETAIL'
            assert message['edi']['interchange_control_number'] == '000000001'

        finally:
            _cleanup_env()

    def test_channel_topic_overrides_the_default(self, parties, tmp_path):
        try:
            server, runtime = _make_runtime(tmp_path, parties, channel_topic='orders.custom')

            body, headers, _, _ = _build_wire_message(parties)
            result = runtime.handle('cid-1', body, headers)

            assert not result.is_error

            topic, _ = server.pubsub_redis.published[0]
            assert topic == 'orders.custom'

        finally:
            _cleanup_env()

    def test_channel_service_overrides_the_topic(self, parties, tmp_path):
        try:
            server, runtime = _make_runtime(tmp_path, parties, service_name='orders.channel-service')

            body, headers, _, _ = _build_wire_message(parties)
            result = runtime.handle('cid-1', body, headers)

            assert not result.is_error

            assert server.pubsub_redis.published == []
            assert len(server.invoked) == 1

            service_name, message = server.invoked[0]
            assert service_name == 'orders.channel-service'
            assert message['edi']['doc_type'] == '850'

        finally:
            _cleanup_env()

    def test_partner_topic_overrides_the_channel(self, parties, tmp_path):
        try:
            server, runtime = _make_runtime(
                tmp_path, parties, service_name='orders.channel-service', partner_topic='orders.partner')

            body, headers, _, _ = _build_wire_message(parties)
            result = runtime.handle('cid-1', body, headers)

            assert not result.is_error

            # The partner's own topic wins over the channel's service.
            assert server.invoked == []

            topic, _ = server.pubsub_redis.published[0]
            assert topic == 'orders.partner'

        finally:
            _cleanup_env()

    def test_partner_service_overrides_everything(self, parties, tmp_path):
        try:
            server, runtime = _make_runtime(
                tmp_path, parties,
                service_name='orders.channel-service',
                partner_service='orders.partner-service', partner_topic='orders.partner',
            )

            body, headers, _, _ = _build_wire_message(parties)
            result = runtime.handle('cid-1', body, headers)

            assert not result.is_error

            assert server.pubsub_redis.published == []

            service_name, _ = server.invoked[0]
            assert service_name == 'orders.partner-service'

        finally:
            _cleanup_env()

    def test_partnership_edits_take_effect_without_a_restart(self, parties, tmp_path):
        try:
            server, runtime = _make_runtime(tmp_path, parties)

            body, headers, _, _ = _build_wire_message(parties)
            result = runtime.handle('cid-1', body, headers)

            assert not result.is_error
            topic, _ = server.pubsub_redis.published[0]
            assert topic == AS2.Default.Inbound_Topic

            # An edit of the Dashboard-managed connection reroutes the very next message.
            server.config_manager.config_store.generic_connection['PartnerCorp AS2'] = {
                'config': _partnership_config(inbound_topic='orders.after-the-edit'),
            }

            body, headers, _, _ = _build_wire_message(parties)
            result = runtime.handle('cid-2', body, headers)

            assert not result.is_error
            topic, _ = server.pubsub_redis.published[1]
            assert topic == 'orders.after-the-edit'

        finally:
            _cleanup_env()

# ################################################################################################################################
# ################################################################################################################################

class TestDuplicates:

    def test_replay_gets_the_stored_mdn_and_is_not_routed_again(self, parties, tmp_path):
        try:
            server, runtime = _make_runtime(tmp_path, parties)

            body, headers, _, _ = _build_wire_message(parties)

            first = runtime.handle('cid-1', body, headers)

            # The replay reuses the same body and headers, Message-ID included.
            second = runtime.handle('cid-2', body, headers)

            assert not first.is_duplicate
            assert second.is_duplicate

            # The stored MDN bytes went out exactly as the first time ..
            assert second.body == first.body
            assert second.status_code == first.status_code

            # .. and the payload was routed only once.
            assert len(server.pubsub_redis.published) == 1

        finally:
            _cleanup_env()

    def test_fresh_message_ids_are_not_duplicates(self, parties, tmp_path):
        try:
            server, runtime = _make_runtime(tmp_path, parties)

            body, headers, _, _ = _build_wire_message(parties)
            first = runtime.handle('cid-1', body, headers)

            body, headers, _, _ = _build_wire_message(parties)
            second = runtime.handle('cid-2', body, headers)

            assert not first.is_duplicate
            assert not second.is_duplicate

            assert len(server.pubsub_redis.published) == 2

        finally:
            _cleanup_env()

# ################################################################################################################################
# ################################################################################################################################

class TestRejections:

    def test_unknown_partner_is_rejected_and_nothing_is_routed(self, parties, tmp_path):
        try:
            server, runtime = _make_runtime(tmp_path, parties, with_partnership=False)

            body, headers, _, _ = _build_wire_message(parties)
            result = runtime.handle('cid-1', body, headers)

            assert result.is_error
            assert result.error_modifier == AS2Error.Unknown_Trading_Relationship

            assert server.invoked == []
            assert server.pubsub_redis.published == []

        finally:
            _cleanup_env()

    def test_rejected_message_is_not_remembered_as_a_duplicate(self, parties, tmp_path):
        try:
            server, runtime = _make_runtime(tmp_path, parties, with_partnership=False)

            body, headers, _, _ = _build_wire_message(parties)

            first = runtime.handle('cid-1', body, headers)
            assert first.is_error

            # The partnership arrives - the same message must now be processable,
            # because a failed delivery never counted as processed.
            config = _partnership_config()
            server.config_manager.config_store.generic_connection['PartnerCorp AS2'] = {'config': config}

            second = runtime.handle('cid-2', body, headers)

            assert not second.is_duplicate
            assert not second.is_error
            assert len(server.pubsub_redis.published) == 1

        finally:
            _cleanup_env()

# ################################################################################################################################
# ################################################################################################################################
