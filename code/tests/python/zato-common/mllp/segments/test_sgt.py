from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import SGT


set_id_sgt = "test_set_id_sgt"
segment_group_name = "test_segment_group_name"


class TestSGT:
    """Comprehensive tests for SGT segment."""

    def test_sgt_build_and_verify(self):
        seg = SGT()

        seg.set_id_sgt = set_id_sgt
        seg.segment_group_name = segment_group_name

        assert seg.set_id_sgt == set_id_sgt
        assert seg.segment_group_name == segment_group_name

    def test_sgt_to_dict(self):
        seg = SGT()

        seg.set_id_sgt = set_id_sgt
        seg.segment_group_name = segment_group_name

        result = seg.to_dict()

        assert result["_segment_id"] == "SGT"
        assert result["set_id_sgt"] == set_id_sgt
        assert result["segment_group_name"] == segment_group_name

    def test_sgt_to_json(self):
        seg = SGT()

        seg.set_id_sgt = set_id_sgt
        seg.segment_group_name = segment_group_name

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "SGT"
        assert result["set_id_sgt"] == set_id_sgt
        assert result["segment_group_name"] == segment_group_name
