from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import GOL


action_code = "test_action_code"
action_date_time = "test_action_date_time"
goal_list_priority = "test_goal_list_priority"
goal_established_date_time = "test_goal_established_dat"
expected_goal_achieve_date_time = "test_expected_goal_achiev"
current_goal_review_date_time = "test_current_goal_review_"
next_goal_review_date_time = "test_next_goal_review_dat"
previous_goal_review_date_time = "test_previous_goal_review"
goal_life_cycle_status_date_time = "test_goal_life_cycle_stat"


class TestGOL:
    """Comprehensive tests for GOL segment."""

    def test_gol_build_and_verify(self):
        seg = GOL()

        seg.action_code = action_code
        seg.action_date_time = action_date_time
        seg.goal_list_priority = goal_list_priority
        seg.goal_established_date_time = goal_established_date_time
        seg.expected_goal_achieve_date_time = expected_goal_achieve_date_time
        seg.current_goal_review_date_time = current_goal_review_date_time
        seg.next_goal_review_date_time = next_goal_review_date_time
        seg.previous_goal_review_date_time = previous_goal_review_date_time
        seg.goal_life_cycle_status_date_time = goal_life_cycle_status_date_time

        assert seg.action_code == action_code
        assert seg.action_date_time == action_date_time
        assert seg.goal_list_priority == goal_list_priority
        assert seg.goal_established_date_time == goal_established_date_time
        assert seg.expected_goal_achieve_date_time == expected_goal_achieve_date_time
        assert seg.current_goal_review_date_time == current_goal_review_date_time
        assert seg.next_goal_review_date_time == next_goal_review_date_time
        assert seg.previous_goal_review_date_time == previous_goal_review_date_time
        assert seg.goal_life_cycle_status_date_time == goal_life_cycle_status_date_time

    def test_gol_to_dict(self):
        seg = GOL()

        seg.action_code = action_code
        seg.action_date_time = action_date_time
        seg.goal_list_priority = goal_list_priority
        seg.goal_established_date_time = goal_established_date_time
        seg.expected_goal_achieve_date_time = expected_goal_achieve_date_time
        seg.current_goal_review_date_time = current_goal_review_date_time
        seg.next_goal_review_date_time = next_goal_review_date_time
        seg.previous_goal_review_date_time = previous_goal_review_date_time
        seg.goal_life_cycle_status_date_time = goal_life_cycle_status_date_time

        result = seg.to_dict()

        assert result["_segment_id"] == "GOL"
        assert result["action_code"] == action_code
        assert result["action_date_time"] == action_date_time
        assert result["goal_list_priority"] == goal_list_priority
        assert result["goal_established_date_time"] == goal_established_date_time
        assert result["expected_goal_achieve_date_time"] == expected_goal_achieve_date_time
        assert result["current_goal_review_date_time"] == current_goal_review_date_time
        assert result["next_goal_review_date_time"] == next_goal_review_date_time
        assert result["previous_goal_review_date_time"] == previous_goal_review_date_time
        assert result["goal_life_cycle_status_date_time"] == goal_life_cycle_status_date_time

    def test_gol_to_json(self):
        seg = GOL()

        seg.action_code = action_code
        seg.action_date_time = action_date_time
        seg.goal_list_priority = goal_list_priority
        seg.goal_established_date_time = goal_established_date_time
        seg.expected_goal_achieve_date_time = expected_goal_achieve_date_time
        seg.current_goal_review_date_time = current_goal_review_date_time
        seg.next_goal_review_date_time = next_goal_review_date_time
        seg.previous_goal_review_date_time = previous_goal_review_date_time
        seg.goal_life_cycle_status_date_time = goal_life_cycle_status_date_time

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "GOL"
        assert result["action_code"] == action_code
        assert result["action_date_time"] == action_date_time
        assert result["goal_list_priority"] == goal_list_priority
        assert result["goal_established_date_time"] == goal_established_date_time
        assert result["expected_goal_achieve_date_time"] == expected_goal_achieve_date_time
        assert result["current_goal_review_date_time"] == current_goal_review_date_time
        assert result["next_goal_review_date_time"] == next_goal_review_date_time
        assert result["previous_goal_review_date_time"] == previous_goal_review_date_time
        assert result["goal_life_cycle_status_date_time"] == goal_life_cycle_status_date_time
