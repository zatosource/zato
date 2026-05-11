from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import OM7


sequence_number_test_observation_master_file = "test_sequence_number_test"
category_description = "test_category_description"
effective_test_service_start_date_time = "test_effective_test_servi"
effective_test_service_end_date_time = "test_effective_test_servi"
test_service_default_duration_quantity = "test_test_service_default"
consent_indicator = "test_consent_indicator"
consent_effective_start_date_time = "test_consent_effective_st"
consent_effective_end_date_time = "test_consent_effective_en"
consent_interval_quantity = "test_consent_interval_qua"
consent_waiting_period_quantity = "test_consent_waiting_peri"
effective_date_time_of_change = "test_effective_date_time_"
special_order_indicator = "test_special_order_indica"


class TestOM7:
    """Comprehensive tests for OM7 segment."""

    def test_om7_build_and_verify(self):
        seg = OM7()

        seg.sequence_number_test_observation_master_file = sequence_number_test_observation_master_file
        seg.category_description = category_description
        seg.effective_test_service_start_date_time = effective_test_service_start_date_time
        seg.effective_test_service_end_date_time = effective_test_service_end_date_time
        seg.test_service_default_duration_quantity = test_service_default_duration_quantity
        seg.consent_indicator = consent_indicator
        seg.consent_effective_start_date_time = consent_effective_start_date_time
        seg.consent_effective_end_date_time = consent_effective_end_date_time
        seg.consent_interval_quantity = consent_interval_quantity
        seg.consent_waiting_period_quantity = consent_waiting_period_quantity
        seg.effective_date_time_of_change = effective_date_time_of_change
        seg.special_order_indicator = special_order_indicator

        assert seg.sequence_number_test_observation_master_file == sequence_number_test_observation_master_file
        assert seg.category_description == category_description
        assert seg.effective_test_service_start_date_time == effective_test_service_start_date_time
        assert seg.effective_test_service_end_date_time == effective_test_service_end_date_time
        assert seg.test_service_default_duration_quantity == test_service_default_duration_quantity
        assert seg.consent_indicator == consent_indicator
        assert seg.consent_effective_start_date_time == consent_effective_start_date_time
        assert seg.consent_effective_end_date_time == consent_effective_end_date_time
        assert seg.consent_interval_quantity == consent_interval_quantity
        assert seg.consent_waiting_period_quantity == consent_waiting_period_quantity
        assert seg.effective_date_time_of_change == effective_date_time_of_change
        assert seg.special_order_indicator == special_order_indicator

    def test_om7_to_dict(self):
        seg = OM7()

        seg.sequence_number_test_observation_master_file = sequence_number_test_observation_master_file
        seg.category_description = category_description
        seg.effective_test_service_start_date_time = effective_test_service_start_date_time
        seg.effective_test_service_end_date_time = effective_test_service_end_date_time
        seg.test_service_default_duration_quantity = test_service_default_duration_quantity
        seg.consent_indicator = consent_indicator
        seg.consent_effective_start_date_time = consent_effective_start_date_time
        seg.consent_effective_end_date_time = consent_effective_end_date_time
        seg.consent_interval_quantity = consent_interval_quantity
        seg.consent_waiting_period_quantity = consent_waiting_period_quantity
        seg.effective_date_time_of_change = effective_date_time_of_change
        seg.special_order_indicator = special_order_indicator

        result = seg.to_dict()

        assert result["_segment_id"] == "OM7"
        assert result["sequence_number_test_observation_master_file"] == sequence_number_test_observation_master_file
        assert result["category_description"] == category_description
        assert result["effective_test_service_start_date_time"] == effective_test_service_start_date_time
        assert result["effective_test_service_end_date_time"] == effective_test_service_end_date_time
        assert result["test_service_default_duration_quantity"] == test_service_default_duration_quantity
        assert result["consent_indicator"] == consent_indicator
        assert result["consent_effective_start_date_time"] == consent_effective_start_date_time
        assert result["consent_effective_end_date_time"] == consent_effective_end_date_time
        assert result["consent_interval_quantity"] == consent_interval_quantity
        assert result["consent_waiting_period_quantity"] == consent_waiting_period_quantity
        assert result["effective_date_time_of_change"] == effective_date_time_of_change
        assert result["special_order_indicator"] == special_order_indicator

    def test_om7_to_json(self):
        seg = OM7()

        seg.sequence_number_test_observation_master_file = sequence_number_test_observation_master_file
        seg.category_description = category_description
        seg.effective_test_service_start_date_time = effective_test_service_start_date_time
        seg.effective_test_service_end_date_time = effective_test_service_end_date_time
        seg.test_service_default_duration_quantity = test_service_default_duration_quantity
        seg.consent_indicator = consent_indicator
        seg.consent_effective_start_date_time = consent_effective_start_date_time
        seg.consent_effective_end_date_time = consent_effective_end_date_time
        seg.consent_interval_quantity = consent_interval_quantity
        seg.consent_waiting_period_quantity = consent_waiting_period_quantity
        seg.effective_date_time_of_change = effective_date_time_of_change
        seg.special_order_indicator = special_order_indicator

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "OM7"
        assert result["sequence_number_test_observation_master_file"] == sequence_number_test_observation_master_file
        assert result["category_description"] == category_description
        assert result["effective_test_service_start_date_time"] == effective_test_service_start_date_time
        assert result["effective_test_service_end_date_time"] == effective_test_service_end_date_time
        assert result["test_service_default_duration_quantity"] == test_service_default_duration_quantity
        assert result["consent_indicator"] == consent_indicator
        assert result["consent_effective_start_date_time"] == consent_effective_start_date_time
        assert result["consent_effective_end_date_time"] == consent_effective_end_date_time
        assert result["consent_interval_quantity"] == consent_interval_quantity
        assert result["consent_waiting_period_quantity"] == consent_waiting_period_quantity
        assert result["effective_date_time_of_change"] == effective_date_time_of_change
        assert result["special_order_indicator"] == special_order_indicator
