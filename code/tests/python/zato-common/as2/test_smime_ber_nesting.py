# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# Zato
from zato.common.as2.common import AS2Error, AS2MalformedCMSException, AS2ProtocolException
from zato.common.as2.smime import decompress, new_part
from zato.common.as2.smime.der import Max_BER_Depth, to_definite_der

# ################################################################################################################################
# ################################################################################################################################

class TestBERNestingBounds:
    """ The BER-to-DER re-encoding recurses once per nested element and runs before any trust
    decision, so a structure nested deeply enough is rejected as malformed instead of
    exhausting the interpreter stack.
    """

    def _nested_indefinite_der(self, depth:'int') -> 'bytes':
        """ Builds a chain of indefinite-length constructed elements nested to the given depth,
        which is what the recursion walks down.
        """
        out = b'\x05\x00'

        for _ in range(depth):
            out = b'\x30\x80' + out + b'\x00\x00'

        return out

# ################################################################################################################################

    def test_deeply_nested_ber_is_rejected_before_the_stack_runs_out(self) -> 'None':
        der = self._nested_indefinite_der(Max_BER_Depth + 10)

        with pytest.raises(AS2MalformedCMSException) as exception_information:
            _ = to_definite_der(der)

        assert 'deeper than the maximum' in str(exception_information.value)

# ################################################################################################################################

    def test_nesting_within_the_limit_is_normalized(self) -> 'None':
        der = self._nested_indefinite_der(4)

        normalized = to_definite_der(der)

        # The indefinite-length markers and their end-of-contents octets are gone.
        assert b'\x30\x80' not in normalized
        assert normalized.startswith(b'\x30')

# ################################################################################################################################

    def test_a_deeply_nested_entity_yields_a_clean_protocol_error(self) -> 'None':
        der = self._nested_indefinite_der(Max_BER_Depth + 10)

        # The pipeline reaches the normalizer through decompress and decrypt alike,
        # and the answer is a disposition modifier rather than an unhandled error.
        part = new_part(der, 'application/pkcs7-mime; smime-type=compressed-data')
        part.content_transfer_encoding = 'binary'

        with pytest.raises(AS2ProtocolException) as exception_information:
            _ = decompress(part)

        assert exception_information.value.modifier == AS2Error.Decompression_Failed

# ################################################################################################################################
# ################################################################################################################################
