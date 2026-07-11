# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The formal-document conformance suite. Every expected value below is typed out
# literally from the governing documents - the AS2 header grammar and disposition
# strings of RFC 4130 sections 6 and 7, the disposition report layout of RFC 8098,
# the micalg names of RFC 5751 and the CMS object identifiers of RFC 5652 - never
# imported from the code under test. Every cryptographic value is recomputed
# independently: the MIC with hashlib over a literally typed entity, SignedData
# after an independent DER parse, EnvelopedData with cryptography primitives only,
# and the openssl CLI stands in as the third-party oracle in both directions.

# stdlib
from base64 import b64decode, b64encode
from hashlib import sha256
from pathlib import Path
from subprocess import run as subprocess_run

# asn1crypto
from asn1crypto.cms import ContentInfo
from asn1crypto.core import Integer, OctetString, Sequence

# cryptography
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
from cryptography.hazmat.primitives.ciphers import Cipher
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.ciphers.algorithms import AES256
from cryptography.hazmat.primitives.ciphers.modes import CBC
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat

# pytest
import pytest

# Zato
from zato.common.as2.common import EncryptionAlgorithm
from zato.common.as2.inbound import handle
from zato.common.as2.outbound import build_message
from zato.common.as2.partnership import new_partnership
from zato.common.as2.smime import decrypt, encrypt, new_part, sign, verify
from zato.common.typing_ import any_, anylist

# ################################################################################################################################
# ################################################################################################################################

# RFC 4130 section 6.1 - the AS2 version this implementation announces.
_as2_version = '1.2'

# RFC 4130 section 7.3 - the Disposition-Notification-Options grammar of a request
# for a signed receipt with an SHA-256 MIC.
_signed_receipt_options = 'signed-receipt-protocol=required, pkcs7-signature; signed-receipt-micalg=required, sha-256'

# RFC 4130 section 7.4.3 with RFC 8098 section 3.2.6 - the disposition field
# of a successfully processed message.
_disposition_processed = 'automatic-action/MDN-sent-automatically; processed'

# RFC 8098 section 3.1 - the report media type and its machine-readable part.
_report_content_type = 'multipart/report; report-type=disposition-notification'
_disposition_part_type = 'message/disposition-notification'

# RFC 5751 section 3.4.3.2 - the micalg parameter values.
_micalg_names = ('sha-1', 'sha-256', 'sha-384', 'sha-512')

# RFC 5652 sections 4, 5 and 6 with RFC 5083 - the CMS content type identifiers.
_oid_signed_data         = '1.2.840.113549.1.7.2'
_oid_enveloped_data      = '1.2.840.113549.1.7.3'
_oid_auth_enveloped_data = '1.2.840.113549.1.9.16.1.23'

# RFC 5652 section 11.2 - the message-digest signed attribute.
_oid_message_digest = '1.2.840.113549.1.9.4'

# RFC 8017 - RSAES-PKCS1-v1_5 key transport.
_oid_rsa = '1.2.840.113549.1.1.1'

# NIST algorithm identifiers - AES-256 in CBC and GCM modes.
_oid_aes256_cbc = '2.16.840.1.101.3.4.1.42'
_oid_aes256_gcm = '2.16.840.1.101.3.4.1.46'

# ################################################################################################################################
# ################################################################################################################################

_sender_identifier   = 'ZatoRetail'
_receiver_identifier = 'PartnerCorp'

# A small X12 purchase order interchange used as the payload throughout.
_edi_payload = b'ISA*00*          *00*          *ZZ*SENDERID       *ZZ*RECEIVERID     ' + \
    b'*260709*1200*U*00401*000000001*0*P*>~GS*PO*SENDERID*RECEIVERID*20260709*1200*1*X*004010~' + \
    b'ST*850*0001~BEG*00*SA*PO-2026-001**20260709~SE*3*0001~GE*1*1~IEA*1*000000001~'

_edi_content_type = 'application/edi-x12'

# The complete MIME entity around the payload, typed out byte by byte - what a signed
# or encrypted message covers per RFC 4130 section 7.3.1.
_edi_entity = b'Content-Type: application/edi-x12\r\nContent-Transfer-Encoding: binary\r\n\r\n' + _edi_payload

# ################################################################################################################################
# ################################################################################################################################

class _GCMParameters(Sequence):
    """ RFC 5084 section 3.2 - the AES-GCM nonce with the tag length, typed out
    from the specification instead of relying on any parser's built-in knowledge.
    """
    _fields = [
        ('nonce', OctetString),
        ('icv_len', Integer),
    ]

# ################################################################################################################################
# ################################################################################################################################

def _edi_part() -> 'any_':
    out = new_part(_edi_payload, _edi_content_type)
    return out

# ################################################################################################################################

def _make_sender_partnership() -> 'any_':
    out = new_partnership()

    out.as2_from = _sender_identifier
    out.as2_to = _receiver_identifier
    out.endpoint_url = 'https://partnercorp.example.com/as2'

    return out

# ################################################################################################################################

def _make_receiver_partnership() -> 'any_':
    out = new_partnership()

    out.as2_from = _receiver_identifier
    out.as2_to = _sender_identifier

    return out

# ################################################################################################################################

def _boundary_of(content_type:'str') -> 'bytes':
    """ Reads the boundary parameter out of a multipart content type with plain string
    operations - independent of any MIME parser in the code under test.
    """
    _, _, after = content_type.partition('boundary="')
    boundary, _, _ = after.partition('"')

    out = boundary.encode('ascii')
    return out

# ################################################################################################################################

def _split_multipart(data:'bytes', boundary:'bytes') -> 'anylist':
    """ Splits a multipart body into its parts with plain byte operations - each part
    is everything between the CRLF after one boundary delimiter and the CRLF
    before the next one, exactly as RFC 2046 frames it.
    """

    # Our response to produce
    out:'anylist' = []

    delimiter = b'--' + boundary
    sections = data.split(delimiter)

    # The first section is the preamble and the last one is the closing '--',
    # everything in between is one part framed by CRLF on both sides.
    for section in sections[1:-1]:
        part = section.removeprefix(b'\r\n')
        part = part.removesuffix(b'\r\n')
        out.append(part)

    return out

# ################################################################################################################################

def _mic_over(covered:'bytes') -> 'str':
    """ Recomputes an SHA-256 MIC with hashlib alone, in the base64-comma-algorithm
    form of RFC 4130 section 7.4.3.
    """
    digest = sha256(covered).digest()
    encoded_bytes = b64encode(digest)
    encoded = encoded_bytes.decode('ascii')

    out = f'{encoded}, sha-256'
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestHeaderGrammarConformance:
    """ RFC 4130 section 6 - the AS2 headers of an outbound message follow
    the literal grammar of the specification.
    """

    def test_headers_follow_the_literal_grammar(self, parties:'any_') -> 'None':
        partnership = _make_sender_partnership()

        _, headers, message_id, _ = build_message(partnership, parties.sender, _edi_payload)

        # Section 6.1 - the version and identity headers.
        assert headers['AS2-Version'] == _as2_version
        assert headers['AS2-From'] == _sender_identifier
        assert headers['AS2-To'] == _receiver_identifier
        assert headers['MIME-Version'] == '1.0'

        # Section 6.2 with RFC 5322 - the Message-ID is a bracketed id-left@id-right pair.
        assert message_id.startswith('<')
        assert message_id.endswith('>')
        assert '@' in message_id
        assert headers['Message-ID'] == message_id

        # Section 7.3 - the literal grammar of a signed receipt request.
        assert headers['Disposition-Notification-To'] == _sender_identifier
        assert headers['Disposition-Notification-Options'] == _signed_receipt_options

        # Section 5.2 with RFC 8551 - an encrypted message travels as enveloped-data.
        assert headers['Content-Type'].startswith('application/pkcs7-mime; smime-type=enveloped-data')

# ################################################################################################################################

    @pytest.mark.parametrize('algorithm', _micalg_names)
    def test_micalg_parameter_uses_the_literal_names(self, parties:'any_', algorithm:'str') -> 'None':
        part = _edi_part()

        signed = sign(part, parties.sender, digest_algorithm=algorithm)

        # RFC 5751 section 3.4.3.2 - the micalg value is the lowercase dashed name.
        assert f'micalg={algorithm}' in signed.content_type
        assert 'protocol="application/pkcs7-signature"' in signed.content_type

# ################################################################################################################################
# ################################################################################################################################

class TestMDNConformance:
    """ RFC 4130 section 7.4 with RFC 8098 - the receiver's MDN is a multipart/report
    whose machine-readable fields carry the literal disposition string and a MIC
    that recomputes with hashlib over the literally typed covered entity.
    """

    def test_report_layout_and_disposition_recompute(self, parties:'any_') -> 'None':
        sender_partnership = _make_sender_partnership()
        sender_partnership.mdn_signed = False

        body, headers, message_id, sender_mic = build_message(sender_partnership, parties.sender, _edi_payload)

        result = handle(body, headers, [_make_receiver_partnership()], parties.receiver)
        assert not result.is_error

        # The MDN is a multipart/report with the literal report type ..
        mdn_content_type = result.headers['Content-Type']
        assert mdn_content_type.startswith(_report_content_type)

        boundary = _boundary_of(mdn_content_type)
        parts = _split_multipart(result.body, boundary)

        # .. carrying the human-readable text part and the machine-readable one ..
        part_count = len(parts)
        assert part_count == 2

        machine_part = parts[1]
        machine_headers, _, machine_fields = machine_part.partition(b'\r\n\r\n')

        assert f'Content-Type: {_disposition_part_type}'.encode('ascii') in machine_headers

        # .. whose fields carry the literal disposition string and the answered Message-ID ..
        fields = machine_fields.decode('ascii')

        assert f'Disposition: {_disposition_processed}' in fields
        assert f'Original-Message-ID: {message_id}' in fields
        assert f'Final-Recipient: rfc822; {_receiver_identifier}' in fields

        # .. and a Received-Content-MIC that recomputes with hashlib alone
        # over the covered entity typed out byte by byte.
        expected_mic = _mic_over(_edi_entity)

        assert f'Received-Content-MIC: {expected_mic}' in fields
        assert sender_mic == expected_mic

# ################################################################################################################################
# ################################################################################################################################

class TestSignedDataRecompute:
    """ RFC 5652 sections 5.4 and 5.6 - the SignedData of a multipart/signed message
    verifies after an independent DER parse: the message digest recomputes with
    hashlib over the covered part and the signature verifies with the public key alone.
    """

    def test_signature_recomputes_independently(self, parties:'any_') -> 'None':
        part = _edi_part()
        signed = sign(part, parties.sender)

        # Split the multipart with plain byte operations ..
        boundary = _boundary_of(signed.content_type)
        parts = _split_multipart(signed.data, boundary)

        part_count = len(parts)
        assert part_count == 2

        covered = parts[0]
        signature_part = parts[1]

        # .. the covered part is the literally typed MIME entity ..
        assert covered == _edi_entity

        # .. the second part carries the base64 of a DER SignedData ..
        _, _, signature_body = signature_part.partition(b'\r\n\r\n')
        signature_der = b64decode(signature_body)

        content_info = ContentInfo.load(signature_der)
        assert content_info['content_type'].dotted == _oid_signed_data

        signed_data = content_info['content']
        signer_info = signed_data['signer_infos'][0]

        # .. the declared digest algorithm is SHA-256 ..
        assert signer_info['digest_algorithm']['algorithm'].native == 'sha256'

        # .. the message-digest attribute recomputes with hashlib over the covered part ..
        declared_digest = b''

        for attribute in signer_info['signed_attrs']:
            if attribute['type'].dotted == _oid_message_digest:
                declared_digest = attribute['values'][0].native

        recomputed_digest = sha256(covered).digest()
        assert declared_digest == recomputed_digest

        # .. and the signature verifies with the public key alone - RFC 5652 section 5.4
        # says the signature covers the signed attributes re-encoded as an explicit SET OF.
        signed_attrs_der = signer_info['signed_attrs'].dump()
        set_of_der = b'\x31' + signed_attrs_der[1:]

        public_key = parties.sender.signing_certificate.public_key()

        # Raises InvalidSignature if the value does not verify.
        public_key.verify(signer_info['signature'].native, set_of_der, PKCS1v15(), SHA256())

# ################################################################################################################################
# ################################################################################################################################

class TestEnvelopedDataRecompute:
    """ RFC 5652 section 6 and RFC 5083 - the enveloped entity decrypts from scratch
    with cryptography primitives only, using nothing but what the DER itself declares.
    """

    def test_cbc_envelope_decrypts_with_primitives_alone(self, parties:'any_') -> 'None':
        part = _edi_part()
        encrypted = encrypt(part, parties.sender.peer_encryption_certificate, EncryptionAlgorithm.AES_256_CBC)

        # The DER declares an EnvelopedData with RSA key transport and AES-256-CBC ..
        content_info = ContentInfo.load(encrypted.data)
        assert content_info['content_type'].dotted == _oid_enveloped_data

        enveloped = content_info['content']
        recipient = enveloped['recipient_infos'][0].chosen
        assert recipient['key_encryption_algorithm']['algorithm'].dotted == _oid_rsa

        content_info_encrypted = enveloped['encrypted_content_info']
        algorithm = content_info_encrypted['content_encryption_algorithm']
        assert algorithm['algorithm'].dotted == _oid_aes256_cbc

        # .. the content key unwraps with the private key and PKCS1v15 alone ..
        wrapped_key = recipient['encrypted_key'].native
        content_key = parties.receiver.decryption_key.decrypt(wrapped_key, PKCS1v15())

        # .. the ciphertext decrypts with a bare AES-CBC cipher and the declared IV ..
        initialization_vector = algorithm['parameters'].native
        ciphertext = content_info_encrypted['encrypted_content'].native

        decryptor = Cipher(AES256(content_key), CBC(initialization_vector)).decryptor()
        padded = decryptor.update(ciphertext) + decryptor.finalize()

        # .. and stripping the PKCS#7 padding by hand yields the literally typed entity.
        pad_length = padded[-1]
        plaintext = padded[:-pad_length]

        assert plaintext == _edi_entity

# ################################################################################################################################

    def test_gcm_envelope_decrypts_with_primitives_alone(self, parties:'any_') -> 'None':
        part = _edi_part()
        encrypted = encrypt(part, parties.sender.peer_encryption_certificate, EncryptionAlgorithm.AES_256_GCM)

        # The DER declares an AuthEnvelopedData with AES-256-GCM ..
        content_info = ContentInfo.load(encrypted.data)
        assert content_info['content_type'].dotted == _oid_auth_enveloped_data

        enveloped = content_info['content']
        recipient = enveloped['recipient_infos'][0].chosen
        assert recipient['key_encryption_algorithm']['algorithm'].dotted == _oid_rsa

        content_info_encrypted = enveloped['auth_encrypted_content_info']
        algorithm = content_info_encrypted['content_encryption_algorithm']
        assert algorithm['algorithm'].dotted == _oid_aes256_gcm

        # .. the content key unwraps with the private key and PKCS1v15 alone ..
        wrapped_key = recipient['encrypted_key'].native
        content_key = parties.receiver.decryption_key.decrypt(wrapped_key, PKCS1v15())

        # .. and the ciphertext decrypts with a bare AESGCM cipher, the declared nonce
        # and the authentication tag the structure carries next to the content.
        parameters_der = algorithm['parameters'].dump()
        parameters = _GCMParameters.load(parameters_der)
        nonce = parameters['nonce'].native

        ciphertext = content_info_encrypted['encrypted_content'].native
        tag = enveloped['mac'].native

        plaintext = AESGCM(content_key).decrypt(nonce, ciphertext + tag, None)

        assert plaintext == _edi_entity

# ################################################################################################################################
# ################################################################################################################################

class TestOpenSSLOracle:
    """ The openssl CLI as the third-party oracle - what we sign and encrypt,
    openssl verifies and decrypts, and what openssl signs and encrypts,
    we verify and decrypt.
    """

    def test_our_signature_verifies_with_openssl(self, parties:'any_', tmp_path:'Path') -> 'None':
        part = _edi_part()
        signed = sign(part, parties.sender)

        # Wrap the multipart in a full S/MIME entity for the CLI ..
        message_path = tmp_path / 'message.smime'
        ca_path = tmp_path / 'ca.pem'
        content_path = tmp_path / 'content.bin'

        entity = b'MIME-Version: 1.0\r\nContent-Type: ' + signed.content_type.encode('ascii') + b'\r\n\r\n' + signed.data

        _ = message_path.write_bytes(entity)
        _ = ca_path.write_bytes(parties.ca_certificate.public_bytes(Encoding.PEM))

        # .. and have an implementation we did not write verify the signature.
        command = [
            'openssl', 'cms', '-verify',
            '-in', str(message_path),
            '-inform', 'SMIME',
            '-CAfile', str(ca_path),
            '-out', str(content_path),
        ]
        _ = subprocess_run(command, check=True, capture_output=True)

        # What openssl recovered is the covered entity, byte for byte.
        assert content_path.read_bytes() == _edi_entity

# ################################################################################################################################

    def test_openssl_signature_verifies_with_ours(self, parties:'any_', tmp_path:'Path') -> 'None':
        # Sign with an implementation we did not write ..
        payload_path = tmp_path / 'payload.bin'
        key_path = tmp_path / 'sender-key.pem'
        certificate_path = tmp_path / 'sender-cert.pem'
        signature_path = tmp_path / 'signature.der'

        key_pem = parties.sender.signing_key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption())
        certificate_pem = parties.sender.signing_certificate.public_bytes(Encoding.PEM)

        _ = payload_path.write_bytes(_edi_entity)
        _ = key_path.write_bytes(key_pem)
        _ = certificate_path.write_bytes(certificate_pem)

        command = [
            'openssl', 'cms', '-sign', '-binary',
            '-md', 'sha256',
            '-in', str(payload_path),
            '-signer', str(certificate_path),
            '-inkey', str(key_path),
            '-outform', 'DER',
            '-out', str(signature_path),
        ]
        _ = subprocess_run(command, check=True, capture_output=True)

        # .. frame the detached signature in the multipart/signed layout of RFC 1847,
        # with the CRLF boundary framing of RFC 2046 ..
        signature_base64 = b64encode(signature_path.read_bytes())

        boundary = b'openssl-oracle-boundary'
        body = b'--' + boundary + b'\r\n' + \
            _edi_entity + b'\r\n' + \
            b'--' + boundary + b'\r\n' + \
            b'Content-Type: application/pkcs7-signature\r\n' + \
            b'Content-Transfer-Encoding: base64\r\n\r\n' + \
            signature_base64 + b'\r\n' + \
            b'--' + boundary + b'--\r\n'

        content_type = 'multipart/signed; protocol="application/pkcs7-signature"; ' + \
            f'micalg=sha-256; boundary="{boundary.decode("ascii")}"'

        # .. and verify it with ours - the recovered content is the entity openssl signed.
        signed = new_part(body, content_type)
        result = verify(signed, parties.receiver)

        assert result.part.data == _edi_payload
        assert result.part.content_type == _edi_content_type

# ################################################################################################################################

    def test_our_envelope_decrypts_with_openssl(self, parties:'any_', tmp_path:'Path') -> 'None':
        part = _edi_part()
        encrypted = encrypt(part, parties.sender.peer_encryption_certificate, EncryptionAlgorithm.AES_256_CBC)

        envelope_path = tmp_path / 'envelope.der'
        key_path = tmp_path / 'receiver-key.pem'
        certificate_path = tmp_path / 'receiver-cert.pem'
        plaintext_path = tmp_path / 'plaintext.bin'

        key_pem = parties.receiver.decryption_key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption())
        certificate_pem = parties.sender.peer_encryption_certificate.public_bytes(Encoding.PEM)

        _ = envelope_path.write_bytes(encrypted.data)
        _ = key_path.write_bytes(key_pem)
        _ = certificate_path.write_bytes(certificate_pem)

        # Decrypt with an implementation we did not write.
        command = [
            'openssl', 'cms', '-decrypt',
            '-inform', 'DER',
            '-in', str(envelope_path),
            '-inkey', str(key_path),
            '-recip', str(certificate_path),
            '-out', str(plaintext_path),
        ]
        _ = subprocess_run(command, check=True, capture_output=True)

        assert plaintext_path.read_bytes() == _edi_entity

# ################################################################################################################################

    def test_openssl_envelope_decrypts_with_ours(self, parties:'any_', tmp_path:'Path') -> 'None':
        # Encrypt to the receiver with an implementation we did not write ..
        payload_path = tmp_path / 'payload.bin'
        certificate_path = tmp_path / 'recipient.pem'
        envelope_path = tmp_path / 'envelope.der'

        certificate_pem = parties.sender.peer_encryption_certificate.public_bytes(Encoding.PEM)

        _ = payload_path.write_bytes(_edi_entity)
        _ = certificate_path.write_bytes(certificate_pem)

        command = [
            'openssl', 'cms', '-encrypt', '-aes-256-cbc', '-binary',
            '-outform', 'DER',
            '-in', str(payload_path),
            '-out', str(envelope_path),
            str(certificate_path),
        ]
        _ = subprocess_run(command, check=True, capture_output=True)

        # .. and decrypt it with ours.
        encrypted = new_part(envelope_path.read_bytes(), 'application/pkcs7-mime; smime-type=enveloped-data')
        decrypted = decrypt(encrypted, parties.receiver)

        assert decrypted.data == _edi_payload
        assert decrypted.content_type == _edi_content_type

# ################################################################################################################################
# ################################################################################################################################
