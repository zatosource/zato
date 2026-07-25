# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from .audit_helpers import certificate_to_pem, key_to_pem, Payload, Receiver_Identifier, Sender_Identifier
from zato.common.as2.outbound import build_message
from zato.common.as2.partnership import new_partnership
from zato.common.typing_ import cast_
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

class FakeConfigManager:
    """ Just enough of the server's configuration manager for the channel runtime.
    """

    def __init__(self) -> 'None':

        # The live per-type dict of AS2 outgoing connection configs, keyed by name
        self.outconn_as2 = {}

        # How many times those configs changed - the real one bumps this from the create,
        # edit and delete events, and a channel rebuilds its partnerships when it moves.
        self.as2_config_generation = 0

# ################################################################################################################################
# ################################################################################################################################

class FakePubSub:
    """ Records everything a channel would have published instead of publishing it.
    """

    def __init__(self) -> 'None':
        self.published = []

# ################################################################################################################################

    def publish(self, topic:'any_', message:'any_', cid:'any_' = '', correl_id:'any_' = '') -> 'None':
        self.published.append((topic, message))

# ################################################################################################################################
# ################################################################################################################################

class FakeChannelServer:
    """ Just enough of a server for the channel runtime.
    """
    name = 'test-server'

    def __init__(self) -> 'None':
        self.invoked = []
        self.config_manager = FakeConfigManager()
        self.pubsub_backend = FakePubSub()

# ################################################################################################################################

    def decrypt(self, value:'any_') -> 'any_':
        return value

# ################################################################################################################################

    def invoke(self, service_name:'any_', message:'any_') -> 'None':
        self.invoked.append((service_name, message))

# ################################################################################################################################
# ################################################################################################################################

def partnership_config() -> 'any_':
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

def channel_config(parties:'TestParties') -> 'any_':
    """ The channel item of one AS2 channel, with the receiver's keys pasted in as PEMs.
    """
    receiver_certificate = parties.receiver.signing_certificate_chain[0]
    sender_certificate = parties.sender.signing_certificate_chain[0]

    receiver_key_pem = key_to_pem(parties.receiver.signing_key)
    receiver_certificate_pem = certificate_to_pem(receiver_certificate)
    sender_certificate_pem = certificate_to_pem(sender_certificate)

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
        'as2_peer_signing_cert': sender_certificate_pem,
        'as2_peer_encryption_cert': sender_certificate_pem,
        'as2_trust_anchors': '',
    }

    return out

# ################################################################################################################################

def make_runtime(parties:'TestParties', with_partnership:'any_' = True) -> 'any_':
    """ Builds a channel runtime on a fake server.
    """
    fake_server = FakeChannelServer()
    server = cast_('ParallelServer', fake_server)

    if with_partnership:
        server.config_manager.outconn_as2['PartnerCorp AS2'] = partnership_config()

    config = channel_config(parties)

    out = AS2ChannelRuntime(server, config)
    return out

# ################################################################################################################################

def build_wire_message(parties:'TestParties') -> 'any_':
    """ Builds one real AS2 message the way the sending side would.
    """
    partnership = new_partnership()
    partnership.as2_from = Sender_Identifier
    partnership.as2_to = Receiver_Identifier

    body, headers, message_id, mic = build_message(partnership, parties.sender, Payload)

    out = body, headers, message_id, mic
    return out

# ################################################################################################################################
# ################################################################################################################################
