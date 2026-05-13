from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import ARQ


occurrence_number = "test_occurrence_number"
appointment_duration = "test_appointment_duration"
priority_arq = "test_priority_arq"
repeating_interval_duration = "test_repeating_interval_d"


class TestARQ:
    """Comprehensive tests for ARQ segment."""

    def test_arq_build_and_verify(self):
        seg = ARQ()

        seg.occurrence_number = occurrence_number
        seg.appointment_duration = appointment_duration
        seg.priority_arq = priority_arq
        seg.repeating_interval_duration = repeating_interval_duration

        assert seg.occurrence_number == occurrence_number
        assert seg.appointment_duration == appointment_duration
        assert seg.priority_arq == priority_arq
        assert seg.repeating_interval_duration == repeating_interval_duration

    def test_arq_to_dict(self):
        seg = ARQ()

        seg.occurrence_number = occurrence_number
        seg.appointment_duration = appointment_duration
        seg.priority_arq = priority_arq
        seg.repeating_interval_duration = repeating_interval_duration

        result = seg.to_dict()

        assert result["_segment_id"] == "ARQ"
        assert result["occurrence_number"] == occurrence_number
        assert result["appointment_duration"] == appointment_duration
        assert result["priority_arq"] == priority_arq
        assert result["repeating_interval_duration"] == repeating_interval_duration

    def test_arq_to_json(self):
        seg = ARQ()

        seg.occurrence_number = occurrence_number
        seg.appointment_duration = appointment_duration
        seg.priority_arq = priority_arq
        seg.repeating_interval_duration = repeating_interval_duration

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "ARQ"
        assert result["occurrence_number"] == occurrence_number
        assert result["appointment_duration"] == appointment_duration
        assert result["priority_arq"] == priority_arq
        assert result["repeating_interval_duration"] == repeating_interval_duration
