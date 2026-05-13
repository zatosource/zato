from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import OMC


sequence_number_test_observation_master_file = "test_sequence_number_test"
segment_action_code = "test_segment_action_code"
answer_required = "test_answer_required"
hint_help_text = "test_hint_help_text"
type_of_answer = "test_type_of_answer"
multiple_answers_allowed = "test_multiple_answers_all"
character_limit = "test_character_limit"
number_of_decimals = "test_number_of_decimals"


class TestOMC:
    """Comprehensive tests for OMC segment."""

    def test_omc_build_and_verify(self):
        seg = OMC()

        seg.sequence_number_test_observation_master_file = sequence_number_test_observation_master_file
        seg.segment_action_code = segment_action_code
        seg.answer_required = answer_required
        seg.hint_help_text = hint_help_text
        seg.type_of_answer = type_of_answer
        seg.multiple_answers_allowed = multiple_answers_allowed
        seg.character_limit = character_limit
        seg.number_of_decimals = number_of_decimals

        assert seg.sequence_number_test_observation_master_file == sequence_number_test_observation_master_file
        assert seg.segment_action_code == segment_action_code
        assert seg.answer_required == answer_required
        assert seg.hint_help_text == hint_help_text
        assert seg.type_of_answer == type_of_answer
        assert seg.multiple_answers_allowed == multiple_answers_allowed
        assert seg.character_limit == character_limit
        assert seg.number_of_decimals == number_of_decimals

    def test_omc_to_dict(self):
        seg = OMC()

        seg.sequence_number_test_observation_master_file = sequence_number_test_observation_master_file
        seg.segment_action_code = segment_action_code
        seg.answer_required = answer_required
        seg.hint_help_text = hint_help_text
        seg.type_of_answer = type_of_answer
        seg.multiple_answers_allowed = multiple_answers_allowed
        seg.character_limit = character_limit
        seg.number_of_decimals = number_of_decimals

        result = seg.to_dict()

        assert result["_segment_id"] == "OMC"
        assert result["sequence_number_test_observation_master_file"] == sequence_number_test_observation_master_file
        assert result["segment_action_code"] == segment_action_code
        assert result["answer_required"] == answer_required
        assert result["hint_help_text"] == hint_help_text
        assert result["type_of_answer"] == type_of_answer
        assert result["multiple_answers_allowed"] == multiple_answers_allowed
        assert result["character_limit"] == character_limit
        assert result["number_of_decimals"] == number_of_decimals

    def test_omc_to_json(self):
        seg = OMC()

        seg.sequence_number_test_observation_master_file = sequence_number_test_observation_master_file
        seg.segment_action_code = segment_action_code
        seg.answer_required = answer_required
        seg.hint_help_text = hint_help_text
        seg.type_of_answer = type_of_answer
        seg.multiple_answers_allowed = multiple_answers_allowed
        seg.character_limit = character_limit
        seg.number_of_decimals = number_of_decimals

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "OMC"
        assert result["sequence_number_test_observation_master_file"] == sequence_number_test_observation_master_file
        assert result["segment_action_code"] == segment_action_code
        assert result["answer_required"] == answer_required
        assert result["hint_help_text"] == hint_help_text
        assert result["type_of_answer"] == type_of_answer
        assert result["multiple_answers_allowed"] == multiple_answers_allowed
        assert result["character_limit"] == character_limit
        assert result["number_of_decimals"] == number_of_decimals
