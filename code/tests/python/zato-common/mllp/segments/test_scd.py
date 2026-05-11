from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import SCD


cycle_start_time = "test_cycle_start_time"
cycle_count = "test_cycle_count"
load_number = "test_load_number"
cycle_start_date_time = "test_cycle_start_date_tim"
cycle_complete_time = "test_cycle_complete_time"


class TestSCD:
    """Comprehensive tests for SCD segment."""

    def test_scd_build_and_verify(self):
        seg = SCD()

        seg.cycle_start_time = cycle_start_time
        seg.cycle_count = cycle_count
        seg.load_number = load_number
        seg.cycle_start_date_time = cycle_start_date_time
        seg.cycle_complete_time = cycle_complete_time

        assert seg.cycle_start_time == cycle_start_time
        assert seg.cycle_count == cycle_count
        assert seg.load_number == load_number
        assert seg.cycle_start_date_time == cycle_start_date_time
        assert seg.cycle_complete_time == cycle_complete_time

    def test_scd_to_dict(self):
        seg = SCD()

        seg.cycle_start_time = cycle_start_time
        seg.cycle_count = cycle_count
        seg.load_number = load_number
        seg.cycle_start_date_time = cycle_start_date_time
        seg.cycle_complete_time = cycle_complete_time

        result = seg.to_dict()

        assert result["_segment_id"] == "SCD"
        assert result["cycle_start_time"] == cycle_start_time
        assert result["cycle_count"] == cycle_count
        assert result["load_number"] == load_number
        assert result["cycle_start_date_time"] == cycle_start_date_time
        assert result["cycle_complete_time"] == cycle_complete_time

    def test_scd_to_json(self):
        seg = SCD()

        seg.cycle_start_time = cycle_start_time
        seg.cycle_count = cycle_count
        seg.load_number = load_number
        seg.cycle_start_date_time = cycle_start_date_time
        seg.cycle_complete_time = cycle_complete_time

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "SCD"
        assert result["cycle_start_time"] == cycle_start_time
        assert result["cycle_count"] == cycle_count
        assert result["load_number"] == load_number
        assert result["cycle_start_date_time"] == cycle_start_date_time
        assert result["cycle_complete_time"] == cycle_complete_time
