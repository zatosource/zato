from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import PRB


action_code = "test_action_code"
action_date_time = "test_action_date_time"
problem_list_priority = "test_problem_list_priorit"
problem_established_date_time = "test_problem_established_"
anticipated_problem_resolution_date_time = "test_anticipated_problem_"
actual_problem_resolution_date_time = "test_actual_problem_resol"
problem_life_cycle_status_date_time = "test_problem_life_cycle_s"
problem_date_of_onset = "test_problem_date_of_onse"
problem_onset_text = "test_problem_onset_text"
probability_of_problem_0_1 = "test_probability_of_probl"
family_significant_other_awareness_of_problem_prognosis = "test_family_significant_o"


class TestPRB:
    """Comprehensive tests for PRB segment."""

    def test_prb_build_and_verify(self):
        seg = PRB()

        seg.action_code = action_code
        seg.action_date_time = action_date_time
        seg.problem_list_priority = problem_list_priority
        seg.problem_established_date_time = problem_established_date_time
        seg.anticipated_problem_resolution_date_time = anticipated_problem_resolution_date_time
        seg.actual_problem_resolution_date_time = actual_problem_resolution_date_time
        seg.problem_life_cycle_status_date_time = problem_life_cycle_status_date_time
        seg.problem_date_of_onset = problem_date_of_onset
        seg.problem_onset_text = problem_onset_text
        seg.probability_of_problem_0_1 = probability_of_problem_0_1
        seg.family_significant_other_awareness_of_problem_prognosis = family_significant_other_awareness_of_problem_prognosis

        assert seg.action_code == action_code
        assert seg.action_date_time == action_date_time
        assert seg.problem_list_priority == problem_list_priority
        assert seg.problem_established_date_time == problem_established_date_time
        assert seg.anticipated_problem_resolution_date_time == anticipated_problem_resolution_date_time
        assert seg.actual_problem_resolution_date_time == actual_problem_resolution_date_time
        assert seg.problem_life_cycle_status_date_time == problem_life_cycle_status_date_time
        assert seg.problem_date_of_onset == problem_date_of_onset
        assert seg.problem_onset_text == problem_onset_text
        assert seg.probability_of_problem_0_1 == probability_of_problem_0_1
        assert seg.family_significant_other_awareness_of_problem_prognosis == family_significant_other_awareness_of_problem_prognosis

    def test_prb_to_dict(self):
        seg = PRB()

        seg.action_code = action_code
        seg.action_date_time = action_date_time
        seg.problem_list_priority = problem_list_priority
        seg.problem_established_date_time = problem_established_date_time
        seg.anticipated_problem_resolution_date_time = anticipated_problem_resolution_date_time
        seg.actual_problem_resolution_date_time = actual_problem_resolution_date_time
        seg.problem_life_cycle_status_date_time = problem_life_cycle_status_date_time
        seg.problem_date_of_onset = problem_date_of_onset
        seg.problem_onset_text = problem_onset_text
        seg.probability_of_problem_0_1 = probability_of_problem_0_1
        seg.family_significant_other_awareness_of_problem_prognosis = family_significant_other_awareness_of_problem_prognosis

        result = seg.to_dict()

        assert result["_segment_id"] == "PRB"
        assert result["action_code"] == action_code
        assert result["action_date_time"] == action_date_time
        assert result["problem_list_priority"] == problem_list_priority
        assert result["problem_established_date_time"] == problem_established_date_time
        assert result["anticipated_problem_resolution_date_time"] == anticipated_problem_resolution_date_time
        assert result["actual_problem_resolution_date_time"] == actual_problem_resolution_date_time
        assert result["problem_life_cycle_status_date_time"] == problem_life_cycle_status_date_time
        assert result["problem_date_of_onset"] == problem_date_of_onset
        assert result["problem_onset_text"] == problem_onset_text
        assert result["probability_of_problem_0_1"] == probability_of_problem_0_1
        assert result["family_significant_other_awareness_of_problem_prognosis"] == family_significant_other_awareness_of_problem_prognosis

    def test_prb_to_json(self):
        seg = PRB()

        seg.action_code = action_code
        seg.action_date_time = action_date_time
        seg.problem_list_priority = problem_list_priority
        seg.problem_established_date_time = problem_established_date_time
        seg.anticipated_problem_resolution_date_time = anticipated_problem_resolution_date_time
        seg.actual_problem_resolution_date_time = actual_problem_resolution_date_time
        seg.problem_life_cycle_status_date_time = problem_life_cycle_status_date_time
        seg.problem_date_of_onset = problem_date_of_onset
        seg.problem_onset_text = problem_onset_text
        seg.probability_of_problem_0_1 = probability_of_problem_0_1
        seg.family_significant_other_awareness_of_problem_prognosis = family_significant_other_awareness_of_problem_prognosis

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "PRB"
        assert result["action_code"] == action_code
        assert result["action_date_time"] == action_date_time
        assert result["problem_list_priority"] == problem_list_priority
        assert result["problem_established_date_time"] == problem_established_date_time
        assert result["anticipated_problem_resolution_date_time"] == anticipated_problem_resolution_date_time
        assert result["actual_problem_resolution_date_time"] == actual_problem_resolution_date_time
        assert result["problem_life_cycle_status_date_time"] == problem_life_cycle_status_date_time
        assert result["problem_date_of_onset"] == problem_date_of_onset
        assert result["problem_onset_text"] == problem_onset_text
        assert result["probability_of_problem_0_1"] == probability_of_problem_0_1
        assert result["family_significant_other_awareness_of_problem_prognosis"] == family_significant_other_awareness_of_problem_prognosis
