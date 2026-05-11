from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import RGS


set_id_rgs = "test_set_id_rgs"
segment_action_code = "test_segment_action_code"


class TestRGS:
    """Comprehensive tests for RGS segment."""

    def test_rgs_build_and_verify(self):
        seg = RGS()

        seg.set_id_rgs = set_id_rgs
        seg.segment_action_code = segment_action_code

        assert seg.set_id_rgs == set_id_rgs
        assert seg.segment_action_code == segment_action_code

    def test_rgs_to_dict(self):
        seg = RGS()

        seg.set_id_rgs = set_id_rgs
        seg.segment_action_code = segment_action_code

        result = seg.to_dict()

        assert result["_segment_id"] == "RGS"
        assert result["set_id_rgs"] == set_id_rgs
        assert result["segment_action_code"] == segment_action_code

    def test_rgs_to_json(self):
        seg = RGS()

        seg.set_id_rgs = set_id_rgs
        seg.segment_action_code = segment_action_code

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "RGS"
        assert result["set_id_rgs"] == set_id_rgs
        assert result["segment_action_code"] == segment_action_code
