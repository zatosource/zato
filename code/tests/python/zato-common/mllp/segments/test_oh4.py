from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import OH4


set_id = "test_set_id"
action_code = "test_action_code"
combat_zone_start_date = "test_combat_zone_start_da"
combat_zone_end_date = "test_combat_zone_end_date"
entered_date = "test_entered_date"


class TestOH4:
    """Comprehensive tests for OH4 segment."""

    def test_oh4_build_and_verify(self):
        seg = OH4()

        seg.set_id = set_id
        seg.action_code = action_code
        seg.combat_zone_start_date = combat_zone_start_date
        seg.combat_zone_end_date = combat_zone_end_date
        seg.entered_date = entered_date

        assert seg.set_id == set_id
        assert seg.action_code == action_code
        assert seg.combat_zone_start_date == combat_zone_start_date
        assert seg.combat_zone_end_date == combat_zone_end_date
        assert seg.entered_date == entered_date

    def test_oh4_to_dict(self):
        seg = OH4()

        seg.set_id = set_id
        seg.action_code = action_code
        seg.combat_zone_start_date = combat_zone_start_date
        seg.combat_zone_end_date = combat_zone_end_date
        seg.entered_date = entered_date

        result = seg.to_dict()

        assert result["_segment_id"] == "OH4"
        assert result["set_id"] == set_id
        assert result["action_code"] == action_code
        assert result["combat_zone_start_date"] == combat_zone_start_date
        assert result["combat_zone_end_date"] == combat_zone_end_date
        assert result["entered_date"] == entered_date

    def test_oh4_to_json(self):
        seg = OH4()

        seg.set_id = set_id
        seg.action_code = action_code
        seg.combat_zone_start_date = combat_zone_start_date
        seg.combat_zone_end_date = combat_zone_end_date
        seg.entered_date = entered_date

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "OH4"
        assert result["set_id"] == set_id
        assert result["action_code"] == action_code
        assert result["combat_zone_start_date"] == combat_zone_start_date
        assert result["combat_zone_end_date"] == combat_zone_end_date
        assert result["entered_date"] == entered_date
