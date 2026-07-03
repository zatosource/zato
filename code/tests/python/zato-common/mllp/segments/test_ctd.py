from __future__ import annotations

import json

from zato.hl7v2.v2_9.segments import CTD


class TestCTD:
    """Comprehensive tests for CTD segment."""

    def test_ctd_to_dict(self):
        seg = CTD()

        result = seg.to_dict()

        assert result["_segment_id"] == "CTD"

    def test_ctd_to_json(self):
        seg = CTD()

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "CTD"
