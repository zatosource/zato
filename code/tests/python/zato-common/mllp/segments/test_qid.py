from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import QID


query_tag = "test_query_tag"


class TestQID:
    """Comprehensive tests for QID segment."""

    def test_qid_build_and_verify(self):
        seg = QID()

        seg.query_tag = query_tag

        assert seg.query_tag == query_tag

    def test_qid_to_dict(self):
        seg = QID()

        seg.query_tag = query_tag

        result = seg.to_dict()

        assert result["_segment_id"] == "QID"
        assert result["query_tag"] == query_tag

    def test_qid_to_json(self):
        seg = QID()

        seg.query_tag = query_tag

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "QID"
        assert result["query_tag"] == query_tag
