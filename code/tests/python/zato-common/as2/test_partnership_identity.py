# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.as2.common import DigestAlgorithm
from zato.common.as2.config import build_partnership
from zato.common.as2.partnership import match_partnership, new_partnership, quote_as2_identifier, \
    unquote_as2_identifier

# Zato
from .partnership_helpers import make_entry, partnership_config, Receiver_Identifier, Sender_Identifier

# ################################################################################################################################
# ################################################################################################################################

class TestNewPartnership:

    def test_fresh_partnership_has_its_list_fields_in_place(self) -> 'None':
        partnership = new_partnership()

        assert partnership.mdn_mic_algorithms == [DigestAlgorithm.SHA256]
        assert partnership.verification_certificates == []
        assert partnership.encryption_certificates == []

# ################################################################################################################################

    def test_list_fields_are_not_shared_between_instances(self) -> 'None':
        first = new_partnership()
        second = new_partnership()

        entry = make_entry(None)

        first.verification_certificates.append(entry)
        first.mdn_mic_algorithms.append(DigestAlgorithm.SHA512)

        assert second.verification_certificates == []
        assert second.mdn_mic_algorithms == [DigestAlgorithm.SHA256]

# ################################################################################################################################

    def test_edi_identity_is_empty_by_default(self) -> 'None':
        partnership = new_partnership()

        assert partnership.isa_qualifier == ''
        assert partnership.isa_id == ''
        assert partnership.gs_id == ''
        assert partnership.unb_id == ''

# ################################################################################################################################
# ################################################################################################################################

class TestIdentifierQuoting:

    def test_atom_identifiers_travel_bare(self) -> 'None':
        assert quote_as2_identifier('PartnerCorp') == 'PartnerCorp'
        assert quote_as2_identifier('partner-corp_01') == 'partner-corp_01'

# ################################################################################################################################

    def test_identifiers_with_spaces_and_colons_are_quoted(self) -> 'None':

        # Certification events assign identifiers that deliberately contain spaces and colons.
        assert quote_as2_identifier('Partner Corp') == '"Partner Corp"'
        assert quote_as2_identifier('Partner:Corp') == '"Partner:Corp"'

# ################################################################################################################################

    def test_embedded_quotes_and_backslashes_are_escaped(self) -> 'None':
        assert quote_as2_identifier('Partner "The Best" Corp') == '"Partner \\"The Best\\" Corp"'
        assert quote_as2_identifier('Partner\\Corp') == '"Partner\\\\Corp"'

# ################################################################################################################################

    def test_unquoting_undoes_the_quoting(self) -> 'None':
        values = ['PartnerCorp', 'Partner Corp', 'Partner:Corp', 'Partner "The Best" Corp', 'Partner\\Corp']

        for value in values:
            quoted = quote_as2_identifier(value)
            assert unquote_as2_identifier(quoted) == value

# ################################################################################################################################
# ################################################################################################################################

class TestMatchPartnership:

    def test_identities_match_crosswise(self) -> 'None':
        partnership = new_partnership()
        partnership.as2_from = Sender_Identifier
        partnership.as2_to = Receiver_Identifier

        # The incoming message's AS2-From is the partner and its AS2-To is us.
        matched = match_partnership([partnership], Receiver_Identifier, Sender_Identifier)
        assert matched is partnership

# ################################################################################################################################

    def test_unknown_pair_matches_nothing(self) -> 'None':
        partnership = new_partnership()
        partnership.as2_from = Sender_Identifier
        partnership.as2_to = Receiver_Identifier

        matched = match_partnership([partnership], Sender_Identifier, Receiver_Identifier)
        assert matched is None

# ################################################################################################################################
# ################################################################################################################################

class TestEDIIdentity:

    def test_edi_identifiers_come_from_configuration(self) -> 'None':
        config = partnership_config()

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
