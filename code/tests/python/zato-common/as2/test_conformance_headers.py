# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The AS2 header grammar of RFC 4130 section 6 and the micalg names of RFC 5751,
# with every expected value typed out literally from the governing document.

# pytest
import pytest

# Zato
from zato.common.as2.outbound import build_message
from zato.common.as2.smime import sign

# Zato
from .conformance_helpers import edi_part, EDI_Payload, make_sender_partnership, Receiver_Identifier, Sender_Identifier

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

# RFC 4130 section 6.1 - the AS2 version this implementation announces.
_as2_version = '1.2'

# RFC 4130 section 7.3 - the Disposition-Notification-Options grammar of a request
# for a signed receipt with an SHA-256 MIC.
_signed_receipt_options = 'signed-receipt-protocol=required, pkcs7-signature; signed-receipt-micalg=required, sha-256'

# RFC 5751 section 3.4.3.2 - the micalg parameter values.
_micalg_names = ('sha-1', 'sha-256', 'sha-384', 'sha-512')

# ################################################################################################################################
# ################################################################################################################################

class TestHeaderGrammarConformance:
    """ RFC 4130 section 6 - the AS2 headers of an outbound message follow
    the literal grammar of the specification.
    """

    def test_headers_follow_the_literal_grammar(self, parties:'any_') -> 'None':
        partnership = make_sender_partnership()

        _, headers, message_id, _ = build_message(partnership, parties.sender, EDI_Payload)

        # Section 6.1 - the version and identity headers.
        assert headers['AS2-Version'] == _as2_version
        assert headers['AS2-From'] == Sender_Identifier
        assert headers['AS2-To'] == Receiver_Identifier
        assert headers['MIME-Version'] == '1.0'

        # Section 6.2 with RFC 5322 - the Message-ID is a bracketed id-left@id-right pair.
        assert message_id.startswith('<')
        assert message_id.endswith('>')
        assert '@' in message_id
        assert headers['Message-ID'] == message_id

        # Section 7.3 - the literal grammar of a signed receipt request.
        assert headers['Disposition-Notification-To'] == Sender_Identifier
        assert headers['Disposition-Notification-Options'] == _signed_receipt_options

        # Section 5.2 with RFC 8551 - an encrypted message travels as enveloped-data.
        content_type = headers['Content-Type']
        assert content_type.startswith('application/pkcs7-mime; smime-type=enveloped-data')

# ################################################################################################################################

    @pytest.mark.parametrize('algorithm', _micalg_names)
    def test_micalg_parameter_uses_the_literal_names(self, parties:'any_', algorithm:'str') -> 'None':
        part = edi_part()

        signed = sign(part, parties.sender, digest_algorithm=algorithm)

        # RFC 5751 section 3.4.3.2 - the micalg value is the lowercase dashed name.
        assert f'micalg={algorithm}' in signed.content_type
        assert 'protocol="application/pkcs7-signature"' in signed.content_type

# ################################################################################################################################
# ################################################################################################################################
