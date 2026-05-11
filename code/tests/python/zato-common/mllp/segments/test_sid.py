from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import SID


substance_lot_number = "test_substance_lot_number"
substance_container_identifier = "test_substance_container_"


class TestSID:
    """Comprehensive tests for SID segment."""

    def test_sid_build_and_verify(self):
        seg = SID()

        seg.substance_lot_number = substance_lot_number
        seg.substance_container_identifier = substance_container_identifier

        assert seg.substance_lot_number == substance_lot_number
        assert seg.substance_container_identifier == substance_container_identifier

    def test_sid_to_dict(self):
        seg = SID()

        seg.substance_lot_number = substance_lot_number
        seg.substance_container_identifier = substance_container_identifier

        result = seg.to_dict()

        assert result["_segment_id"] == "SID"
        assert result["substance_lot_number"] == substance_lot_number
        assert result["substance_container_identifier"] == substance_container_identifier

    def test_sid_to_json(self):
        seg = SID()

        seg.substance_lot_number = substance_lot_number
        seg.substance_container_identifier = substance_container_identifier

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "SID"
        assert result["substance_lot_number"] == substance_lot_number
        assert result["substance_container_identifier"] == substance_container_identifier
