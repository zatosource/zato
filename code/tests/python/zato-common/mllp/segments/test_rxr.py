from __future__ import annotations

import json

from zato.hl7v2.v2_9.segments import RXR


class TestRXR:
    """Comprehensive tests for RXR segment."""

    def test_rxr_to_dict(self):
        seg = RXR()

        result = seg.to_dict()

        assert result["_segment_id"] == "RXR"

    def test_rxr_to_json(self):
        seg = RXR()

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "RXR"
