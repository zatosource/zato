from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import CTI


action_code = "test_action_code"


class TestCTI:
    """Comprehensive tests for CTI segment."""

    def test_cti_build_and_verify(self):
        seg = CTI()

        seg.action_code = action_code

        assert seg.action_code == action_code

    def test_cti_to_dict(self):
        seg = CTI()

        seg.action_code = action_code

        result = seg.to_dict()

        assert result["_segment_id"] == "CTI"
        assert result["action_code"] == action_code

    def test_cti_to_json(self):
        seg = CTI()

        seg.action_code = action_code

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "CTI"
        assert result["action_code"] == action_code
