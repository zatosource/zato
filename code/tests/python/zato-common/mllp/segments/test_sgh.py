from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import SGH


set_id_sgh = "test_set_id_sgh"
segment_group_name = "test_segment_group_name"


class TestSGH:
    """Comprehensive tests for SGH segment."""

    def test_sgh_build_and_verify(self):
        seg = SGH()

        seg.set_id_sgh = set_id_sgh
        seg.segment_group_name = segment_group_name

        assert seg.set_id_sgh == set_id_sgh
        assert seg.segment_group_name == segment_group_name

    def test_sgh_to_dict(self):
        seg = SGH()

        seg.set_id_sgh = set_id_sgh
        seg.segment_group_name = segment_group_name

        result = seg.to_dict()

        assert result["_segment_id"] == "SGH"
        assert result["set_id_sgh"] == set_id_sgh
        assert result["segment_group_name"] == segment_group_name

    def test_sgh_to_json(self):
        seg = SGH()

        seg.set_id_sgh = set_id_sgh
        seg.segment_group_name = segment_group_name

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "SGH"
        assert result["set_id_sgh"] == set_id_sgh
        assert result["segment_group_name"] == segment_group_name
