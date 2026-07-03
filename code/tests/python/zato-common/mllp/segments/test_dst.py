from __future__ import annotations

import json

from zato.hl7v2.v2_9.segments import DST


class TestDST:
    """Comprehensive tests for DST segment."""

    def test_dst_to_dict(self):
        seg = DST()

        result = seg.to_dict()

        assert result["_segment_id"] == "DST"

    def test_dst_to_json(self):
        seg = DST()

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "DST"
