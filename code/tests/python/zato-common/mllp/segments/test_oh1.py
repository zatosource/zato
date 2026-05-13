from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import OH1


set_id = "test_set_id"
action_code = "test_action_code"
employment_status_start_date = "test_employment_status_st"
employment_status_end_date = "test_employment_status_en"
entered_date = "test_entered_date"


class TestOH1:
    """Comprehensive tests for OH1 segment."""

    def test_oh1_build_and_verify(self):
        seg = OH1()

        seg.set_id = set_id
        seg.action_code = action_code
        seg.employment_status_start_date = employment_status_start_date
        seg.employment_status_end_date = employment_status_end_date
        seg.entered_date = entered_date

        assert seg.set_id == set_id
        assert seg.action_code == action_code
        assert seg.employment_status_start_date == employment_status_start_date
        assert seg.employment_status_end_date == employment_status_end_date
        assert seg.entered_date == entered_date

    def test_oh1_to_dict(self):
        seg = OH1()

        seg.set_id = set_id
        seg.action_code = action_code
        seg.employment_status_start_date = employment_status_start_date
        seg.employment_status_end_date = employment_status_end_date
        seg.entered_date = entered_date

        result = seg.to_dict()

        assert result["_segment_id"] == "OH1"
        assert result["set_id"] == set_id
        assert result["action_code"] == action_code
        assert result["employment_status_start_date"] == employment_status_start_date
        assert result["employment_status_end_date"] == employment_status_end_date
        assert result["entered_date"] == entered_date

    def test_oh1_to_json(self):
        seg = OH1()

        seg.set_id = set_id
        seg.action_code = action_code
        seg.employment_status_start_date = employment_status_start_date
        seg.employment_status_end_date = employment_status_end_date
        seg.entered_date = entered_date

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "OH1"
        assert result["set_id"] == set_id
        assert result["action_code"] == action_code
        assert result["employment_status_start_date"] == employment_status_start_date
        assert result["employment_status_end_date"] == employment_status_end_date
        assert result["entered_date"] == entered_date
