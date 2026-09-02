# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timedelta, timezone

# Zato
from zato.common.as2.common import MDNMode
from zato.common.as2.config import build_partnership
from zato.common.as2.partnership import active_verification_certificates, select_encryption_certificate

# Zato
from .partnership_helpers import certificate_to_pem, partnership_config, Receiver_Identifier, Sender_Identifier

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from .conftest import TestParties
    TestParties = TestParties

# ################################################################################################################################
# ################################################################################################################################

class TestConfigBridging:

    def test_scalar_fields_come_from_configuration(self) -> 'None':
        config = partnership_config()

        config['mdn_mode'] = MDNMode.Async
        config['async_mdn_url'] = 'https://zatoretail.example.com/zato/as2/mdn'
        config['compress'] = True
        config['http_timeout_seconds'] = 120

        partnership = build_partnership(config)

        assert partnership.as2_from == Sender_Identifier
        assert partnership.as2_to == Receiver_Identifier
        assert partnership.endpoint_url == 'https://partnercorp.example.com/as2'
        assert partnership.mdn_mode == MDNMode.Async
        assert partnership.async_mdn_url == 'https://zatoretail.example.com/zato/as2/mdn'
        assert partnership.compress is True
        assert partnership.http_timeout_seconds == 120

# ################################################################################################################################

    def test_empty_certificate_fields_leave_the_lists_empty(self) -> 'None':
        config = partnership_config()
        partnership = build_partnership(config)

        assert partnership.verification_certificates == []
        assert partnership.encryption_certificates == []

# ################################################################################################################################

    def test_current_certificate_joins_both_lists_without_a_window(self, parties:'TestParties') -> 'None':
        certificate = parties.receiver.signing_certificate_chain[0]

        config = partnership_config()
        config['as2_partner_cert'] = certificate_to_pem(certificate)

        partnership = build_partnership(config)

        assert len(partnership.verification_certificates) == 1
        assert len(partnership.encryption_certificates) == 1

        entry = partnership.verification_certificates[0]

        assert entry.certificate == certificate
        assert entry.valid_from is None
        assert entry.valid_until is None

# ################################################################################################################################

    def test_next_certificate_carries_its_activation_date(self, parties:'TestParties') -> 'None':
        current_certificate = parties.receiver.signing_certificate_chain[0]
        next_certificate = parties.sender.signing_certificate_chain[0]

        # The rotation activates ten days from now - the fixture certificates are valid from yesterday
        # for a year, so both probes below fall inside the certificates' own dates.
        now = datetime.now(timezone.utc)
        activation_day = now + timedelta(days=10)
        activation_date = activation_day.date()

        config = partnership_config()
        config['as2_partner_cert'] = certificate_to_pem(current_certificate)
        config['as2_partner_next_cert'] = certificate_to_pem(next_certificate)
        config['as2_partner_next_cert_from'] = activation_date.isoformat()

        partnership = build_partnership(config)

        assert len(partnership.verification_certificates) == 2

        next_entry = partnership.verification_certificates[1]
        expected_activation = datetime(activation_date.year, activation_date.month, activation_date.day, tzinfo=timezone.utc)

        assert next_entry.certificate == next_certificate
        assert next_entry.valid_from == expected_activation

        # Before the activation date the current certificate is the one to encrypt to ..
        before = now
        assert select_encryption_certificate(partnership, before) == current_certificate

        # .. after it, the next one - while verification accepts both throughout the overlap.
        after = now + timedelta(days=20)
        assert select_encryption_certificate(partnership, after) == next_certificate
        assert active_verification_certificates(partnership, after) == [current_certificate, next_certificate]

# ################################################################################################################################

    def test_next_certificate_without_an_activation_date_is_accepted_immediately(self, parties:'TestParties') -> 'None':
        next_certificate = parties.sender.signing_certificate_chain[0]

        config = partnership_config()
        config['as2_partner_next_cert'] = certificate_to_pem(next_certificate)

        partnership = build_partnership(config)

        entry = partnership.verification_certificates[0]

        assert entry.certificate == next_certificate
        assert entry.valid_from is None

# ################################################################################################################################

    def test_a_pem_with_several_certificates_yields_one_entry_each(self, parties:'TestParties') -> 'None':
        first_certificate = parties.receiver.signing_certificate_chain[0]
        second_certificate = parties.sender.signing_certificate_chain[0]

        first_pem = certificate_to_pem(first_certificate)
        second_pem = certificate_to_pem(second_certificate)

        config = partnership_config()
        config['as2_partner_cert'] = first_pem + second_pem

        partnership = build_partnership(config)

        assert len(partnership.verification_certificates) == 2

        first_entry = partnership.verification_certificates[0]
        second_entry = partnership.verification_certificates[1]

        assert first_entry.certificate == first_certificate
        assert second_entry.certificate == second_certificate

# ################################################################################################################################
# ################################################################################################################################
