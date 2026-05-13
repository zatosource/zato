from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import ECD


reference_command_number = "test_reference_command_nu"
response_required = "test_response_required"


class TestECD:
    """Comprehensive tests for ECD segment."""

    def test_ecd_build_and_verify(self):
        seg = ECD()

        seg.reference_command_number = reference_command_number
        seg.response_required = response_required

        assert seg.reference_command_number == reference_command_number
        assert seg.response_required == response_required

    def test_ecd_to_dict(self):
        seg = ECD()

        seg.reference_command_number = reference_command_number
        seg.response_required = response_required

        result = seg.to_dict()

        assert result["_segment_id"] == "ECD"
        assert result["reference_command_number"] == reference_command_number
        assert result["response_required"] == response_required

    def test_ecd_to_json(self):
        seg = ECD()

        seg.reference_command_number = reference_command_number
        seg.response_required = response_required

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "ECD"
        assert result["reference_command_number"] == reference_command_number
        assert result["response_required"] == response_required
