from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import LCH


segment_action_code = "test_segment_action_code"


class TestLCH:
    """Comprehensive tests for LCH segment."""

    def test_lch_build_and_verify(self):
        seg = LCH()

        seg.segment_action_code = segment_action_code

        assert seg.segment_action_code == segment_action_code

    def test_lch_to_dict(self):
        seg = LCH()

        seg.segment_action_code = segment_action_code

        result = seg.to_dict()

        assert result["_segment_id"] == "LCH"
        assert result["segment_action_code"] == segment_action_code

    def test_lch_to_json(self):
        seg = LCH()

        seg.segment_action_code = segment_action_code

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "LCH"
        assert result["segment_action_code"] == segment_action_code
