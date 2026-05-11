from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import QPD


query_tag = "test_query_tag"


class TestQPD:
    """Comprehensive tests for QPD segment."""

    def test_qpd_build_and_verify(self):
        seg = QPD()

        seg.query_tag = query_tag

        assert seg.query_tag == query_tag

    def test_qpd_to_dict(self):
        seg = QPD()

        seg.query_tag = query_tag

        result = seg.to_dict()

        assert result["_segment_id"] == "QPD"
        assert result["query_tag"] == query_tag

    def test_qpd_to_json(self):
        seg = QPD()

        seg.query_tag = query_tag

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "QPD"
        assert result["query_tag"] == query_tag
