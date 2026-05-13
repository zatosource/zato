from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import ADJ


adjustment_sequence_number = "test_adjustment_sequence_"
adjustment_description = "test_adjustment_descripti"
original_value = "test_original_value"
substitute_value = "test_substitute_value"
adjustment_date = "test_adjustment_date"


class TestADJ:
    """Comprehensive tests for ADJ segment."""

    def test_adj_build_and_verify(self):
        seg = ADJ()

        seg.adjustment_sequence_number = adjustment_sequence_number
        seg.adjustment_description = adjustment_description
        seg.original_value = original_value
        seg.substitute_value = substitute_value
        seg.adjustment_date = adjustment_date

        assert seg.adjustment_sequence_number == adjustment_sequence_number
        assert seg.adjustment_description == adjustment_description
        assert seg.original_value == original_value
        assert seg.substitute_value == substitute_value
        assert seg.adjustment_date == adjustment_date

    def test_adj_to_dict(self):
        seg = ADJ()

        seg.adjustment_sequence_number = adjustment_sequence_number
        seg.adjustment_description = adjustment_description
        seg.original_value = original_value
        seg.substitute_value = substitute_value
        seg.adjustment_date = adjustment_date

        result = seg.to_dict()

        assert result["_segment_id"] == "ADJ"
        assert result["adjustment_sequence_number"] == adjustment_sequence_number
        assert result["adjustment_description"] == adjustment_description
        assert result["original_value"] == original_value
        assert result["substitute_value"] == substitute_value
        assert result["adjustment_date"] == adjustment_date

    def test_adj_to_json(self):
        seg = ADJ()

        seg.adjustment_sequence_number = adjustment_sequence_number
        seg.adjustment_description = adjustment_description
        seg.original_value = original_value
        seg.substitute_value = substitute_value
        seg.adjustment_date = adjustment_date

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "ADJ"
        assert result["adjustment_sequence_number"] == adjustment_sequence_number
        assert result["adjustment_description"] == adjustment_description
        assert result["original_value"] == original_value
        assert result["substitute_value"] == substitute_value
        assert result["adjustment_date"] == adjustment_date
