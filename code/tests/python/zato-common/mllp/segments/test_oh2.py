from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import OH2


set_id = "test_set_id"
action_code = "test_action_code"
entered_date = "test_entered_date"
job_start_date = "test_job_start_date"
job_end_date = "test_job_end_date"
average_hours_worked_per_day = "test_average_hours_worked"
average_days_worked_per_week = "test_average_days_worked_"


class TestOH2:
    """Comprehensive tests for OH2 segment."""

    def test_oh2_build_and_verify(self):
        seg = OH2()

        seg.set_id = set_id
        seg.action_code = action_code
        seg.entered_date = entered_date
        seg.job_start_date = job_start_date
        seg.job_end_date = job_end_date
        seg.average_hours_worked_per_day = average_hours_worked_per_day
        seg.average_days_worked_per_week = average_days_worked_per_week

        assert seg.set_id == set_id
        assert seg.action_code == action_code
        assert seg.entered_date == entered_date
        assert seg.job_start_date == job_start_date
        assert seg.job_end_date == job_end_date
        assert seg.average_hours_worked_per_day == average_hours_worked_per_day
        assert seg.average_days_worked_per_week == average_days_worked_per_week

    def test_oh2_to_dict(self):
        seg = OH2()

        seg.set_id = set_id
        seg.action_code = action_code
        seg.entered_date = entered_date
        seg.job_start_date = job_start_date
        seg.job_end_date = job_end_date
        seg.average_hours_worked_per_day = average_hours_worked_per_day
        seg.average_days_worked_per_week = average_days_worked_per_week

        result = seg.to_dict()

        assert result["_segment_id"] == "OH2"
        assert result["set_id"] == set_id
        assert result["action_code"] == action_code
        assert result["entered_date"] == entered_date
        assert result["job_start_date"] == job_start_date
        assert result["job_end_date"] == job_end_date
        assert result["average_hours_worked_per_day"] == average_hours_worked_per_day
        assert result["average_days_worked_per_week"] == average_days_worked_per_week

    def test_oh2_to_json(self):
        seg = OH2()

        seg.set_id = set_id
        seg.action_code = action_code
        seg.entered_date = entered_date
        seg.job_start_date = job_start_date
        seg.job_end_date = job_end_date
        seg.average_hours_worked_per_day = average_hours_worked_per_day
        seg.average_days_worked_per_week = average_days_worked_per_week

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "OH2"
        assert result["set_id"] == set_id
        assert result["action_code"] == action_code
        assert result["entered_date"] == entered_date
        assert result["job_start_date"] == job_start_date
        assert result["job_end_date"] == job_end_date
        assert result["average_hours_worked_per_day"] == average_hours_worked_per_day
        assert result["average_days_worked_per_week"] == average_days_worked_per_week
