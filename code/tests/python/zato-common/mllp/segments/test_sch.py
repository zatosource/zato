from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import SCH


occurrence_number = "test_occurrence_number"


class TestSCH:
    """Comprehensive tests for SCH segment."""

    def test_sch_build_and_verify(self):
        seg = SCH()

        seg.occurrence_number = occurrence_number

        assert seg.occurrence_number == occurrence_number

    def test_sch_to_dict(self):
        seg = SCH()

        seg.occurrence_number = occurrence_number

        result = seg.to_dict()

        assert result["_segment_id"] == "SCH"
        assert result["occurrence_number"] == occurrence_number

    def test_sch_to_json(self):
        seg = SCH()

        seg.occurrence_number = occurrence_number

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "SCH"
        assert result["occurrence_number"] == occurrence_number
