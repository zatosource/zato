from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import LRL


segment_action_code = "test_segment_action_code"


class TestLRL:
    """Comprehensive tests for LRL segment."""

    def test_lrl_build_and_verify(self):
        seg = LRL()

        seg.segment_action_code = segment_action_code

        assert seg.segment_action_code == segment_action_code

    def test_lrl_to_dict(self):
        seg = LRL()

        seg.segment_action_code = segment_action_code

        result = seg.to_dict()

        assert result["_segment_id"] == "LRL"
        assert result["segment_action_code"] == segment_action_code

    def test_lrl_to_json(self):
        seg = LRL()

        seg.segment_action_code = segment_action_code

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "LRL"
        assert result["segment_action_code"] == segment_action_code
