from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import AIS


set_id_ais = "test_set_id_ais"
segment_action_code = "test_segment_action_code"
start_date_time = "test_start_date_time"
start_date_time_offset = "test_start_date_time_offs"
duration = "test_duration"


class TestAIS:
    """Comprehensive tests for AIS segment."""

    def test_ais_build_and_verify(self):
        seg = AIS()

        seg.set_id_ais = set_id_ais
        seg.segment_action_code = segment_action_code
        seg.start_date_time = start_date_time
        seg.start_date_time_offset = start_date_time_offset
        seg.duration = duration

        assert seg.set_id_ais == set_id_ais
        assert seg.segment_action_code == segment_action_code
        assert seg.start_date_time == start_date_time
        assert seg.start_date_time_offset == start_date_time_offset
        assert seg.duration == duration

    def test_ais_to_dict(self):
        seg = AIS()

        seg.set_id_ais = set_id_ais
        seg.segment_action_code = segment_action_code
        seg.start_date_time = start_date_time
        seg.start_date_time_offset = start_date_time_offset
        seg.duration = duration

        result = seg.to_dict()

        assert result["_segment_id"] == "AIS"
        assert result["set_id_ais"] == set_id_ais
        assert result["segment_action_code"] == segment_action_code
        assert result["start_date_time"] == start_date_time
        assert result["start_date_time_offset"] == start_date_time_offset
        assert result["duration"] == duration

    def test_ais_to_json(self):
        seg = AIS()

        seg.set_id_ais = set_id_ais
        seg.segment_action_code = segment_action_code
        seg.start_date_time = start_date_time
        seg.start_date_time_offset = start_date_time_offset
        seg.duration = duration

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "AIS"
        assert result["set_id_ais"] == set_id_ais
        assert result["segment_action_code"] == segment_action_code
        assert result["start_date_time"] == start_date_time
        assert result["start_date_time_offset"] == start_date_time_offset
        assert result["duration"] == duration
