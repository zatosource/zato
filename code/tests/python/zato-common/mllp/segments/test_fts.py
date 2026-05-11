from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import FTS


file_batch_count = "test_file_batch_count"
file_trailer_comment = "test_file_trailer_comment"


class TestFTS:
    """Comprehensive tests for FTS segment."""

    def test_fts_build_and_verify(self):
        seg = FTS()

        seg.file_batch_count = file_batch_count
        seg.file_trailer_comment = file_trailer_comment

        assert seg.file_batch_count == file_batch_count
        assert seg.file_trailer_comment == file_trailer_comment

    def test_fts_to_dict(self):
        seg = FTS()

        seg.file_batch_count = file_batch_count
        seg.file_trailer_comment = file_trailer_comment

        result = seg.to_dict()

        assert result["_segment_id"] == "FTS"
        assert result["file_batch_count"] == file_batch_count
        assert result["file_trailer_comment"] == file_trailer_comment

    def test_fts_to_json(self):
        seg = FTS()

        seg.file_batch_count = file_batch_count
        seg.file_trailer_comment = file_trailer_comment

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "FTS"
        assert result["file_batch_count"] == file_batch_count
        assert result["file_trailer_comment"] == file_trailer_comment
