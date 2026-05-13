from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import OVR


override_comments = "test_override_comments"


class TestOVR:
    """Comprehensive tests for OVR segment."""

    def test_ovr_build_and_verify(self):
        seg = OVR()

        seg.override_comments = override_comments

        assert seg.override_comments == override_comments

    def test_ovr_to_dict(self):
        seg = OVR()

        seg.override_comments = override_comments

        result = seg.to_dict()

        assert result["_segment_id"] == "OVR"
        assert result["override_comments"] == override_comments

    def test_ovr_to_json(self):
        seg = OVR()

        seg.override_comments = override_comments

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "OVR"
        assert result["override_comments"] == override_comments
