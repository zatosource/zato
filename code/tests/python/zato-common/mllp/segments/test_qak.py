from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import QAK


query_tag = "test_query_tag"
query_response_status = "test_query_response_statu"
hit_count_total = "test_hit_count_total"
this_payload = "test_this_payload"
hits_remaining = "test_hits_remaining"


class TestQAK:
    """Comprehensive tests for QAK segment."""

    def test_qak_build_and_verify(self):
        seg = QAK()

        seg.query_tag = query_tag
        seg.query_response_status = query_response_status
        seg.hit_count_total = hit_count_total
        seg.this_payload = this_payload
        seg.hits_remaining = hits_remaining

        assert seg.query_tag == query_tag
        assert seg.query_response_status == query_response_status
        assert seg.hit_count_total == hit_count_total
        assert seg.this_payload == this_payload
        assert seg.hits_remaining == hits_remaining

    def test_qak_to_dict(self):
        seg = QAK()

        seg.query_tag = query_tag
        seg.query_response_status = query_response_status
        seg.hit_count_total = hit_count_total
        seg.this_payload = this_payload
        seg.hits_remaining = hits_remaining

        result = seg.to_dict()

        assert result["_segment_id"] == "QAK"
        assert result["query_tag"] == query_tag
        assert result["query_response_status"] == query_response_status
        assert result["hit_count_total"] == hit_count_total
        assert result["this_payload"] == this_payload
        assert result["hits_remaining"] == hits_remaining

    def test_qak_to_json(self):
        seg = QAK()

        seg.query_tag = query_tag
        seg.query_response_status = query_response_status
        seg.hit_count_total = hit_count_total
        seg.this_payload = this_payload
        seg.hits_remaining = hits_remaining

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "QAK"
        assert result["query_tag"] == query_tag
        assert result["query_response_status"] == query_response_status
        assert result["hit_count_total"] == hit_count_total
        assert result["this_payload"] == this_payload
        assert result["hits_remaining"] == hits_remaining
