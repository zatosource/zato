from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import EQU


event_date_time = "test_event_date_time"
expected_datetime_of_the_next_status_change = "test_expected_datetime_of"


class TestEQU:
    """Comprehensive tests for EQU segment."""

    def test_equ_build_and_verify(self):
        seg = EQU()

        seg.event_date_time = event_date_time
        seg.expected_datetime_of_the_next_status_change = expected_datetime_of_the_next_status_change

        assert seg.event_date_time == event_date_time
        assert seg.expected_datetime_of_the_next_status_change == expected_datetime_of_the_next_status_change

    def test_equ_to_dict(self):
        seg = EQU()

        seg.event_date_time = event_date_time
        seg.expected_datetime_of_the_next_status_change = expected_datetime_of_the_next_status_change

        result = seg.to_dict()

        assert result["_segment_id"] == "EQU"
        assert result["event_date_time"] == event_date_time
        assert result["expected_datetime_of_the_next_status_change"] == expected_datetime_of_the_next_status_change

    def test_equ_to_json(self):
        seg = EQU()

        seg.event_date_time = event_date_time
        seg.expected_datetime_of_the_next_status_change = expected_datetime_of_the_next_status_change

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "EQU"
        assert result["event_date_time"] == event_date_time
        assert result["expected_datetime_of_the_next_status_change"] == expected_datetime_of_the_next_status_change
