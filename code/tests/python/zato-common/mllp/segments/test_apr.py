from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import APR


slot_spacing_criteria = "test_slot_spacing_criteri"


class TestAPR:
    """Comprehensive tests for APR segment."""

    def test_apr_build_and_verify(self):
        seg = APR()

        seg.slot_spacing_criteria = slot_spacing_criteria

        assert seg.slot_spacing_criteria == slot_spacing_criteria

    def test_apr_to_dict(self):
        seg = APR()

        seg.slot_spacing_criteria = slot_spacing_criteria

        result = seg.to_dict()

        assert result["_segment_id"] == "APR"
        assert result["slot_spacing_criteria"] == slot_spacing_criteria

    def test_apr_to_json(self):
        seg = APR()

        seg.slot_spacing_criteria = slot_spacing_criteria

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "APR"
        assert result["slot_spacing_criteria"] == slot_spacing_criteria
