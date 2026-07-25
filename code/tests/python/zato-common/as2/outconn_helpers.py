# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# cryptography
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat

# httpx
import httpx

# Zato
from zato.common.as2.inbound import handle
from zato.common.as2.partnership import new_partnership
from zato.common.ext.bunch import Bunch
from zato.common.typing_ import cast_
from zato.server.connection.facade import AS2Facade
from zato.server.generic.api.outconn_as2 import _AS2Connection, OutconnAS2Wrapper

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, stranydict
    from zato.server.base.config_manager import ConfigManager
    ConfigManager = ConfigManager

    from .conftest import TestParties
    TestParties = TestParties

# ################################################################################################################################
# ################################################################################################################################

Sender_Identifier   = 'ZatoRetail'
Receiver_Identifier = 'PartnerCorp'

# The name the Dashboard-managed connection is configured under.
Connection_Name = 'PartnerCorp AS2'

Payload = (
    b'ISA*00*          *00*          *ZZ*ZATORETAIL     *ZZ*PARTNERCORP    '
    + b'*260709*1200*U*00401*000000001*0*P*>~GS*PO*ZATORETAIL*PARTNERCORP*20260709*1200*1*X*004010~'
    + b'ST*850*0001~BEG*00*NE*4523891**20260709~SE*3*0001~GE*1*1~IEA*1*000000001~'
)

# ################################################################################################################################
# ################################################################################################################################

def key_to_pem(key:'any_') -> 'any_':
    """ One private key in the PEM form the connection form stores it in.
    """
    no_encryption = NoEncryption()
    key_bytes = key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, no_encryption)

    out = key_bytes.decode('ascii')
    return out

# ################################################################################################################################

def certificate_to_pem(certificate:'any_') -> 'any_':
    """ One certificate in the PEM form the connection form stores it in.
    """
    certificate_bytes = certificate.public_bytes(Encoding.PEM)

    out = certificate_bytes.decode('ascii')
    return out

# ################################################################################################################################
# ################################################################################################################################

class FakeServer:
    """ Just enough of a server for the connection wrapper - decryption is the identity function
    because the test configuration stores its PEMs in the clear, and each decrypted value
    is recorded so the tests can see that private keys did go through it.
    """
    name = 'test-server'

    def __init__(self) -> 'None':
        self.decrypted = []

# ################################################################################################################################

    def decrypt(self, value:'any_') -> 'any_':
        self.decrypted.append(value)

        return value

# ################################################################################################################################
# ################################################################################################################################

class FakeConfigManager:
    """ Just enough of a config manager for the facade - the per-type dict
    of AS2 outgoing connections is all it reads.
    """

    def __init__(self, outconn_as2:'stranydict') -> 'None':
        self.outconn_as2 = outconn_as2

# ################################################################################################################################
# ################################################################################################################################

def connection_config(parties:'TestParties', **overrides:'any_') -> 'any_':
    """ The flat configuration dict of one Dashboard-managed AS2 connection,
    with our own keys pasted in as PEMs and the partner's certificate on the rotation list.
    """
    sender_certificate = parties.sender.signing_certificate_chain[0]
    receiver_certificate = parties.receiver.signing_certificate_chain[0]

    sender_key_pem = key_to_pem(parties.sender.signing_key)
    sender_certificate_pem = certificate_to_pem(sender_certificate)
    receiver_certificate_pem = certificate_to_pem(receiver_certificate)

    out = Bunch()

    # The connection queue fields.
    out['id'] = 1
    out['name'] = Connection_Name
    out['is_active'] = True
    out['type_'] = 'outconn-as2'
    out['username'] = ''
    out['secret'] = ''
    out['pool_size'] = 1
    out['queue_build_cap'] = 30

    # The AS2 identities and the endpoint.
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

    # The partner's certificate serves both encryption and MDN verification.
    out['as2_partner_cert'] = receiver_certificate_pem
    out['as2_partner_next_cert'] = ''
    out['as2_partner_next_cert_from'] = ''

    # Our own keystore material - no explicit peer certificates,
    # so the rotation list is what outgoing encryption uses.
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

def new_mock_client(parties:'TestParties', requests:'anylist', results:'anylist') -> 'any_':
    """ Wires the receiving side's real inbound pipeline behind an HTTP mock transport.
    """
    receiver_partnership = new_partnership()
    receiver_partnership.as2_from = Receiver_Identifier
    receiver_partnership.as2_to = Sender_Identifier

    def _handler(request:'httpx.Request') -> 'any_':

        body = request.read()
        requests.append(request)

        headers = dict(request.headers)
        result = handle(body, headers, [receiver_partnership], parties.receiver)
        results.append(result)

        response = httpx.Response(result.status_code, content=result.body, headers=result.headers)
        return response

    transport = httpx.MockTransport(_handler)

    out = httpx.Client(transport=transport)
    return out

# ################################################################################################################################

def make_connection(parties:'TestParties', **overrides:'any_') -> 'any_':
    """ Builds one AS2 connection over a mock wire, returning it together
    with the receiving side's captures.
    """
    server = FakeServer()
    config = connection_config(parties, **overrides)

    connection = _AS2Connection(config, server)

    requests = []
    results = []

    # The mock wire replaces the connection's own HTTP client.
    connection.http_client.close()
    connection.http_client = new_mock_client(parties, requests, results)

    out = connection, server, requests, results
    return out

# ################################################################################################################################

def make_facade(parties:'any_', requests:'anylist', results:'anylist') -> 'AS2Facade':
    """ Builds the facade over one pooled connection wired to the mock wire,
    the way a service sees it after Service._init ran.
    """
    server = FakeServer()
    config = connection_config(parties)

    wrapper = OutconnAS2Wrapper(config, server)
    wrapper.add_client()

    # The pooled connection talks to the mock wire.
    queue = cast_('any_', wrapper.client.queue)
    connection = queue.queue[0]
    connection.http_client = new_mock_client(parties, requests, results)

    # The config manager holds the per-type dict the way the server builds it -
    # one item per connection, with the wrapper under the item's conn key.
    item = Bunch()
    item['conn'] = wrapper

    config_manager = FakeConfigManager({config['name']: item})
    manager = cast_('ConfigManager', config_manager)

    out = AS2Facade()
    out.init('cid-1', manager)

    return out

# ################################################################################################################################
# ################################################################################################################################
