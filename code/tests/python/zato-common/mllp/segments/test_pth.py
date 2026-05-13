from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import PTH


action_code = "test_action_code"
pathway_established_date_time = "test_pathway_established_"
change_pathway_life_cycle_status_date_time = "test_change_pathway_life_"


class TestPTH:
    """Comprehensive tests for PTH segment."""

    def test_pth_build_and_verify(self):
        seg = PTH()

        seg.action_code = action_code
        seg.pathway_established_date_time = pathway_established_date_time
        seg.change_pathway_life_cycle_status_date_time = change_pathway_life_cycle_status_date_time

        assert seg.action_code == action_code
        assert seg.pathway_established_date_time == pathway_established_date_time
        assert seg.change_pathway_life_cycle_status_date_time == change_pathway_life_cycle_status_date_time

    def test_pth_to_dict(self):
        seg = PTH()

        seg.action_code = action_code
        seg.pathway_established_date_time = pathway_established_date_time
        seg.change_pathway_life_cycle_status_date_time = change_pathway_life_cycle_status_date_time

        result = seg.to_dict()

        assert result["_segment_id"] == "PTH"
        assert result["action_code"] == action_code
        assert result["pathway_established_date_time"] == pathway_established_date_time
        assert result["change_pathway_life_cycle_status_date_time"] == change_pathway_life_cycle_status_date_time

    def test_pth_to_json(self):
        seg = PTH()

        seg.action_code = action_code
        seg.pathway_established_date_time = pathway_established_date_time
        seg.change_pathway_life_cycle_status_date_time = change_pathway_life_cycle_status_date_time

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "PTH"
        assert result["action_code"] == action_code
        assert result["pathway_established_date_time"] == pathway_established_date_time
        assert result["change_pathway_life_cycle_status_date_time"] == change_pathway_life_cycle_status_date_time
