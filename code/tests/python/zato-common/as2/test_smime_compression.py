# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# Zato
from .smime_helpers import EDI_Content_Type as _edi_content_type, EDI_Payload as _edi_payload, new_edi_part
from zato.common.as2.common import AS2Error, AS2ProtocolException
from zato.common.as2.smime import compress, compression, decompress, encrypt, new_part, sign, verify

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    from .conftest import TestParties
    TestParties = TestParties

# ################################################################################################################################
# ################################################################################################################################

class TestCompression:
    """ Compressing an entity and inflating it back, on its own and around a signature.
    """

    def test_compress_decompress_roundtrip(self) -> 'None':
        part = new_edi_part()

        compressed = compress(part)

        assert 'smime-type=compressed-data' in compressed.content_type
        assert _edi_payload not in compressed.data

        decompressed = decompress(compressed)

        assert decompressed.data == _edi_payload
        assert decompressed.content_type == _edi_content_type

# ################################################################################################################################

    def test_compress_then_sign(self, parties:'TestParties') -> 'None':
        part = new_edi_part()

        compressed = compress(part)
        signed = sign(compressed, parties.sender)

        result = verify(signed, parties.receiver)

        assert 'smime-type=compressed-data' in result.part.content_type

        decompressed = decompress(result.part)

        assert decompressed.data == _edi_payload

# ################################################################################################################################

    def test_sign_then_compress(self, parties:'TestParties') -> 'None':
        part = new_edi_part()

        signed = sign(part, parties.sender)
        compressed = compress(signed)

        decompressed = decompress(compressed)

        assert decompressed.content_type.startswith('multipart/signed')

        result = verify(decompressed, parties.receiver)

        assert result.part.data == _edi_payload

# ################################################################################################################################

    def test_garbage_input_is_rejected(self) -> 'None':
        garbage = new_part(b'This is not a CMS structure at all', 'application/pkcs7-mime; smime-type=compressed-data')

        with pytest.raises(AS2ProtocolException) as exception_information:
            _ = decompress(garbage)

        assert exception_information.value.modifier == AS2Error.Decompression_Failed

# ################################################################################################################################

    def test_enveloped_input_is_rejected(self, parties:'TestParties') -> 'None':
        part = new_edi_part()

        encrypted = encrypt(part, parties.sender.peer_encryption_certificate)

        with pytest.raises(AS2ProtocolException) as exception_information:
            _ = decompress(encrypted)

        assert exception_information.value.modifier == AS2Error.Decompression_Failed

# ################################################################################################################################
# ################################################################################################################################

class TestDecompressionBounds:
    """ Decompression runs on unauthenticated input, so the expansion is watched as it happens
    rather than measured once it is over.
    """

    def test_a_decompression_bomb_is_rejected(self, monkeypatch:'any_') -> 'None':

        # A ceiling low enough to cross without building a genuinely huge input, so the test
        # exercises the same code path a real bomb would take.
        monkeypatch.setattr(compression, 'Max_Decompressed_Bytes', 1024)
        monkeypatch.setattr(compression, '_decompression_chunk_size', 256)

        # A megabyte of zero bytes compresses to about a kilobyte, which is the shape
        # of the attack - a small request expanding without limit on the receiving side.
        part = new_part(b'\x00' * (1024 * 1024), _edi_content_type)
        compressed = compress(part)

        with pytest.raises(AS2ProtocolException) as exception_information:
            _ = decompress(compressed)

        assert exception_information.value.modifier == AS2Error.Decompression_Failed
        assert 'larger than the maximum' in exception_information.value.detail

# ################################################################################################################################

    def test_content_under_the_ceiling_still_decompresses(self, monkeypatch:'any_') -> 'None':

        # The chunk size is deliberately smaller than the content, so the inflate loop
        # runs several rounds and its chunk-joining is exercised.
        monkeypatch.setattr(compression, '_decompression_chunk_size', 64)

        payload = _edi_payload * 100
        part = new_part(payload, _edi_content_type)

        compressed = compress(part)
        decompressed = decompress(compressed)

        assert decompressed.data == payload

# ################################################################################################################################

    def test_a_truncated_stream_is_rejected(self) -> 'None':
        part = new_edi_part()
        compressed = compress(part)

        # The zlib stream inside the CMS structure loses its tail, which a chunked
        # decompressor reports by never reaching the end of the stream.
        compressed.data = compressed.data[:-8]

        with pytest.raises(AS2ProtocolException) as exception_information:
            _ = decompress(compressed)

        assert exception_information.value.modifier == AS2Error.Decompression_Failed

# ################################################################################################################################
# ################################################################################################################################
