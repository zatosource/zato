# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# Zato
from .smime_helpers import EDI_Content_Type as _edi_content_type, EDI_Payload as _edi_payload
from zato.common.as2.common import AS2Error, AS2ProtocolException
from zato.common.as2.smime import new_part, serialize_part

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

class TestHeaderValueValidation:
    """ On an inner entity the header values were parsed out of plaintext the peer controls.
    Writing a control character back into a header block would produce bytes a downstream parser
    splits differently, so our idea of what the signature covers would stop matching the partner's.
    """

    @pytest.mark.parametrize('value', [
        'application/edi-x12\r\nX-Injected: yes',
        'application/edi-x12\nX-Injected: yes',
        'application/edi-x12\rX-Injected: yes',
        'application/edi-x12\x00',
        'application/edi-x12\x0b',
    ])
    def test_a_control_character_in_the_content_type_is_refused(self, value:'any_') -> 'None':
        part = new_part(_edi_payload, value)

        with pytest.raises(AS2ProtocolException) as exception_information:
            _ = serialize_part(part)

        assert exception_information.value.modifier == AS2Error.Unexpected_Processing_Error
        assert 'Content-Type' in exception_information.value.detail

# ################################################################################################################################

    def test_a_control_character_in_the_disposition_is_refused(self) -> 'None':
        part = new_part(_edi_payload, _edi_content_type)
        part.content_disposition = 'attachment; filename="po.edi"\r\nX-Injected: yes'

        with pytest.raises(AS2ProtocolException) as exception_information:
            _ = serialize_part(part)

        assert 'Content-Disposition' in exception_information.value.detail

# ################################################################################################################################

    def test_a_control_character_in_the_transfer_encoding_is_refused(self) -> 'None':
        part = new_part(_edi_payload, _edi_content_type)
        part.content_transfer_encoding = 'binary\r\nX-Injected: yes'

        with pytest.raises(AS2ProtocolException) as exception_information:
            _ = serialize_part(part)

        assert 'Content-Transfer-Encoding' in exception_information.value.detail

# ################################################################################################################################

    def test_a_non_ascii_character_is_refused(self) -> 'None':
        part = new_part(_edi_payload, 'application/edi-x12; name="zam\u00f3wienie.edi"')

        with pytest.raises(AS2ProtocolException) as exception_information:
            _ = serialize_part(part)

        assert 'Non-ASCII' in exception_information.value.detail

# ################################################################################################################################

    def test_ordinary_values_serialize_unchanged(self) -> 'None':
        part = new_part(_edi_payload, _edi_content_type)
        part.content_disposition = 'attachment; filename="po-850.edi"'

        serialized = serialize_part(part)

        assert b'Content-Type: application/edi-x12\r\n' in serialized
        assert b'Content-Disposition: attachment; filename="po-850.edi"\r\n' in serialized
        assert serialized.endswith(_edi_payload)

# ################################################################################################################################

    def test_a_tab_is_allowed_as_folding_whitespace(self) -> 'None':
        part = new_part(_edi_payload, 'application/edi-x12;\tname="po.edi"')

        serialized = serialize_part(part)

        assert b'application/edi-x12;\tname="po.edi"' in serialized

# ################################################################################################################################
# ################################################################################################################################
