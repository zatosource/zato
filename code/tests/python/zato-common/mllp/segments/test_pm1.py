from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import PM1


group_number = "test_group_number"
plan_effective_date = "test_plan_effective_date"
plan_expiration_date = "test_plan_expiration_date"
patient_dob_required = "test_patient_dob_required"
patient_gender_required = "test_patient_gender_requi"
patient_relationship_required = "test_patient_relationship"
patient_signature_required = "test_patient_signature_re"
diagnosis_required = "test_diagnosis_required"
service_required = "test_service_required"
patient_name_required = "test_patient_name_require"
patient_address_required = "test_patient_address_requ"
subscribers_name_required = "test_subscribers_name_req"
workmans_comp_indicator = "test_workmans_comp_indica"
bill_type_required = "test_bill_type_required"
commercial_carrier_name_and_address_required = "test_commercial_carrier_n"
policy_number_pattern = "test_policy_number_patter"
group_number_pattern = "test_group_number_pattern"


class TestPM1:
    """Comprehensive tests for PM1 segment."""

    def test_pm1_build_and_verify(self):
        seg = PM1()

        seg.group_number = group_number
        seg.plan_effective_date = plan_effective_date
        seg.plan_expiration_date = plan_expiration_date
        seg.patient_dob_required = patient_dob_required
        seg.patient_gender_required = patient_gender_required
        seg.patient_relationship_required = patient_relationship_required
        seg.patient_signature_required = patient_signature_required
        seg.diagnosis_required = diagnosis_required
        seg.service_required = service_required
        seg.patient_name_required = patient_name_required
        seg.patient_address_required = patient_address_required
        seg.subscribers_name_required = subscribers_name_required
        seg.workmans_comp_indicator = workmans_comp_indicator
        seg.bill_type_required = bill_type_required
        seg.commercial_carrier_name_and_address_required = commercial_carrier_name_and_address_required
        seg.policy_number_pattern = policy_number_pattern
        seg.group_number_pattern = group_number_pattern

        assert seg.group_number == group_number
        assert seg.plan_effective_date == plan_effective_date
        assert seg.plan_expiration_date == plan_expiration_date
        assert seg.patient_dob_required == patient_dob_required
        assert seg.patient_gender_required == patient_gender_required
        assert seg.patient_relationship_required == patient_relationship_required
        assert seg.patient_signature_required == patient_signature_required
        assert seg.diagnosis_required == diagnosis_required
        assert seg.service_required == service_required
        assert seg.patient_name_required == patient_name_required
        assert seg.patient_address_required == patient_address_required
        assert seg.subscribers_name_required == subscribers_name_required
        assert seg.workmans_comp_indicator == workmans_comp_indicator
        assert seg.bill_type_required == bill_type_required
        assert seg.commercial_carrier_name_and_address_required == commercial_carrier_name_and_address_required
        assert seg.policy_number_pattern == policy_number_pattern
        assert seg.group_number_pattern == group_number_pattern

    def test_pm1_to_dict(self):
        seg = PM1()

        seg.group_number = group_number
        seg.plan_effective_date = plan_effective_date
        seg.plan_expiration_date = plan_expiration_date
        seg.patient_dob_required = patient_dob_required
        seg.patient_gender_required = patient_gender_required
        seg.patient_relationship_required = patient_relationship_required
        seg.patient_signature_required = patient_signature_required
        seg.diagnosis_required = diagnosis_required
        seg.service_required = service_required
        seg.patient_name_required = patient_name_required
        seg.patient_address_required = patient_address_required
        seg.subscribers_name_required = subscribers_name_required
        seg.workmans_comp_indicator = workmans_comp_indicator
        seg.bill_type_required = bill_type_required
        seg.commercial_carrier_name_and_address_required = commercial_carrier_name_and_address_required
        seg.policy_number_pattern = policy_number_pattern
        seg.group_number_pattern = group_number_pattern

        result = seg.to_dict()

        assert result["_segment_id"] == "PM1"
        assert result["group_number"] == group_number
        assert result["plan_effective_date"] == plan_effective_date
        assert result["plan_expiration_date"] == plan_expiration_date
        assert result["patient_dob_required"] == patient_dob_required
        assert result["patient_gender_required"] == patient_gender_required
        assert result["patient_relationship_required"] == patient_relationship_required
        assert result["patient_signature_required"] == patient_signature_required
        assert result["diagnosis_required"] == diagnosis_required
        assert result["service_required"] == service_required
        assert result["patient_name_required"] == patient_name_required
        assert result["patient_address_required"] == patient_address_required
        assert result["subscribers_name_required"] == subscribers_name_required
        assert result["workmans_comp_indicator"] == workmans_comp_indicator
        assert result["bill_type_required"] == bill_type_required
        assert result["commercial_carrier_name_and_address_required"] == commercial_carrier_name_and_address_required
        assert result["policy_number_pattern"] == policy_number_pattern
        assert result["group_number_pattern"] == group_number_pattern

    def test_pm1_to_json(self):
        seg = PM1()

        seg.group_number = group_number
        seg.plan_effective_date = plan_effective_date
        seg.plan_expiration_date = plan_expiration_date
        seg.patient_dob_required = patient_dob_required
        seg.patient_gender_required = patient_gender_required
        seg.patient_relationship_required = patient_relationship_required
        seg.patient_signature_required = patient_signature_required
        seg.diagnosis_required = diagnosis_required
        seg.service_required = service_required
        seg.patient_name_required = patient_name_required
        seg.patient_address_required = patient_address_required
        seg.subscribers_name_required = subscribers_name_required
        seg.workmans_comp_indicator = workmans_comp_indicator
        seg.bill_type_required = bill_type_required
        seg.commercial_carrier_name_and_address_required = commercial_carrier_name_and_address_required
        seg.policy_number_pattern = policy_number_pattern
        seg.group_number_pattern = group_number_pattern

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "PM1"
        assert result["group_number"] == group_number
        assert result["plan_effective_date"] == plan_effective_date
        assert result["plan_expiration_date"] == plan_expiration_date
        assert result["patient_dob_required"] == patient_dob_required
        assert result["patient_gender_required"] == patient_gender_required
        assert result["patient_relationship_required"] == patient_relationship_required
        assert result["patient_signature_required"] == patient_signature_required
        assert result["diagnosis_required"] == diagnosis_required
        assert result["service_required"] == service_required
        assert result["patient_name_required"] == patient_name_required
        assert result["patient_address_required"] == patient_address_required
        assert result["subscribers_name_required"] == subscribers_name_required
        assert result["workmans_comp_indicator"] == workmans_comp_indicator
        assert result["bill_type_required"] == bill_type_required
        assert result["commercial_carrier_name_and_address_required"] == commercial_carrier_name_and_address_required
        assert result["policy_number_pattern"] == policy_number_pattern
        assert result["group_number_pattern"] == group_number_pattern
