from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import OBX


set_id_obx = "test_set_id_obx"
value_type = "test_value_type"
reference_range = "test_reference_range"
probability = "test_probability"
observation_result_status = "test_observation_result_s"
effective_date_of_reference_range = "test_effective_date_of_re"
user_defined_access_checks = "test_user_defined_access_"
date_time_of_the_observation = "test_date_time_of_the_obs"
date_time_of_the_analysis = "test_date_time_of_the_ana"
patient_results_release_category = "test_patient_results_rele"
observation_type = "test_observation_type"
observation_sub_type = "test_observation_sub_type"
action_code = "test_action_code"


class TestOBX:
    """Comprehensive tests for OBX segment."""

    def test_obx_build_and_verify(self):
        seg = OBX()

        seg.set_id_obx = set_id_obx
        seg.value_type = value_type
        seg.reference_range = reference_range
        seg.probability = probability
        seg.observation_result_status = observation_result_status
        seg.effective_date_of_reference_range = effective_date_of_reference_range
        seg.user_defined_access_checks = user_defined_access_checks
        seg.date_time_of_the_observation = date_time_of_the_observation
        seg.date_time_of_the_analysis = date_time_of_the_analysis
        seg.patient_results_release_category = patient_results_release_category
        seg.observation_type = observation_type
        seg.observation_sub_type = observation_sub_type
        seg.action_code = action_code

        assert seg.set_id_obx == set_id_obx
        assert seg.value_type == value_type
        assert seg.reference_range == reference_range
        assert seg.probability == probability
        assert seg.observation_result_status == observation_result_status
        assert seg.effective_date_of_reference_range == effective_date_of_reference_range
        assert seg.user_defined_access_checks == user_defined_access_checks
        assert seg.date_time_of_the_observation == date_time_of_the_observation
        assert seg.date_time_of_the_analysis == date_time_of_the_analysis
        assert seg.patient_results_release_category == patient_results_release_category
        assert seg.observation_type == observation_type
        assert seg.observation_sub_type == observation_sub_type
        assert seg.action_code == action_code

    def test_obx_to_dict(self):
        seg = OBX()

        seg.set_id_obx = set_id_obx
        seg.value_type = value_type
        seg.reference_range = reference_range
        seg.probability = probability
        seg.observation_result_status = observation_result_status
        seg.effective_date_of_reference_range = effective_date_of_reference_range
        seg.user_defined_access_checks = user_defined_access_checks
        seg.date_time_of_the_observation = date_time_of_the_observation
        seg.date_time_of_the_analysis = date_time_of_the_analysis
        seg.patient_results_release_category = patient_results_release_category
        seg.observation_type = observation_type
        seg.observation_sub_type = observation_sub_type
        seg.action_code = action_code

        result = seg.to_dict()

        assert result["_segment_id"] == "OBX"
        assert result["set_id_obx"] == set_id_obx
        assert result["value_type"] == value_type
        assert result["reference_range"] == reference_range
        assert result["probability"] == probability
        assert result["observation_result_status"] == observation_result_status
        assert result["effective_date_of_reference_range"] == effective_date_of_reference_range
        assert result["user_defined_access_checks"] == user_defined_access_checks
        assert result["date_time_of_the_observation"] == date_time_of_the_observation
        assert result["date_time_of_the_analysis"] == date_time_of_the_analysis
        assert result["patient_results_release_category"] == patient_results_release_category
        assert result["observation_type"] == observation_type
        assert result["observation_sub_type"] == observation_sub_type
        assert result["action_code"] == action_code

    def test_obx_to_json(self):
        seg = OBX()

        seg.set_id_obx = set_id_obx
        seg.value_type = value_type
        seg.reference_range = reference_range
        seg.probability = probability
        seg.observation_result_status = observation_result_status
        seg.effective_date_of_reference_range = effective_date_of_reference_range
        seg.user_defined_access_checks = user_defined_access_checks
        seg.date_time_of_the_observation = date_time_of_the_observation
        seg.date_time_of_the_analysis = date_time_of_the_analysis
        seg.patient_results_release_category = patient_results_release_category
        seg.observation_type = observation_type
        seg.observation_sub_type = observation_sub_type
        seg.action_code = action_code

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "OBX"
        assert result["set_id_obx"] == set_id_obx
        assert result["value_type"] == value_type
        assert result["reference_range"] == reference_range
        assert result["probability"] == probability
        assert result["observation_result_status"] == observation_result_status
        assert result["effective_date_of_reference_range"] == effective_date_of_reference_range
        assert result["user_defined_access_checks"] == user_defined_access_checks
        assert result["date_time_of_the_observation"] == date_time_of_the_observation
        assert result["date_time_of_the_analysis"] == date_time_of_the_analysis
        assert result["patient_results_release_category"] == patient_results_release_category
        assert result["observation_type"] == observation_type
        assert result["observation_sub_type"] == observation_sub_type
        assert result["action_code"] == action_code
