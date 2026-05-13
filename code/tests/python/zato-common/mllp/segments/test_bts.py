from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import BTS


batch_message_count = "test_batch_message_count"
batch_comment = "test_batch_comment"


class TestBTS:
    """Comprehensive tests for BTS segment."""

    def test_bts_build_and_verify(self):
        seg = BTS()

        seg.batch_message_count = batch_message_count
        seg.batch_comment = batch_comment

        assert seg.batch_message_count == batch_message_count
        assert seg.batch_comment == batch_comment

    def test_bts_to_dict(self):
        seg = BTS()

        seg.batch_message_count = batch_message_count
        seg.batch_comment = batch_comment

        result = seg.to_dict()

        assert result["_segment_id"] == "BTS"
        assert result["batch_message_count"] == batch_message_count
        assert result["batch_comment"] == batch_comment

    def test_bts_to_json(self):
        seg = BTS()

        seg.batch_message_count = batch_message_count
        seg.batch_comment = batch_comment

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "BTS"
        assert result["batch_message_count"] == batch_message_count
        assert result["batch_comment"] == batch_comment
