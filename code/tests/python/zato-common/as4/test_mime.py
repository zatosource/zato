# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# Zato
from zato.common.as4.common import AS4ProtocolException, EbMSError
from zato.common.as4.mime_ import build_multipart, compress_part, decompress_part, parse_multipart
from zato.common.as4.outbound import new_part

# ################################################################################################################################
# ################################################################################################################################

class TestCompression:

    def test_compress_decompress_roundtrip(self):
        part = new_part(b'<Invoice>data</Invoice>')

        compress_part(part)
        assert part.compressed
        assert part.content_type == 'application/gzip'
        assert part.data != b'<Invoice>data</Invoice>'

        decompress_part(part)
        assert not part.compressed
        assert part.content_type == 'application/xml'
        assert part.data == b'<Invoice>data</Invoice>'

    def test_compression_is_deterministic(self):
        part1 = new_part(b'same bytes')
        part2 = new_part(b'same bytes')

        compress_part(part1)
        compress_part(part2)

        assert part1.data == part2.data

    def test_decompress_garbage_raises_0303(self):
        part = new_part(b'this is not gzip')
        part.compressed = True

        with pytest.raises(AS4ProtocolException) as exc:
            decompress_part(part)

        assert exc.value.error_code == EbMSError.Decompression_Failure

# ################################################################################################################################
# ################################################################################################################################

class TestMultipart:

    def test_multipart_roundtrip(self):
        envelope = b'<Envelope>test</Envelope>'
        part = new_part(b'payload bytes', 'application/pdf')

        body, content_type = build_multipart(envelope, [part])

        assert content_type.startswith('multipart/related')
        assert 'boundary=' in content_type

        parsed_envelope, parsed_parts = parse_multipart(body, content_type)

        assert parsed_envelope == envelope
        assert len(parsed_parts) == 1
        assert parsed_parts[0].content_id == part.content_id
        assert parsed_parts[0].data == b'payload bytes'

    def test_binary_payload_survives(self):
        # Bytes that look like MIME structure must survive the trip.
        tricky = b'\r\n--fake-boundary\r\nContent-Type: evil\r\n\r\n\x00\x01\x02\xff'
        envelope = b'<Envelope/>'
        part = new_part(tricky, 'application/octet-stream')

        body, content_type = build_multipart(envelope, [part])
        _, parsed_parts = parse_multipart(body, content_type)

        assert parsed_parts[0].data == tricky

    def test_signal_without_parts_is_bare_soap(self):
        envelope = b'<Envelope>signal</Envelope>'

        body, content_type = build_multipart(envelope, [])

        assert body == envelope
        assert content_type.startswith('application/soap+xml')

        parsed_envelope, parsed_parts = parse_multipart(body, content_type)
        assert parsed_envelope == envelope
        assert parsed_parts == []

    def test_unexpected_content_type_raises_0007(self):
        with pytest.raises(AS4ProtocolException) as exc:
            _ = parse_multipart(b'{}', 'application/json')

        assert exc.value.error_code == EbMSError.Mime_Inconsistency

    def test_missing_boundary_raises_0007(self):
        with pytest.raises(AS4ProtocolException) as exc:
            _ = parse_multipart(b'body', 'multipart/related')

        assert exc.value.error_code == EbMSError.Mime_Inconsistency

# ################################################################################################################################
# ################################################################################################################################
