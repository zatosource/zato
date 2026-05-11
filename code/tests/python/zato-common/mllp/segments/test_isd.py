from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import ISD


reference_interaction_number = "test_reference_interactio"


class TestISD:
    """Comprehensive tests for ISD segment."""

    def test_isd_build_and_verify(self):
        seg = ISD()

        seg.reference_interaction_number = reference_interaction_number

        assert seg.reference_interaction_number == reference_interaction_number

    def test_isd_to_dict(self):
        seg = ISD()

        seg.reference_interaction_number = reference_interaction_number

        result = seg.to_dict()

        assert result["_segment_id"] == "ISD"
        assert result["reference_interaction_number"] == reference_interaction_number

    def test_isd_to_json(self):
        seg = ISD()

        seg.reference_interaction_number = reference_interaction_number

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "ISD"
        assert result["reference_interaction_number"] == reference_interaction_number
