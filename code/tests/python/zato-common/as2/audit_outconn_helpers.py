# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# httpx
import httpx

# Zato
from .audit_helpers import certificate_to_pem, key_to_pem, Receiver_Identifier, Sender_Identifier
from zato.common.as2.inbound import handle
from zato.common.as2.partnership import new_partnership
from zato.common.ext.bunch import Bunch
from zato.server.generic.api.outconn_as2 import _AS2Connection

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    from .conftest import TestParties
    TestParties = TestParties

# ################################################################################################################################
# ################################################################################################################################

class FakeOutconnServer:
    """ Just enough of a server for the outgoing connection - decryption is the identity
    function because the test configuration stores its PEMs in the clear.
    """
    name = 'test-server'

    def decrypt(self, value:'any_') -> 'any_':
        return value

# ################################################################################################################################
# ################################################################################################################################

def connection_config(parties:'TestParties', **overrides:'any_') -> 'any_':
    """ The flat configuration dict of one Dashboard-managed AS2 connection.
    """
    sender_certificate = parties.sender.signing_certificate_chain[0]
    receiver_certificate = parties.receiver.signing_certificate_chain[0]

    sender_key_pem = key_to_pem(parties.sender.signing_key)
    sender_certificate_pem = certificate_to_pem(sender_certificate)
    receiver_certificate_pem = certificate_to_pem(receiver_certificate)

    out = Bunch()

    out['id'] = 1
    out['name'] = 'PartnerCorp AS2'
    out['is_active'] = True
    out['type_'] = 'outconn-as2'
    out['username'] = ''
    out['secret'] = ''
    out['pool_size'] = 1
    out['queue_build_cap'] = 30

    out['as2_from'] = Sender_Identifier
    out['as2_to'] = Receiver_Identifier
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

def new_mock_client(parties:'TestParties') -> 'any_':
    """ Wires the receiving side's real inbound pipeline behind an HTTP mock transport.
    """
    receiver_partnership = new_partnership()
    receiver_partnership.as2_from = Receiver_Identifier
    receiver_partnership.as2_to = Sender_Identifier

    def _handler(request:'httpx.Request') -> 'any_':

        body = request.read()
        headers = dict(request.headers)

        result = handle(body, headers, [receiver_partnership], parties.receiver)

        response = httpx.Response(result.status_code, content=result.body, headers=result.headers)
        return response

    transport = httpx.MockTransport(_handler)

    out = httpx.Client(transport=transport)
    return out

# ################################################################################################################################

def make_connection(parties:'TestParties', **overrides:'any_') -> 'any_':
    """ Builds one AS2 connection over a mock wire.
    """
    server = FakeOutconnServer()
    config = connection_config(parties, **overrides)

    out = _AS2Connection(config, server)

    # The mock wire replaces the connection's own HTTP client.
    out.http_client.close()
    out.http_client = new_mock_client(parties)

    return out

# ################################################################################################################################
# ################################################################################################################################
