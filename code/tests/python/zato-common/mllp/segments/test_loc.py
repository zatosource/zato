from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import LOC


location_description = "test_location_description"


class TestLOC:
    """Comprehensive tests for LOC segment."""

    def test_loc_build_and_verify(self):
        seg = LOC()

        seg.location_description = location_description

        assert seg.location_description == location_description

    def test_loc_to_dict(self):
        seg = LOC()

        seg.location_description = location_description

        result = seg.to_dict()

        assert result["_segment_id"] == "LOC"
        assert result["location_description"] == location_description

    def test_loc_to_json(self):
        seg = LOC()

        seg.location_description = location_description

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "LOC"
        assert result["location_description"] == location_description
