from __future__ import annotations

import json

from zato.hl7v2.v2_9.segments import UAC


class TestUAC:
    """Comprehensive tests for UAC segment."""

    def test_uac_to_dict(self):
        seg = UAC()

        result = seg.to_dict()

        assert result["_segment_id"] == "UAC"

    def test_uac_to_json(self):
        seg = UAC()

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "UAC"
