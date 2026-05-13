from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import TQ2


set_id_tq2 = "test_set_id_tq2"
sequence_results_flag = "test_sequence_results_fla"
sequence_condition_code = "test_sequence_condition_c"
cyclic_entry_exit_indicator = "test_cyclic_entry_exit_in"
cyclic_group_maximum_number_of_repeats = "test_cyclic_group_maximum"
special_service_request_relationship = "test_special_service_requ"


class TestTQ2:
    """Comprehensive tests for TQ2 segment."""

    def test_tq2_build_and_verify(self):
        seg = TQ2()

        seg.set_id_tq2 = set_id_tq2
        seg.sequence_results_flag = sequence_results_flag
        seg.sequence_condition_code = sequence_condition_code
        seg.cyclic_entry_exit_indicator = cyclic_entry_exit_indicator
        seg.cyclic_group_maximum_number_of_repeats = cyclic_group_maximum_number_of_repeats
        seg.special_service_request_relationship = special_service_request_relationship

        assert seg.set_id_tq2 == set_id_tq2
        assert seg.sequence_results_flag == sequence_results_flag
        assert seg.sequence_condition_code == sequence_condition_code
        assert seg.cyclic_entry_exit_indicator == cyclic_entry_exit_indicator
        assert seg.cyclic_group_maximum_number_of_repeats == cyclic_group_maximum_number_of_repeats
        assert seg.special_service_request_relationship == special_service_request_relationship

    def test_tq2_to_dict(self):
        seg = TQ2()

        seg.set_id_tq2 = set_id_tq2
        seg.sequence_results_flag = sequence_results_flag
        seg.sequence_condition_code = sequence_condition_code
        seg.cyclic_entry_exit_indicator = cyclic_entry_exit_indicator
        seg.cyclic_group_maximum_number_of_repeats = cyclic_group_maximum_number_of_repeats
        seg.special_service_request_relationship = special_service_request_relationship

        result = seg.to_dict()

        assert result["_segment_id"] == "TQ2"
        assert result["set_id_tq2"] == set_id_tq2
        assert result["sequence_results_flag"] == sequence_results_flag
        assert result["sequence_condition_code"] == sequence_condition_code
        assert result["cyclic_entry_exit_indicator"] == cyclic_entry_exit_indicator
        assert result["cyclic_group_maximum_number_of_repeats"] == cyclic_group_maximum_number_of_repeats
        assert result["special_service_request_relationship"] == special_service_request_relationship

    def test_tq2_to_json(self):
        seg = TQ2()

        seg.set_id_tq2 = set_id_tq2
        seg.sequence_results_flag = sequence_results_flag
        seg.sequence_condition_code = sequence_condition_code
        seg.cyclic_entry_exit_indicator = cyclic_entry_exit_indicator
        seg.cyclic_group_maximum_number_of_repeats = cyclic_group_maximum_number_of_repeats
        seg.special_service_request_relationship = special_service_request_relationship

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "TQ2"
        assert result["set_id_tq2"] == set_id_tq2
        assert result["sequence_results_flag"] == sequence_results_flag
        assert result["sequence_condition_code"] == sequence_condition_code
        assert result["cyclic_entry_exit_indicator"] == cyclic_entry_exit_indicator
        assert result["cyclic_group_maximum_number_of_repeats"] == cyclic_group_maximum_number_of_repeats
        assert result["special_service_request_relationship"] == special_service_request_relationship
