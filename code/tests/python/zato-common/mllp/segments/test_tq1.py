from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import TQ1


set_id_tq1 = "test_set_id_tq1"
start_datetime = "test_start_datetime"
end_datetime = "test_end_datetime"
condition_text = "test_condition_text"
text_instruction = "test_text_instruction"
conjunction = "test_conjunction"
total_occurrences = "test_total_occurrences"


class TestTQ1:
    """Comprehensive tests for TQ1 segment."""

    def test_tq1_build_and_verify(self):
        seg = TQ1()

        seg.set_id_tq1 = set_id_tq1
        seg.start_datetime = start_datetime
        seg.end_datetime = end_datetime
        seg.condition_text = condition_text
        seg.text_instruction = text_instruction
        seg.conjunction = conjunction
        seg.total_occurrences = total_occurrences

        assert seg.set_id_tq1 == set_id_tq1
        assert seg.start_datetime == start_datetime
        assert seg.end_datetime == end_datetime
        assert seg.condition_text == condition_text
        assert seg.text_instruction == text_instruction
        assert seg.conjunction == conjunction
        assert seg.total_occurrences == total_occurrences

    def test_tq1_to_dict(self):
        seg = TQ1()

        seg.set_id_tq1 = set_id_tq1
        seg.start_datetime = start_datetime
        seg.end_datetime = end_datetime
        seg.condition_text = condition_text
        seg.text_instruction = text_instruction
        seg.conjunction = conjunction
        seg.total_occurrences = total_occurrences

        result = seg.to_dict()

        assert result["_segment_id"] == "TQ1"
        assert result["set_id_tq1"] == set_id_tq1
        assert result["start_datetime"] == start_datetime
        assert result["end_datetime"] == end_datetime
        assert result["condition_text"] == condition_text
        assert result["text_instruction"] == text_instruction
        assert result["conjunction"] == conjunction
        assert result["total_occurrences"] == total_occurrences

    def test_tq1_to_json(self):
        seg = TQ1()

        seg.set_id_tq1 = set_id_tq1
        seg.start_datetime = start_datetime
        seg.end_datetime = end_datetime
        seg.condition_text = condition_text
        seg.text_instruction = text_instruction
        seg.conjunction = conjunction
        seg.total_occurrences = total_occurrences

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "TQ1"
        assert result["set_id_tq1"] == set_id_tq1
        assert result["start_datetime"] == start_datetime
        assert result["end_datetime"] == end_datetime
        assert result["condition_text"] == condition_text
        assert result["text_instruction"] == text_instruction
        assert result["conjunction"] == conjunction
        assert result["total_occurrences"] == total_occurrences
