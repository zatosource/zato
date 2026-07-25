# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from base64 import b64encode
from datetime import datetime, timedelta, timezone

# Zato
from zato.common.as2.common import AS2Error

# Zato
from .outconn_helpers import certificate_to_pem, key_to_pem, make_connection, Payload, Receiver_Identifier, \
    Sender_Identifier

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    from .conftest import TestParties
    TestParties = TestParties

# ################################################################################################################################
# ################################################################################################################################

# The credentials the basic authentication tests configure the connection with.
_basic_username = 'as2-basic-user'
_basic_password = 'as2-basic-password'

# ################################################################################################################################
# ################################################################################################################################

class TestConfigBridging:

    def test_partnership_and_keystore_come_from_the_config(self, parties:'TestParties') -> 'None':

        connection, server, _, _ = make_connection(parties)

        # The partnership carries the configured identities and endpoint ..
        assert connection.partnership.as2_from == Sender_Identifier
        assert connection.partnership.as2_to == Receiver_Identifier
        assert connection.partnership.endpoint_url == 'https://partnercorp.example.com/as2'

        # .. the keystore holds our own material ..
        assert connection.keystore.signing_key
        assert connection.keystore.decryption_key

        # .. and both private keys went through the server's decryption.
        sender_key_pem = key_to_pem(parties.sender.signing_key)
        assert server.decrypted == [sender_key_pem, sender_key_pem]

# ################################################################################################################################

    def test_rotation_list_supplies_the_peer_certificates(self, parties:'TestParties') -> 'None':

        connection, _, _, results = make_connection(parties)

        # No peer certificates are pinned in the keystore ..
        assert connection.keystore.peer_encryption_certificate is None
        assert connection.keystore.peer_signing_certificate is None

        # .. yet the send encrypts to the partner and the returned MDN verifies,
        # because the rotation list supplies both certificates at send time.
        result = connection.send('cid-1', Payload)

        assert result.is_ok

        first_result = results[0]
        assert not first_result.is_error

# ################################################################################################################################

    def test_an_activated_next_certificate_supersedes_the_current_one(
        self,
        parties:'TestParties',
        make_rotated_pair:'any_',
        ) -> 'None':

        # A fresh partner certificate whose activation date has already passed.
        rotated = make_rotated_pair('as2-receiver-next')

        now = datetime.now(timezone.utc)
        activated = now - timedelta(days=1)

        options = {
            'as2_partner_next_cert': certificate_to_pem(rotated.certificate),
            'as2_partner_next_cert_from': activated.isoformat(),
        }

        connection, _, _, results = make_connection(parties, **options)

        result = connection.send('cid-1', Payload)

        # The receiver only holds the key of the current certificate, so a message
        # encrypted to the activated next certificate does not decrypt there -
        # the proof that outgoing encryption switched over.
        assert not result.is_ok

        first_result = results[0]

        assert first_result.is_error
        assert first_result.error_modifier == AS2Error.Decryption_Failed

# ################################################################################################################################

    def test_a_future_next_certificate_leaves_the_current_one_in_place(
        self,
        parties:'TestParties',
        make_rotated_pair:'any_',
        ) -> 'None':

        # A fresh partner certificate that only activates a month from now.
        rotated = make_rotated_pair('as2-receiver-next')

        now = datetime.now(timezone.utc)
        activation = now + timedelta(days=30)

        options = {
            'as2_partner_next_cert': certificate_to_pem(rotated.certificate),
            'as2_partner_next_cert_from': activation.isoformat(),
        }

        connection, _, _, results = make_connection(parties, **options)

        result = connection.send('cid-1', Payload)

        # Encryption stayed with the current certificate, so the receiver decrypts fine.
        assert result.is_ok

        first_result = results[0]
        assert not first_result.is_error

# ################################################################################################################################

    def test_username_turns_on_basic_authentication(self, parties:'any_') -> 'None':

        options = {
            'username': _basic_username,
            'secret': _basic_password,
        }

        connection, server, requests, _ = make_connection(parties, **options)

        # The partnership carries the credentials ..
        assert connection.partnership.http_auth
        assert connection.partnership.http_auth.username == _basic_username
        assert connection.partnership.http_auth.password == _basic_password

        # .. the password went through the server's decryption like every secret ..
        assert _basic_password in server.decrypted

        # .. and the delivery itself carries the matching Authorization header.
        result = connection.send('cid-1', Payload)
        assert result.is_ok

        credentials_text = f'{_basic_username}:{_basic_password}'
        credentials_bytes = credentials_text.encode('ascii')
        credentials_base64 = b64encode(credentials_bytes)
        credentials = credentials_base64.decode('ascii')

        first_request = requests[0]
        assert first_request.headers['authorization'] == f'Basic {credentials}'

# ################################################################################################################################

    def test_no_username_means_no_basic_authentication(self, parties:'any_') -> 'None':

        connection, _, requests, _ = make_connection(parties)

        # No credentials are configured ..
        assert connection.partnership.http_auth is None

        # .. and the delivery carries no Authorization header.
        result = connection.send('cid-1', Payload)
        assert result.is_ok

        first_request = requests[0]
        assert 'authorization' not in first_request.headers

# ################################################################################################################################

    def test_next_decryption_pair_joins_the_rotation_entries(
        self,
        parties:'TestParties',
        make_rotated_pair:'any_',
        ) -> 'None':

        # Our own next key with its certificate, configured ahead of the rotation.
        rotated = make_rotated_pair('as2-sender-next')
        rotated_key_pem = key_to_pem(rotated.key)

        options = {
            'as2_next_decryption_key': rotated_key_pem,
            'as2_next_decryption_cert': certificate_to_pem(rotated.certificate),
        }

        connection, server, _, _ = make_connection(parties, **options)

        # The pair joined the keystore's rotation entries ..
        entry = connection.keystore.decryption_entries[0]
        assert entry.certificate.serial_number == rotated.certificate.serial_number

        # .. and the next key went through the server's decryption like every private key.
        assert rotated_key_pem in server.decrypted

# ################################################################################################################################
# ################################################################################################################################
