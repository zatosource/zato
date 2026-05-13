from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import AIL


set_id_ail = "test_set_id_ail"
segment_action_code = "test_segment_action_code"
start_date_time = "test_start_date_time"
start_date_time_offset = "test_start_date_time_offs"
duration = "test_duration"


class TestAIL:
    """Comprehensive tests for AIL segment."""

    def test_ail_build_and_verify(self):
        seg = AIL()

        seg.set_id_ail = set_id_ail
        seg.segment_action_code = segment_action_code
        seg.start_date_time = start_date_time
        seg.start_date_time_offset = start_date_time_offset
        seg.duration = duration

        assert seg.set_id_ail == set_id_ail
        assert seg.segment_action_code == segment_action_code
        assert seg.start_date_time == start_date_time
        assert seg.start_date_time_offset == start_date_time_offset
        assert seg.duration == duration

    def test_ail_to_dict(self):
        seg = AIL()

        seg.set_id_ail = set_id_ail
        seg.segment_action_code = segment_action_code
        seg.start_date_time = start_date_time
        seg.start_date_time_offset = start_date_time_offset
        seg.duration = duration

        result = seg.to_dict()

        assert result["_segment_id"] == "AIL"
        assert result["set_id_ail"] == set_id_ail
        assert result["segment_action_code"] == segment_action_code
        assert result["start_date_time"] == start_date_time
        assert result["start_date_time_offset"] == start_date_time_offset
        assert result["duration"] == duration

    def test_ail_to_json(self):
        seg = AIL()

        seg.set_id_ail = set_id_ail
        seg.segment_action_code = segment_action_code
        seg.start_date_time = start_date_time
        seg.start_date_time_offset = start_date_time_offset
        seg.duration = duration

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "AIL"
        assert result["set_id_ail"] == set_id_ail
        assert result["segment_action_code"] == segment_action_code
        assert result["start_date_time"] == start_date_time
        assert result["start_date_time_offset"] == start_date_time_offset
        assert result["duration"] == duration
