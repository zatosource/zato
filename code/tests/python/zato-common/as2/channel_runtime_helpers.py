# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# cryptography
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat

# Zato
from zato.common.as2.common import MDNMode
from zato.common.as2.outbound import build_message
from zato.common.as2.partnership import new_partnership
from zato.common.audit_log.api import ModuleCtx as AuditLogCtx
from zato.common.typing_ import cast_
from zato.common.util.xml_.keystore import new_keystore
from zato.server.connection.as2 import AS2ChannelRuntime

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

Sender_Identifier   = 'ZatoRetail'
Receiver_Identifier = 'PartnerCorp'

# The name the Dashboard-managed outgoing connection is keyed under on the receiving side.
Connection_Name = 'PartnerCorp AS2'

# Where the sending side asks its receipts to be delivered - the same host the partnership
# already names, which is what the inbound pipeline checks the destination against.
Async_MDN_URL = 'https://zatoretail.example.com/zato/as2/mdn'

Payload = (
    b'ISA*00*          *00*          *ZZ*ZATORETAIL     *ZZ*PARTNERCORP    '
    + b'*260709*1200*U*00401*000000001*0*P*>~GS*PO*ZATORETAIL*PARTNERCORP*20260709*1200*1*X*004010~'
    + b'ST*850*0001~BEG*00*NE*4523891**20260709~SE*3*0001~GE*1*1~IEA*1*000000001~'
)

# ################################################################################################################################
# ################################################################################################################################

def key_to_pem(key:'any_') -> 'any_':
    encryption = NoEncryption()

    out = key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, encryption).decode('ascii')
    return out

# ################################################################################################################################

def certificate_to_pem(certificate:'any_') -> 'any_':
    out = certificate.public_bytes(Encoding.PEM).decode('ascii')
    return out

# ################################################################################################################################

def sender_certificate_to_pem(parties:'TestParties') -> 'any_':
    """ The PEM of the certificate the sending side currently signs with.
    """
    certificate = parties.sender.signing_certificate_chain[0]

    out = certificate_to_pem(certificate)
    return out

# ################################################################################################################################
# ################################################################################################################################

class _FakeConfigManager:
    def __init__(self) -> 'None':

        # The live per-type dict of AS2 outgoing connection configs, keyed by name
        self.outconn_as2 = {}

        # How many times those configs changed - the real one bumps this from the create,
        # edit and delete events, and a channel rebuilds its partnerships when it moves.
        self.as2_config_generation = 0

# ################################################################################################################################

class _FakePubSub:
    def __init__(self) -> 'None':
        self.published = []

# ################################################################################################################################

    def publish(self, topic:'any_', message:'any_', cid:'any_' = '', correl_id:'any_' = '') -> 'None':
        self.published.append((topic, message))

# ################################################################################################################################

class _FakeServer:
    """ Just enough of a server for the channel runtime - decryption is the identity function
    because the test configuration stores its PEMs in the clear.
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
# ################################################################################################################################

def make_partnership_config(
    inbound_topic:'any_' = '',
    inbound_service:'any_' = '',
    partner_certificate:'any_' = '',
    next_certificate:'any_' = '',
    next_certificate_from:'any_' = '',
) -> 'any_':
    """ The flat configuration dict of one Dashboard-managed AS2 connection,
    as the receiving side sees the relationship.
    """
    out = {
        'type_': 'outconn-as2',

        # The identities compare crosswise on inbound - as2_from is our own identifier.
        'as2_from': Receiver_Identifier,
        'as2_to': Sender_Identifier,

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
        'is_audit_log_active': True,

        'http_timeout_seconds': 0,
        'chunked_threshold_bytes': 0,
        'ack_overdue_after': 0,
        'resend_max_retries': 0,

        'as2_partner_cert': partner_certificate,
        'as2_partner_next_cert': next_certificate,
        'as2_partner_next_cert_from': next_certificate_from,
    }

    return out

# ################################################################################################################################

def make_channel_config(parties:'TestParties', service_name:'any_' = None, inbound_topic:'any_' = None) -> 'any_':
    """ The channel item of one AS2 channel, with the receiver's keys pasted in as PEMs.
    """
    receiver_key_pem = key_to_pem(parties.receiver.signing_key)
    receiver_certificate = parties.receiver.signing_certificate_chain[0]
    receiver_certificate_pem = certificate_to_pem(receiver_certificate)
    sender_certificate_pem = sender_certificate_to_pem(parties)

    out = {
        'name': 'zato.channel.as2',
        'service_name': service_name,
        'as2_inbound_topic': inbound_topic,
        'as2_duplicate_window_days': None,

        'as2_signing_key': receiver_key_pem,
        'as2_signing_cert_chain': receiver_certificate_pem,
        'as2_decryption_key': receiver_key_pem,
        'as2_next_decryption_key': '',
        'as2_next_decryption_cert': '',
        'as2_peer_signing_cert': sender_certificate_pem,
        'as2_peer_encryption_cert': sender_certificate_pem,
        'as2_trust_anchors': '',
    }

    return out

# ################################################################################################################################

def make_runtime(
    tmp_path:'os.PathLike',
    parties:'TestParties',
    service_name:'any_' = None,
    channel_topic:'any_' = None,
    with_partnership:'any_' = True,
    partner_topic:'any_' = '',
    partner_service:'any_' = '',
    partner_certificate:'any_' = '',
    next_certificate:'any_' = '',
    next_certificate_from:'any_' = '',
    ) -> 'any_':
    """ Builds a channel runtime on a fake server with a per-test SQLite audit database.
    """
    directory = str(tmp_path)
    database_path = os.path.join(directory, 'audit.db')

    os.environ[AuditLogCtx.Env_Type] = AuditLogCtx.Type_SQLite
    os.environ[AuditLogCtx.Env_Name] = database_path

    server = _FakeServer()

    if with_partnership:
        options = {
            'inbound_topic': partner_topic,
            'inbound_service': partner_service,
            'partner_certificate': partner_certificate,
            'next_certificate': next_certificate,
            'next_certificate_from': next_certificate_from,
            }
        config = make_partnership_config(**options)
        server.config_manager.outconn_as2[Connection_Name] = config

    channel_config = make_channel_config(parties, service_name, channel_topic)
    parallel_server = cast_('ParallelServer', server)
    runtime = AS2ChannelRuntime(parallel_server, channel_config)

    out = server, runtime
    return out

# ################################################################################################################################

def cleanup_env() -> 'None':
    del os.environ[AuditLogCtx.Env_Type]
    del os.environ[AuditLogCtx.Env_Name]

# ################################################################################################################################

def build_wire_message(parties:'TestParties', message_id:'any_' = None, sender_keystore:'any_' = None) -> 'any_':
    """ Builds one real AS2 message the way the sending side would.
    """
    partnership = new_partnership()
    partnership.as2_from = Sender_Identifier
    partnership.as2_to = Receiver_Identifier

    if sender_keystore is None:
        sender_keystore = parties.sender

    body, headers, message_id, mic = build_message(partnership, sender_keystore, Payload, message_id=message_id)

    out = body, headers, message_id, mic
    return out

# ################################################################################################################################

def build_async_wire_message(parties:'TestParties') -> 'any_':
    """ Builds one real AS2 message asking for its receipt to be delivered asynchronously,
    to a URL on the same host the partnership already names.
    """
    partnership = new_partnership()
    partnership.as2_from = Sender_Identifier
    partnership.as2_to = Receiver_Identifier
    partnership.mdn_mode = MDNMode.Async
    partnership.async_mdn_url = Async_MDN_URL

    body, headers, message_id, mic = build_message(partnership, parties.sender, Payload)

    out = body, headers, message_id, mic
    return out

# ################################################################################################################################

def rotated_sender_keystore(parties:'TestParties', rotated:'any_') -> 'any_':
    """ The sending side's keystore after it rotated its signing pair -
    encryption still targets the receiver's current certificate.
    """
    out = new_keystore()

    out.signing_key = rotated.key
    out.signing_certificate_chain = [rotated.certificate]
    out.peer_encryption_certificate = parties.receiver.signing_certificate_chain[0]

    return out

# ################################################################################################################################
# ################################################################################################################################
