# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.as2.common import DigestAlgorithm, EncryptionAlgorithm, MDNMode
from zato.common.as2.profiles import EPCIS_Content_Type, FDA_Production_Identifier, new_default_partnership, \
    new_dscsa_partnership, new_fda_esg_partnership, new_sha1_3des_partnership, new_walmart_partnership

# ################################################################################################################################
# ################################################################################################################################

class TestProfiles:

    def test_default_partnership(self) -> 'None':
        partnership = new_default_partnership()

        assert partnership.sign is True
        assert partnership.sign_algorithm == DigestAlgorithm.SHA256
        assert partnership.encrypt is True
        assert partnership.encryption_algorithm == EncryptionAlgorithm.AES_128_CBC
        assert partnership.compress is True
        assert partnership.mdn_mode == MDNMode.Sync
        assert partnership.mdn_signed is True
        assert partnership.mdn_mic_algorithms == [DigestAlgorithm.SHA256]

# ################################################################################################################################

    def test_walmart_partnership(self) -> 'None':
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

# ################################################################################################################################

    def test_sha1_3des_partnership(self) -> 'None':
        partnership = new_sha1_3des_partnership()

        assert partnership.sign is True
        assert partnership.sign_algorithm == DigestAlgorithm.SHA1
        assert partnership.mdn_mic_algorithms == [DigestAlgorithm.SHA1]

        # 3DES travels in both directions with these partners.
        assert partnership.encrypt is True
        assert partnership.encryption_algorithm == EncryptionAlgorithm.DES_EDE3_CBC

# ################################################################################################################################

    def test_fda_esg_partnership(self) -> 'None':
        partnership = new_fda_esg_partnership()

        assert partnership.as2_to == FDA_Production_Identifier

        assert partnership.sign is True
        assert partnership.sign_algorithm == DigestAlgorithm.SHA256

        # AES-CBC and never GCM, which the gateway rejects.
        assert partnership.encrypt is True
        assert partnership.encryption_algorithm == EncryptionAlgorithm.AES_256_CBC

        assert partnership.mdn_mode == MDNMode.Async
        assert partnership.mdn_signed is True

# ################################################################################################################################

    def test_dscsa_partnership(self) -> 'None':
        partnership = new_dscsa_partnership()

        assert partnership.content_type == EPCIS_Content_Type

        assert partnership.sign is True
        assert partnership.encrypt is True
        assert partnership.mdn_mode == MDNMode.Sync
        assert partnership.mdn_signed is True

# ################################################################################################################################
# ################################################################################################################################
