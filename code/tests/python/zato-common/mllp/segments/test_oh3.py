from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import OH3


set_id = "test_set_id"
action_code = "test_action_code"
usual_occupation_duration_years = "test_usual_occupation_dur"
start_year = "test_start_year"
entered_date = "test_entered_date"


class TestOH3:
    """Comprehensive tests for OH3 segment."""

    def test_oh3_build_and_verify(self):
        seg = OH3()

        seg.set_id = set_id
        seg.action_code = action_code
        seg.usual_occupation_duration_years = usual_occupation_duration_years
        seg.start_year = start_year
        seg.entered_date = entered_date

        assert seg.set_id == set_id
        assert seg.action_code == action_code
        assert seg.usual_occupation_duration_years == usual_occupation_duration_years
        assert seg.start_year == start_year
        assert seg.entered_date == entered_date

    def test_oh3_to_dict(self):
        seg = OH3()

        seg.set_id = set_id
        seg.action_code = action_code
        seg.usual_occupation_duration_years = usual_occupation_duration_years
        seg.start_year = start_year
        seg.entered_date = entered_date

        result = seg.to_dict()

        assert result["_segment_id"] == "OH3"
        assert result["set_id"] == set_id
        assert result["action_code"] == action_code
        assert result["usual_occupation_duration_years"] == usual_occupation_duration_years
        assert result["start_year"] == start_year
        assert result["entered_date"] == entered_date

    def test_oh3_to_json(self):
        seg = OH3()

        seg.set_id = set_id
        seg.action_code = action_code
        seg.usual_occupation_duration_years = usual_occupation_duration_years
        seg.start_year = start_year
        seg.entered_date = entered_date

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "OH3"
        assert result["set_id"] == set_id
        assert result["action_code"] == action_code
        assert result["usual_occupation_duration_years"] == usual_occupation_duration_years
        assert result["start_year"] == start_year
        assert result["entered_date"] == entered_date
