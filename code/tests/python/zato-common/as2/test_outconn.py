# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import socket
import ssl
import threading
from base64 import b64encode
from datetime import datetime, timedelta, timezone

# cryptography
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat

# httpx
import httpx

# pytest
import pytest

# Zato
from zato.common.as2.common import AS2Error, AS2Exception
from zato.common.as2.inbound import handle
from zato.common.as2.mdn import normalize_message_id
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

class _FakeServer:
    """ Just enough of a server for the connection wrapper - decryption is the identity function
    because the test configuration stores its PEMs in the clear, and each decrypted value
    is recorded so the tests can see that private keys did go through it.
    """
    name = 'test-server'

    def __init__(self):
        self.decrypted = []

    def decrypt(self, value):
        self.decrypted.append(value)
        return value

# ################################################################################################################################
# ################################################################################################################################

def _connection_config(parties, **overrides):
    """ The flat configuration dict of one Dashboard-managed AS2 connection,
    with our own keys pasted in as PEMs and the partner's certificate on the rotation list.
    """
    sender_key_pem = _key_to_pem(parties.sender.signing_key)
    sender_certificate_pem = _certificate_to_pem(parties.sender.signing_certificate_chain[0])
    receiver_certificate_pem = _certificate_to_pem(parties.receiver.signing_certificate_chain[0])

    out = Bunch()

    # The connection queue fields.
    out['id'] = 1
    out['name'] = 'PartnerCorp AS2'
    out['is_active'] = True
    out['type_'] = 'outconn-as2'
    out['username'] = ''
    out['secret'] = ''
    out['pool_size'] = 1
    out['queue_build_cap'] = 30

    # The AS2 identities and the endpoint.
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

def _new_mock_client(parties, requests, results):
    """ Wires the receiving side's real inbound pipeline behind an HTTP mock transport.
    """
    receiver_partnership = new_partnership()
    receiver_partnership.as2_from = _receiver_identifier
    receiver_partnership.as2_to = _sender_identifier

    def _handler(request):

        body = request.read()
        requests.append(request)

        result = handle(body, dict(request.headers), [receiver_partnership], parties.receiver)
        results.append(result)

        response = httpx.Response(result.status_code, content=result.body, headers=result.headers)
        return response

    transport = httpx.MockTransport(_handler)

    out = httpx.Client(transport=transport)
    return out

# ################################################################################################################################

def _make_connection(parties, **overrides):
    """ Builds one AS2 connection over a mock wire, returning it together
    with the receiving side's captures.
    """
    server = _FakeServer()
    config = _connection_config(parties, **overrides)

    connection = _AS2Connection(config, server)

    requests = []
    results = []

    # The mock wire replaces the connection's own HTTP client.
    connection.http_client.close()
    connection.http_client = _new_mock_client(parties, requests, results)

    out = connection, server, requests, results
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestConnection:

    def test_send_reconciles_the_sync_mdn(self, parties):

        connection, _, requests, results = _make_connection(parties)

        result = connection.send('cid-1', _payload)

        # The delivery went out signed and encrypted and came back confirmed ..
        assert result.is_ok
        assert result.message_id
        assert result.mic

        # .. the MDN answers the message that was sent ..
        assert result.mdn
        assert normalize_message_id(result.mdn.original_message_id) == normalize_message_id(result.message_id)

        # .. and the receiver's real pipeline accepted the payload.
        assert len(requests) == 1
        assert not results[0].is_error
        assert results[0].payloads[0].data == _payload

    def test_send_accepts_a_string_payload(self, parties):

        connection, _, _, results = _make_connection(parties)

        result = connection.send('cid-1', _payload.decode('ascii'))

        assert result.is_ok
        assert results[0].payloads[0].data == _payload

    def test_send_reports_an_unconfirmed_delivery(self, parties):

        # The receiver does not know this sender, so its MDN reports an error disposition.
        connection, _, _, results = _make_connection(parties, as2_from='UnknownSender')

        result = connection.send('cid-1', _payload)

        assert not result.is_ok
        assert results[0].is_error

# ################################################################################################################################
# ################################################################################################################################

class TestConfigBridging:

    def test_partnership_and_keystore_come_from_the_config(self, parties):

        connection, server, _, _ = _make_connection(parties)

        # The partnership carries the configured identities and endpoint ..
        assert connection.partnership.as2_from == _sender_identifier
        assert connection.partnership.as2_to == _receiver_identifier
        assert connection.partnership.endpoint_url == 'https://partnercorp.example.com/as2'

        # .. the keystore holds our own material ..
        assert connection.keystore.signing_key
        assert connection.keystore.decryption_key

        # .. and both private keys went through the server's decryption.
        sender_key_pem = _key_to_pem(parties.sender.signing_key)
        assert server.decrypted == [sender_key_pem, sender_key_pem]

    def test_rotation_list_supplies_the_peer_certificates(self, parties):

        connection, _, _, results = _make_connection(parties)

        # No peer certificates are pinned in the keystore ..
        assert connection.keystore.peer_encryption_certificate is None
        assert connection.keystore.peer_signing_certificate is None

        # .. yet the send encrypts to the partner and the returned MDN verifies,
        # because the rotation list supplies both certificates at send time.
        result = connection.send('cid-1', _payload)

        assert result.is_ok
        assert not results[0].is_error

    def test_an_activated_next_certificate_supersedes_the_current_one(self, parties, make_rotated_pair):

        # A fresh partner certificate whose activation date has already passed.
        rotated = make_rotated_pair('as2-receiver-next')
        activated = datetime.now(timezone.utc) - timedelta(days=1)

        connection, _, _, results = _make_connection(
            parties,
            as2_partner_next_cert=_certificate_to_pem(rotated.certificate),
            as2_partner_next_cert_from=activated.isoformat(),
        )

        result = connection.send('cid-1', _payload)

        # The receiver only holds the key of the current certificate, so a message
        # encrypted to the activated next certificate does not decrypt there -
        # the proof that outgoing encryption switched over.
        assert not result.is_ok
        assert results[0].is_error
        assert results[0].error_modifier == AS2Error.Decryption_Failed

    def test_a_future_next_certificate_leaves_the_current_one_in_place(self, parties, make_rotated_pair):

        # A fresh partner certificate that only activates a month from now.
        rotated = make_rotated_pair('as2-receiver-next')
        activation = datetime.now(timezone.utc) + timedelta(days=30)

        connection, _, _, results = _make_connection(
            parties,
            as2_partner_next_cert=_certificate_to_pem(rotated.certificate),
            as2_partner_next_cert_from=activation.isoformat(),
        )

        result = connection.send('cid-1', _payload)

        # Encryption stayed with the current certificate, so the receiver decrypts fine.
        assert result.is_ok
        assert not results[0].is_error

    def test_username_turns_on_basic_authentication(self, parties:'any_') -> 'None':

        connection, server, requests, _ = _make_connection(
            parties,
            username='as2-basic-user',
            secret='as2-basic-password',
        )

        # The partnership carries the credentials ..
        assert connection.partnership.http_auth
        assert connection.partnership.http_auth.username == 'as2-basic-user'
        assert connection.partnership.http_auth.password == 'as2-basic-password'

        # .. the password went through the server's decryption like every secret ..
        assert 'as2-basic-password' in server.decrypted

        # .. and the delivery itself carries the matching Authorization header.
        result = connection.send('cid-1', _payload)
        assert result.is_ok

        credentials = b64encode(b'as2-basic-user:as2-basic-password').decode('ascii')
        assert requests[0].headers['authorization'] == f'Basic {credentials}'

    def test_no_username_means_no_basic_authentication(self, parties:'any_') -> 'None':

        connection, _, requests, _ = _make_connection(parties)

        # No credentials are configured ..
        assert connection.partnership.http_auth is None

        # .. and the delivery carries no Authorization header.
        result = connection.send('cid-1', _payload)
        assert result.is_ok
        assert 'authorization' not in requests[0].headers

    def test_next_decryption_pair_joins_the_rotation_entries(self, parties, make_rotated_pair):

        # Our own next key with its certificate, configured ahead of the rotation.
        rotated = make_rotated_pair('as2-sender-next')

        connection, server, _, _ = _make_connection(
            parties,
            as2_next_decryption_key=_key_to_pem(rotated.key),
            as2_next_decryption_cert=_certificate_to_pem(rotated.certificate),
        )

        # The pair joined the keystore's rotation entries ..
        entry = connection.keystore.decryption_entries[0]
        assert entry.certificate.serial_number == rotated.certificate.serial_number

        # .. and the next key went through the server's decryption like every private key.
        assert _key_to_pem(rotated.key) in server.decrypted

# ################################################################################################################################
# ################################################################################################################################

class TestPing:

    def test_ping_connects_over_plain_http(self, parties):

        # A listening socket is all a plain HTTP ping needs.
        listener = socket.socket()
        listener.bind(('127.0.0.1', 0))
        listener.listen(1)
        port = listener.getsockname()[1]

        try:
            connection, _, _, _ = _make_connection(parties, endpoint_url=f'http://127.0.0.1:{port}/as2')
            connection.ping()
        finally:
            listener.close()

    def test_ping_runs_the_tls_handshake(self, parties, tmp_path):

        # The endpoint presents the receiver's certificate over TLS.
        certificate_path = tmp_path / 'endpoint-cert.pem'
        key_path = tmp_path / 'endpoint-key.pem'

        _ = certificate_path.write_text(_certificate_to_pem(parties.receiver.signing_certificate_chain[0]))
        _ = key_path.write_text(_key_to_pem(parties.receiver.signing_key))

        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(str(certificate_path), str(key_path))

        listener = socket.socket()
        listener.bind(('127.0.0.1', 0))
        listener.listen(1)
        port = listener.getsockname()[1]

        def _serve_one_handshake():
            try:
                client_socket, _ignored = listener.accept()
                tls_socket = context.wrap_socket(client_socket, server_side=True)
                tls_socket.close()
            except OSError:
                pass

        server_thread = threading.Thread(target=_serve_one_handshake)
        server_thread.start()

        try:
            # The endpoint's certificate is self-issued for the test,
            # which is exactly what the verification toggle is for.
            connection, _, _, _ = _make_connection(
                parties,
                endpoint_url=f'https://127.0.0.1:{port}/as2',
                verify_tls=False,
            )
            connection.ping()
        finally:
            server_thread.join()
            listener.close()

    def test_ping_fails_when_nothing_listens(self, parties):

        # Bind a port and close it right away so nothing listens on it.
        listener = socket.socket()
        listener.bind(('127.0.0.1', 0))
        port = listener.getsockname()[1]
        listener.close()

        connection, _, _, _ = _make_connection(parties, endpoint_url=f'http://127.0.0.1:{port}/as2')

        with pytest.raises(OSError):
            connection.ping()

    def test_ping_fails_without_an_endpoint(self, parties):

        connection, _, _, _ = _make_connection(parties, endpoint_url='')

        with pytest.raises(AS2Exception):
            connection.ping()

# ################################################################################################################################
# ################################################################################################################################

class TestWrapper:

    def test_send_goes_through_a_pooled_connection(self, parties):

        server = _FakeServer()
        config = _connection_config(parties)

        wrapper = OutconnAS2Wrapper(config, server)
        wrapper.add_client()

        # The pooled connection talks to the mock wire.
        requests = []
        results = []

        connection = wrapper.client.queue.queue[0]
        connection.http_client = _new_mock_client(parties, requests, results)

        result = wrapper.send('cid-1', _payload)

        assert result.is_ok
        assert len(requests) == 1
        assert not results[0].is_error

        # The connection went back to the pool after the send.
        assert wrapper.client.queue.qsize() == 1

    def test_add_client_without_a_signing_key_adds_nothing(self, parties):

        server = _FakeServer()
        config = _connection_config(parties, as2_signing_key='')

        wrapper = OutconnAS2Wrapper(config, server)
        wrapper.add_client()

        assert wrapper.client.queue.qsize() == 0

# ################################################################################################################################
# ################################################################################################################################

class _FakeConfigManager:
    """ Just enough of a config manager for the facade - the per-type dict
    of AS2 outgoing connections is all it reads.
    """

    def __init__(self, outconn_as2:'stranydict') -> 'None':
        self.outconn_as2 = outconn_as2

# ################################################################################################################################
# ################################################################################################################################

def _make_facade(parties:'any_', requests:'anylist', results:'anylist') -> 'AS2Facade':
    """ Builds the facade over one pooled connection wired to the mock wire,
    the way a service sees it after Service._init ran.
    """
    server = _FakeServer()
    config = _connection_config(parties)

    wrapper = OutconnAS2Wrapper(config, server)
    wrapper.add_client()

    # The pooled connection talks to the mock wire.
    queue = cast_('any_', wrapper.client.queue)
    connection = queue.queue[0]
    connection.http_client = _new_mock_client(parties, requests, results)

    # The config manager holds the per-type dict the way the server builds it -
    # one item per connection, with the wrapper under the item's conn key.
    item = Bunch()
    item['conn'] = wrapper

    config_manager = _FakeConfigManager({config['name']: item})

    out = AS2Facade()
    out.init('cid-1', cast_('ConfigManager', config_manager))

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestFacade:

    def test_send_carries_the_cid_for_the_user(self, parties:'any_') -> 'None':

        requests = []
        results = []

        facade = _make_facade(parties, requests, results)

        # The one-liner a service runs - no cid anywhere in user code.
        connection = facade['PartnerCorp AS2']
        result = connection.send(_payload)

        assert result.is_ok
        assert len(requests) == 1
        assert not results[0].is_error
        assert results[0].payloads[0].data == _payload

    def test_an_unknown_name_raises_a_key_error(self, parties:'any_') -> 'None':

        facade = _make_facade(parties, [], [])

        with pytest.raises(KeyError):
            _ = facade['No Such Partner']

# ################################################################################################################################
# ################################################################################################################################
