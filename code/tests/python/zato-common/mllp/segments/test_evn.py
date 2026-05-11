from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import EVN


recorded_date_time = "test_recorded_date_time"
date_time_planned_event = "test_date_time_planned_ev"
event_occurred = "test_event_occurred"


class TestEVN:
    """Comprehensive tests for EVN segment."""

    def test_evn_build_and_verify(self):
        seg = EVN()

        seg.recorded_date_time = recorded_date_time
        seg.date_time_planned_event = date_time_planned_event
        seg.event_occurred = event_occurred

        assert seg.recorded_date_time == recorded_date_time
        assert seg.date_time_planned_event == date_time_planned_event
        assert seg.event_occurred == event_occurred

    def test_evn_to_dict(self):
        seg = EVN()

        seg.recorded_date_time = recorded_date_time
        seg.date_time_planned_event = date_time_planned_event
        seg.event_occurred = event_occurred

        result = seg.to_dict()

        assert result["_segment_id"] == "EVN"
        assert result["recorded_date_time"] == recorded_date_time
        assert result["date_time_planned_event"] == date_time_planned_event
        assert result["event_occurred"] == event_occurred

    def test_evn_to_json(self):
        seg = EVN()

        seg.recorded_date_time = recorded_date_time
        seg.date_time_planned_event = date_time_planned_event
        seg.event_occurred = event_occurred

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "EVN"
        assert result["recorded_date_time"] == recorded_date_time
        assert result["date_time_planned_event"] == date_time_planned_event
        assert result["event_occurred"] == event_occurred
