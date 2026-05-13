from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import AIG


set_id_aig = "test_set_id_aig"
segment_action_code = "test_segment_action_code"
resource_quantity = "test_resource_quantity"
start_date_time = "test_start_date_time"
start_date_time_offset = "test_start_date_time_offs"
duration = "test_duration"


class TestAIG:
    """Comprehensive tests for AIG segment."""

    def test_aig_build_and_verify(self):
        seg = AIG()

        seg.set_id_aig = set_id_aig
        seg.segment_action_code = segment_action_code
        seg.resource_quantity = resource_quantity
        seg.start_date_time = start_date_time
        seg.start_date_time_offset = start_date_time_offset
        seg.duration = duration

        assert seg.set_id_aig == set_id_aig
        assert seg.segment_action_code == segment_action_code
        assert seg.resource_quantity == resource_quantity
        assert seg.start_date_time == start_date_time
        assert seg.start_date_time_offset == start_date_time_offset
        assert seg.duration == duration

    def test_aig_to_dict(self):
        seg = AIG()

        seg.set_id_aig = set_id_aig
        seg.segment_action_code = segment_action_code
        seg.resource_quantity = resource_quantity
        seg.start_date_time = start_date_time
        seg.start_date_time_offset = start_date_time_offset
        seg.duration = duration

        result = seg.to_dict()

        assert result["_segment_id"] == "AIG"
        assert result["set_id_aig"] == set_id_aig
        assert result["segment_action_code"] == segment_action_code
        assert result["resource_quantity"] == resource_quantity
        assert result["start_date_time"] == start_date_time
        assert result["start_date_time_offset"] == start_date_time_offset
        assert result["duration"] == duration

    def test_aig_to_json(self):
        seg = AIG()

        seg.set_id_aig = set_id_aig
        seg.segment_action_code = segment_action_code
        seg.resource_quantity = resource_quantity
        seg.start_date_time = start_date_time
        seg.start_date_time_offset = start_date_time_offset
        seg.duration = duration

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "AIG"
        assert result["set_id_aig"] == set_id_aig
        assert result["segment_action_code"] == segment_action_code
        assert result["resource_quantity"] == resource_quantity
        assert result["start_date_time"] == start_date_time
        assert result["start_date_time_offset"] == start_date_time_offset
        assert result["duration"] == duration
