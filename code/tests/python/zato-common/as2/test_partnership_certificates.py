# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.as2.partnership import active_verification_certificates, is_certificate_entry_active, \
    new_partnership, select_encryption_certificate

# Zato
from .partnership_helpers import make_entry, Now, One_Day

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    from .conftest import TestParties
    TestParties = TestParties

# ################################################################################################################################
# ################################################################################################################################

class TestCertificateWindows:

    def test_entry_without_a_window_is_always_active(self) -> 'None':
        entry = make_entry(None)
        assert is_certificate_entry_active(entry, Now)

# ################################################################################################################################

    def test_entry_before_its_activation_date_is_not_active(self) -> 'None':
        entry = make_entry(None, valid_from=Now + One_Day)
        assert not is_certificate_entry_active(entry, Now)

# ################################################################################################################################

    def test_entry_past_its_expiry_date_is_not_active(self) -> 'None':
        entry = make_entry(None, valid_until=Now - One_Day)
        assert not is_certificate_entry_active(entry, Now)

# ################################################################################################################################

    def test_entry_inside_its_window_is_active(self) -> 'None':
        entry = make_entry(None, valid_from=Now - One_Day, valid_until=Now + One_Day)
        assert is_certificate_entry_active(entry, Now)

# ################################################################################################################################
# ################################################################################################################################

class TestVerificationCertificates:

    def test_all_currently_valid_certificates_are_accepted(self, parties:'TestParties') -> 'None':
        """ A migration window can have more than two certificates live at once -
        inbound verification accepts any of them.
        """
        old_certificate = parties.sender.signing_certificate_chain[0]
        new_certificate = parties.receiver.signing_certificate_chain[0]
        next_certificate = parties.ca_certificate

        old_entry = make_entry(old_certificate)
        new_entry = make_entry(new_certificate, valid_from=Now - One_Day)
        next_entry = make_entry(next_certificate, valid_from=Now - One_Day)

        partnership = new_partnership()
        partnership.verification_certificates.append(old_entry)
        partnership.verification_certificates.append(new_entry)
        partnership.verification_certificates.append(next_entry)

        accepted = active_verification_certificates(partnership, Now)

        assert accepted == [old_certificate, new_certificate, next_certificate]

# ################################################################################################################################

    def test_certificates_outside_their_window_are_not_accepted(self, parties:'TestParties') -> 'None':
        expired_certificate = parties.sender.signing_certificate_chain[0]
        current_certificate = parties.receiver.signing_certificate_chain[0]
        future_certificate = parties.ca_certificate

        expired_entry = make_entry(expired_certificate, valid_until=Now - One_Day)
        current_entry = make_entry(current_certificate)
        future_entry = make_entry(future_certificate, valid_from=Now + One_Day)

        partnership = new_partnership()
        partnership.verification_certificates.append(expired_entry)
        partnership.verification_certificates.append(current_entry)
        partnership.verification_certificates.append(future_entry)

        accepted = active_verification_certificates(partnership, Now)

        assert accepted == [current_certificate]

# ################################################################################################################################
# ################################################################################################################################

class TestCertificateOwnDates:
    """ The configured rotation window is an operator's statement about a migration while the
    certificate's own dates are the issuer's statement about the key - an entry is in service
    only when both cover the moment.
    """

    def test_an_expired_certificate_is_not_active(self, make_dated_pair:'any_') -> 'None':
        pair = make_dated_pair('as2-expired', Now - (10 * One_Day), Now - One_Day)

        # The configured window says nothing, so the certificate's own dates decide.
        entry = make_entry(pair.certificate)

        assert not is_certificate_entry_active(entry, Now)

# ################################################################################################################################

    def test_a_not_yet_valid_certificate_is_not_active(self, make_dated_pair:'any_') -> 'None':
        pair = make_dated_pair('as2-future', Now + One_Day, Now + (10 * One_Day))

        entry = make_entry(pair.certificate)

        assert not is_certificate_entry_active(entry, Now)

# ################################################################################################################################

    def test_an_open_configured_window_does_not_revive_an_expired_certificate(
        self, make_dated_pair:'any_') -> 'None':
        pair = make_dated_pair('as2-expired-open-window', Now - (10 * One_Day), Now - One_Day)

        # A configuration that forgot to retire the entry leaves the window wide open,
        # which is exactly the case the certificate's own dates have to catch.
        entry = make_entry(pair.certificate, valid_from=Now - (20 * One_Day), valid_until=Now + (20 * One_Day))

        assert not is_certificate_entry_active(entry, Now)

# ################################################################################################################################

    def test_an_expired_certificate_does_not_verify_inbound_signatures(self, make_dated_pair:'any_') -> 'None':
        expired = make_dated_pair('as2-expired-signer', Now - (10 * One_Day), Now - One_Day)
        current = make_dated_pair('as2-current-signer', Now - One_Day, Now + (10 * One_Day))

        expired_entry = make_entry(expired.certificate)
        current_entry = make_entry(current.certificate)

        partnership = new_partnership()
        partnership.verification_certificates.append(expired_entry)
        partnership.verification_certificates.append(current_entry)

        accepted = active_verification_certificates(partnership, Now)

        assert accepted == [current.certificate]

# ################################################################################################################################

    def test_an_expired_certificate_is_not_selected_for_encryption(self, make_dated_pair:'any_') -> 'None':
        expired = make_dated_pair('as2-expired-recipient', Now - (10 * One_Day), Now - One_Day)

        expired_entry = make_entry(expired.certificate)

        partnership = new_partnership()
        partnership.encryption_certificates.append(expired_entry)

        assert select_encryption_certificate(partnership, Now) is None

# ################################################################################################################################
# ################################################################################################################################

class TestEncryptionCertificateSelection:

    def test_nothing_is_selected_from_an_empty_list(self) -> 'None':
        partnership = new_partnership()
        assert select_encryption_certificate(partnership, Now) is None

# ################################################################################################################################

    def test_the_only_certificate_is_selected(self, parties:'TestParties') -> 'None':
        certificate = parties.receiver.signing_certificate_chain[0]

        entry = make_entry(certificate)

        partnership = new_partnership()
        partnership.encryption_certificates.append(entry)

        assert select_encryption_certificate(partnership, Now) is certificate

# ################################################################################################################################

    def test_current_certificate_wins_before_the_activation_date(self, parties:'TestParties') -> 'None':
        current_certificate = parties.receiver.signing_certificate_chain[0]
        next_certificate = parties.sender.signing_certificate_chain[0]

        current_entry = make_entry(current_certificate)
        next_entry = make_entry(next_certificate, valid_from=Now + One_Day)

        partnership = new_partnership()
        partnership.encryption_certificates.append(current_entry)
        partnership.encryption_certificates.append(next_entry)

        assert select_encryption_certificate(partnership, Now) is current_certificate

# ################################################################################################################################

    def test_next_certificate_wins_once_its_activation_date_passes(self, parties:'TestParties') -> 'None':
        current_certificate = parties.receiver.signing_certificate_chain[0]
        next_certificate = parties.sender.signing_certificate_chain[0]

        current_entry = make_entry(current_certificate)
        next_entry = make_entry(next_certificate, valid_from=Now - One_Day)

        partnership = new_partnership()
        partnership.encryption_certificates.append(current_entry)
        partnership.encryption_certificates.append(next_entry)

        assert select_encryption_certificate(partnership, Now) is next_certificate

# ################################################################################################################################

    def test_most_recently_activated_certificate_wins_among_several_live_ones(self, parties:'TestParties') -> 'None':
        oldest_certificate = parties.receiver.signing_certificate_chain[0]
        older_certificate = parties.sender.signing_certificate_chain[0]
        newest_certificate = parties.ca_certificate

        oldest_entry = make_entry(oldest_certificate)
        newest_entry = make_entry(newest_certificate, valid_from=Now - One_Day)
        older_entry = make_entry(older_certificate, valid_from=Now - (2 * One_Day))

        partnership = new_partnership()
        partnership.encryption_certificates.append(oldest_entry)
        partnership.encryption_certificates.append(newest_entry)
        partnership.encryption_certificates.append(older_entry)

        assert select_encryption_certificate(partnership, Now) is newest_certificate

# ################################################################################################################################
# ################################################################################################################################
