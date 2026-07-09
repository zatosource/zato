# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timedelta, timezone

# cryptography
from cryptography.hazmat.primitives.serialization import Encoding

# Zato
from zato.common.as2.common import DigestAlgorithm, EncryptionAlgorithm, MDNMode
from zato.common.as2.config import build_partnership
from zato.common.as2.partnership import active_verification_certificates, CertificateEntry, is_certificate_entry_active, \
    match_partnership, new_partnership, quote_as2_identifier, select_encryption_certificate, unquote_as2_identifier
from zato.common.as2.profiles import EPCIS_Content_Type, FDA_Production_Identifier, new_default_partnership, \
    new_dscsa_partnership, new_fda_esg_partnership, new_legacy_partnership, new_walmart_partnership

# ################################################################################################################################
# ################################################################################################################################

_sender_identifier   = 'ZatoRetail'
_receiver_identifier = 'PartnerCorp'

# A fixed moment all the window checks run against, so the tests never depend on the clock.
_now = datetime(2026, 7, 10, 12, 0, 0, tzinfo=timezone.utc)

_one_day = timedelta(days=1)

# ################################################################################################################################
# ################################################################################################################################

def _certificate_to_pem(certificate):
    out = certificate.public_bytes(Encoding.PEM).decode('ascii')
    return out

# ################################################################################################################################

def _make_entry(certificate, valid_from=None, valid_until=None):
    out = CertificateEntry()

    out.certificate = certificate
    out.valid_from = valid_from
    out.valid_until = valid_until

    return out

# ################################################################################################################################

def _partnership_config():
    """ The flat configuration dict of one Dashboard-managed AS2 connection,
    with every field of the connection schema present.
    """
    out = {
        'as2_from': _sender_identifier,
        'as2_to': _receiver_identifier,

        'isa_qualifier': '',
        'isa_id': '',
        'gs_id': '',
        'unb_id': '',

        'endpoint_url': 'https://partnercorp.example.com/as2',
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
# ################################################################################################################################

class TestNewPartnership:

    def test_fresh_partnership_has_its_list_fields_in_place(self):
        partnership = new_partnership()

        assert partnership.mdn_mic_algorithms == [DigestAlgorithm.SHA256]
        assert partnership.verification_certificates == []
        assert partnership.encryption_certificates == []

    def test_list_fields_are_not_shared_between_instances(self):
        first = new_partnership()
        second = new_partnership()

        first.verification_certificates.append(_make_entry(None))
        first.mdn_mic_algorithms.append(DigestAlgorithm.SHA512)

        assert second.verification_certificates == []
        assert second.mdn_mic_algorithms == [DigestAlgorithm.SHA256]

    def test_edi_identity_is_empty_by_default(self):
        partnership = new_partnership()

        assert partnership.isa_qualifier == ''
        assert partnership.isa_id == ''
        assert partnership.gs_id == ''
        assert partnership.unb_id == ''

# ################################################################################################################################
# ################################################################################################################################

class TestIdentifierQuoting:

    def test_atom_identifiers_travel_bare(self):
        assert quote_as2_identifier('PartnerCorp') == 'PartnerCorp'
        assert quote_as2_identifier('partner-corp_01') == 'partner-corp_01'

    def test_identifiers_with_spaces_and_colons_are_quoted(self):

        # Certification events assign identifiers that deliberately contain spaces and colons.
        assert quote_as2_identifier('Partner Corp') == '"Partner Corp"'
        assert quote_as2_identifier('Partner:Corp') == '"Partner:Corp"'

    def test_embedded_quotes_and_backslashes_are_escaped(self):
        assert quote_as2_identifier('Partner "The Best" Corp') == '"Partner \\"The Best\\" Corp"'
        assert quote_as2_identifier('Partner\\Corp') == '"Partner\\\\Corp"'

    def test_unquoting_undoes_the_quoting(self):
        values = ['PartnerCorp', 'Partner Corp', 'Partner:Corp', 'Partner "The Best" Corp', 'Partner\\Corp']

        for value in values:
            quoted = quote_as2_identifier(value)
            assert unquote_as2_identifier(quoted) == value

# ################################################################################################################################
# ################################################################################################################################

class TestMatchPartnership:

    def test_identities_match_crosswise(self):
        partnership = new_partnership()
        partnership.as2_from = _sender_identifier
        partnership.as2_to = _receiver_identifier

        # The incoming message's AS2-From is the partner and its AS2-To is us.
        matched = match_partnership([partnership], _receiver_identifier, _sender_identifier)
        assert matched is partnership

    def test_unknown_pair_matches_nothing(self):
        partnership = new_partnership()
        partnership.as2_from = _sender_identifier
        partnership.as2_to = _receiver_identifier

        matched = match_partnership([partnership], _sender_identifier, _receiver_identifier)
        assert matched is None

# ################################################################################################################################
# ################################################################################################################################

class TestEDIIdentity:

    def test_edi_identifiers_come_from_configuration(self):
        config = _partnership_config()

        config['isa_qualifier'] = '01'
        config['isa_id'] = '0123456789'
        config['gs_id'] = 'PARTNERCORP'
        config['unb_id'] = 'PARTNERCORP:14'

        partnership = build_partnership(config)

        assert partnership.isa_qualifier == '01'
        assert partnership.isa_id == '0123456789'
        assert partnership.gs_id == 'PARTNERCORP'
        assert partnership.unb_id == 'PARTNERCORP:14'

# ################################################################################################################################
# ################################################################################################################################

class TestCertificateWindows:

    def test_entry_without_a_window_is_always_active(self):
        entry = _make_entry(None)
        assert is_certificate_entry_active(entry, _now)

    def test_entry_before_its_activation_date_is_not_active(self):
        entry = _make_entry(None, valid_from=_now + _one_day)
        assert not is_certificate_entry_active(entry, _now)

    def test_entry_past_its_expiry_date_is_not_active(self):
        entry = _make_entry(None, valid_until=_now - _one_day)
        assert not is_certificate_entry_active(entry, _now)

    def test_entry_inside_its_window_is_active(self):
        entry = _make_entry(None, valid_from=_now - _one_day, valid_until=_now + _one_day)
        assert is_certificate_entry_active(entry, _now)

# ################################################################################################################################
# ################################################################################################################################

class TestVerificationCertificates:

    def test_all_currently_valid_certificates_are_accepted(self, parties):
        """ A migration window can have more than two certificates live at once -
        inbound verification accepts any of them.
        """
        old_certificate = parties.sender.signing_certificate_chain[0]
        new_certificate = parties.receiver.signing_certificate_chain[0]
        next_certificate = parties.ca_certificate

        partnership = new_partnership()
        partnership.verification_certificates.append(_make_entry(old_certificate))
        partnership.verification_certificates.append(_make_entry(new_certificate, valid_from=_now - _one_day))
        partnership.verification_certificates.append(_make_entry(next_certificate, valid_from=_now - _one_day))

        accepted = active_verification_certificates(partnership, _now)

        assert accepted == [old_certificate, new_certificate, next_certificate]

    def test_certificates_outside_their_window_are_not_accepted(self, parties):
        expired_certificate = parties.sender.signing_certificate_chain[0]
        current_certificate = parties.receiver.signing_certificate_chain[0]
        future_certificate = parties.ca_certificate

        partnership = new_partnership()
        partnership.verification_certificates.append(_make_entry(expired_certificate, valid_until=_now - _one_day))
        partnership.verification_certificates.append(_make_entry(current_certificate))
        partnership.verification_certificates.append(_make_entry(future_certificate, valid_from=_now + _one_day))

        accepted = active_verification_certificates(partnership, _now)

        assert accepted == [current_certificate]

# ################################################################################################################################
# ################################################################################################################################

class TestEncryptionCertificateSelection:

    def test_nothing_is_selected_from_an_empty_list(self):
        partnership = new_partnership()
        assert select_encryption_certificate(partnership, _now) is None

    def test_the_only_certificate_is_selected(self, parties):
        certificate = parties.receiver.signing_certificate_chain[0]

        partnership = new_partnership()
        partnership.encryption_certificates.append(_make_entry(certificate))

        assert select_encryption_certificate(partnership, _now) is certificate

    def test_current_certificate_wins_before_the_activation_date(self, parties):
        current_certificate = parties.receiver.signing_certificate_chain[0]
        next_certificate = parties.sender.signing_certificate_chain[0]

        partnership = new_partnership()
        partnership.encryption_certificates.append(_make_entry(current_certificate))
        partnership.encryption_certificates.append(_make_entry(next_certificate, valid_from=_now + _one_day))

        assert select_encryption_certificate(partnership, _now) is current_certificate

    def test_next_certificate_wins_once_its_activation_date_passes(self, parties):
        current_certificate = parties.receiver.signing_certificate_chain[0]
        next_certificate = parties.sender.signing_certificate_chain[0]

        partnership = new_partnership()
        partnership.encryption_certificates.append(_make_entry(current_certificate))
        partnership.encryption_certificates.append(_make_entry(next_certificate, valid_from=_now - _one_day))

        assert select_encryption_certificate(partnership, _now) is next_certificate

    def test_most_recently_activated_certificate_wins_among_several_live_ones(self, parties):
        oldest_certificate = parties.receiver.signing_certificate_chain[0]
        older_certificate = parties.sender.signing_certificate_chain[0]
        newest_certificate = parties.ca_certificate

        partnership = new_partnership()
        partnership.encryption_certificates.append(_make_entry(oldest_certificate))
        partnership.encryption_certificates.append(_make_entry(newest_certificate, valid_from=_now - _one_day))
        partnership.encryption_certificates.append(_make_entry(older_certificate, valid_from=_now - (2 * _one_day)))

        assert select_encryption_certificate(partnership, _now) is newest_certificate

# ################################################################################################################################
# ################################################################################################################################

class TestConfigBridging:

    def test_scalar_fields_come_from_configuration(self):
        config = _partnership_config()

        config['mdn_mode'] = MDNMode.Async
        config['async_mdn_url'] = 'https://zatoretail.example.com/zato/as2/mdn'
        config['compress'] = True
        config['http_timeout_seconds'] = 120

        partnership = build_partnership(config)

        assert partnership.as2_from == _sender_identifier
        assert partnership.as2_to == _receiver_identifier
        assert partnership.endpoint_url == 'https://partnercorp.example.com/as2'
        assert partnership.mdn_mode == MDNMode.Async
        assert partnership.async_mdn_url == 'https://zatoretail.example.com/zato/as2/mdn'
        assert partnership.compress is True
        assert partnership.http_timeout_seconds == 120

    def test_empty_certificate_fields_leave_the_lists_empty(self):
        config = _partnership_config()
        partnership = build_partnership(config)

        assert partnership.verification_certificates == []
        assert partnership.encryption_certificates == []

    def test_current_certificate_joins_both_lists_without_a_window(self, parties):
        certificate = parties.receiver.signing_certificate_chain[0]

        config = _partnership_config()
        config['as2_partner_cert'] = _certificate_to_pem(certificate)

        partnership = build_partnership(config)

        assert len(partnership.verification_certificates) == 1
        assert len(partnership.encryption_certificates) == 1

        entry = partnership.verification_certificates[0]

        assert entry.certificate == certificate
        assert entry.valid_from is None
        assert entry.valid_until is None

    def test_next_certificate_carries_its_activation_date(self, parties):
        current_certificate = parties.receiver.signing_certificate_chain[0]
        next_certificate = parties.sender.signing_certificate_chain[0]

        config = _partnership_config()
        config['as2_partner_cert'] = _certificate_to_pem(current_certificate)
        config['as2_partner_next_cert'] = _certificate_to_pem(next_certificate)
        config['as2_partner_next_cert_from'] = '2026-09-01'

        partnership = build_partnership(config)

        assert len(partnership.verification_certificates) == 2

        next_entry = partnership.verification_certificates[1]
        expected_activation = datetime(2026, 9, 1, tzinfo=timezone.utc)

        assert next_entry.certificate == next_certificate
        assert next_entry.valid_from == expected_activation

        # Before the activation date the current certificate is the one to encrypt to ..
        before = datetime(2026, 8, 15, tzinfo=timezone.utc)
        assert select_encryption_certificate(partnership, before) == current_certificate

        # .. after it, the next one - while verification accepts both throughout the overlap.
        after = datetime(2026, 9, 15, tzinfo=timezone.utc)
        assert select_encryption_certificate(partnership, after) == next_certificate
        assert active_verification_certificates(partnership, after) == [current_certificate, next_certificate]

    def test_next_certificate_without_an_activation_date_is_accepted_immediately(self, parties):
        next_certificate = parties.sender.signing_certificate_chain[0]

        config = _partnership_config()
        config['as2_partner_next_cert'] = _certificate_to_pem(next_certificate)

        partnership = build_partnership(config)

        entry = partnership.verification_certificates[0]

        assert entry.certificate == next_certificate
        assert entry.valid_from is None

    def test_a_pem_with_several_certificates_yields_one_entry_each(self, parties):
        first_certificate = parties.receiver.signing_certificate_chain[0]
        second_certificate = parties.sender.signing_certificate_chain[0]

        config = _partnership_config()
        config['as2_partner_cert'] = _certificate_to_pem(first_certificate) + _certificate_to_pem(second_certificate)

        partnership = build_partnership(config)

        assert len(partnership.verification_certificates) == 2
        assert partnership.verification_certificates[0].certificate == first_certificate
        assert partnership.verification_certificates[1].certificate == second_certificate

# ################################################################################################################################
# ################################################################################################################################

class TestProfiles:

    def test_default_partnership(self):
        partnership = new_default_partnership()

        assert partnership.sign is True
        assert partnership.sign_algorithm == DigestAlgorithm.SHA256
        assert partnership.encrypt is True
        assert partnership.encryption_algorithm == EncryptionAlgorithm.AES_128_CBC
        assert partnership.compress is True
        assert partnership.mdn_mode == MDNMode.Sync
        assert partnership.mdn_signed is True
        assert partnership.mdn_mic_algorithms == [DigestAlgorithm.SHA256]

    def test_walmart_partnership(self):
        partnership = new_walmart_partnership()

        # SHA-256 is the only signing algorithm the partner accepts,
        # and the MDN is always synchronous, signed and SHA-256, never asynchronous.
        assert partnership.sign is True
        assert partnership.sign_algorithm == DigestAlgorithm.SHA256
        assert partnership.mdn_mode == MDNMode.Sync
        assert partnership.mdn_signed is True
        assert partnership.mdn_mic_algorithms == [DigestAlgorithm.SHA256]

        assert partnership.encrypt is True
        assert partnership.encryption_algorithm == EncryptionAlgorithm.AES_128_CBC
        assert partnership.compress is False

    def test_legacy_partnership(self):
        partnership = new_legacy_partnership()

        assert partnership.sign is True
        assert partnership.sign_algorithm == DigestAlgorithm.SHA1
        assert partnership.mdn_mic_algorithms == [DigestAlgorithm.SHA1]

        # 3DES is accepted from these partners on the way in only - outgoing
        # encryption never produces it.
        assert partnership.encrypt is True
        assert partnership.encryption_algorithm == EncryptionAlgorithm.AES_128_CBC

    def test_fda_esg_partnership(self):
        partnership = new_fda_esg_partnership()

        assert partnership.as2_to == FDA_Production_Identifier

        assert partnership.sign is True
        assert partnership.sign_algorithm == DigestAlgorithm.SHA256

        # AES-CBC and never GCM, which the gateway rejects.
        assert partnership.encrypt is True
        assert partnership.encryption_algorithm == EncryptionAlgorithm.AES_256_CBC

        assert partnership.mdn_mode == MDNMode.Async
        assert partnership.mdn_signed is True

    def test_dscsa_partnership(self):
        partnership = new_dscsa_partnership()

        assert partnership.content_type == EPCIS_Content_Type

        assert partnership.sign is True
        assert partnership.encrypt is True
        assert partnership.mdn_mode == MDNMode.Sync
        assert partnership.mdn_signed is True

# ################################################################################################################################
# ################################################################################################################################
