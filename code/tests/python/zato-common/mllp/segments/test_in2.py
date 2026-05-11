from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import IN2


insureds_social_security_number = "test_insureds_social_secu"
medicare_health_ins_card_number = "test_medicare_health_ins_"
medicaid_case_number = "test_medicaid_case_number"
military_id_number = "test_military_id_number"
military_organization = "test_military_organizatio"
military_station = "test_military_station"
military_retire_date = "test_military_retire_date"
military_non_avail_cert_on_file = "test_military_non_avail_c"
baby_coverage = "test_baby_coverage"
combine_baby_bill = "test_combine_baby_bill"
blood_deductible = "test_blood_deductible"
special_coverage_approval_title = "test_special_coverage_app"
protection_indicator = "test_protection_indicator"
insureds_employment_start_date = "test_insureds_employment_"
employment_stop_date = "test_employment_stop_date"
job_title = "test_job_title"
relationship_to_the_patient_start_date = "test_relationship_to_the_"
suspend_flag = "test_suspend_flag"
copay_limit_flag = "test_copay_limit_flag"
stoploss_limit_flag = "test_stoploss_limit_flag"


class TestIN2:
    """Comprehensive tests for IN2 segment."""

    def test_in2_build_and_verify(self):
        seg = IN2()

        seg.insureds_social_security_number = insureds_social_security_number
        seg.medicare_health_ins_card_number = medicare_health_ins_card_number
        seg.medicaid_case_number = medicaid_case_number
        seg.military_id_number = military_id_number
        seg.military_organization = military_organization
        seg.military_station = military_station
        seg.military_retire_date = military_retire_date
        seg.military_non_avail_cert_on_file = military_non_avail_cert_on_file
        seg.baby_coverage = baby_coverage
        seg.combine_baby_bill = combine_baby_bill
        seg.blood_deductible = blood_deductible
        seg.special_coverage_approval_title = special_coverage_approval_title
        seg.protection_indicator = protection_indicator
        seg.insureds_employment_start_date = insureds_employment_start_date
        seg.employment_stop_date = employment_stop_date
        seg.job_title = job_title
        seg.relationship_to_the_patient_start_date = relationship_to_the_patient_start_date
        seg.suspend_flag = suspend_flag
        seg.copay_limit_flag = copay_limit_flag
        seg.stoploss_limit_flag = stoploss_limit_flag

        assert seg.insureds_social_security_number == insureds_social_security_number
        assert seg.medicare_health_ins_card_number == medicare_health_ins_card_number
        assert seg.medicaid_case_number == medicaid_case_number
        assert seg.military_id_number == military_id_number
        assert seg.military_organization == military_organization
        assert seg.military_station == military_station
        assert seg.military_retire_date == military_retire_date
        assert seg.military_non_avail_cert_on_file == military_non_avail_cert_on_file
        assert seg.baby_coverage == baby_coverage
        assert seg.combine_baby_bill == combine_baby_bill
        assert seg.blood_deductible == blood_deductible
        assert seg.special_coverage_approval_title == special_coverage_approval_title
        assert seg.protection_indicator == protection_indicator
        assert seg.insureds_employment_start_date == insureds_employment_start_date
        assert seg.employment_stop_date == employment_stop_date
        assert seg.job_title == job_title
        assert seg.relationship_to_the_patient_start_date == relationship_to_the_patient_start_date
        assert seg.suspend_flag == suspend_flag
        assert seg.copay_limit_flag == copay_limit_flag
        assert seg.stoploss_limit_flag == stoploss_limit_flag

    def test_in2_to_dict(self):
        seg = IN2()

        seg.insureds_social_security_number = insureds_social_security_number
        seg.medicare_health_ins_card_number = medicare_health_ins_card_number
        seg.medicaid_case_number = medicaid_case_number
        seg.military_id_number = military_id_number
        seg.military_organization = military_organization
        seg.military_station = military_station
        seg.military_retire_date = military_retire_date
        seg.military_non_avail_cert_on_file = military_non_avail_cert_on_file
        seg.baby_coverage = baby_coverage
        seg.combine_baby_bill = combine_baby_bill
        seg.blood_deductible = blood_deductible
        seg.special_coverage_approval_title = special_coverage_approval_title
        seg.protection_indicator = protection_indicator
        seg.insureds_employment_start_date = insureds_employment_start_date
        seg.employment_stop_date = employment_stop_date
        seg.job_title = job_title
        seg.relationship_to_the_patient_start_date = relationship_to_the_patient_start_date
        seg.suspend_flag = suspend_flag
        seg.copay_limit_flag = copay_limit_flag
        seg.stoploss_limit_flag = stoploss_limit_flag

        result = seg.to_dict()

        assert result["_segment_id"] == "IN2"
        assert result["insureds_social_security_number"] == insureds_social_security_number
        assert result["medicare_health_ins_card_number"] == medicare_health_ins_card_number
        assert result["medicaid_case_number"] == medicaid_case_number
        assert result["military_id_number"] == military_id_number
        assert result["military_organization"] == military_organization
        assert result["military_station"] == military_station
        assert result["military_retire_date"] == military_retire_date
        assert result["military_non_avail_cert_on_file"] == military_non_avail_cert_on_file
        assert result["baby_coverage"] == baby_coverage
        assert result["combine_baby_bill"] == combine_baby_bill
        assert result["blood_deductible"] == blood_deductible
        assert result["special_coverage_approval_title"] == special_coverage_approval_title
        assert result["protection_indicator"] == protection_indicator
        assert result["insureds_employment_start_date"] == insureds_employment_start_date
        assert result["employment_stop_date"] == employment_stop_date
        assert result["job_title"] == job_title
        assert result["relationship_to_the_patient_start_date"] == relationship_to_the_patient_start_date
        assert result["suspend_flag"] == suspend_flag
        assert result["copay_limit_flag"] == copay_limit_flag
        assert result["stoploss_limit_flag"] == stoploss_limit_flag

    def test_in2_to_json(self):
        seg = IN2()

        seg.insureds_social_security_number = insureds_social_security_number
        seg.medicare_health_ins_card_number = medicare_health_ins_card_number
        seg.medicaid_case_number = medicaid_case_number
        seg.military_id_number = military_id_number
        seg.military_organization = military_organization
        seg.military_station = military_station
        seg.military_retire_date = military_retire_date
        seg.military_non_avail_cert_on_file = military_non_avail_cert_on_file
        seg.baby_coverage = baby_coverage
        seg.combine_baby_bill = combine_baby_bill
        seg.blood_deductible = blood_deductible
        seg.special_coverage_approval_title = special_coverage_approval_title
        seg.protection_indicator = protection_indicator
        seg.insureds_employment_start_date = insureds_employment_start_date
        seg.employment_stop_date = employment_stop_date
        seg.job_title = job_title
        seg.relationship_to_the_patient_start_date = relationship_to_the_patient_start_date
        seg.suspend_flag = suspend_flag
        seg.copay_limit_flag = copay_limit_flag
        seg.stoploss_limit_flag = stoploss_limit_flag

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "IN2"
        assert result["insureds_social_security_number"] == insureds_social_security_number
        assert result["medicare_health_ins_card_number"] == medicare_health_ins_card_number
        assert result["medicaid_case_number"] == medicaid_case_number
        assert result["military_id_number"] == military_id_number
        assert result["military_organization"] == military_organization
        assert result["military_station"] == military_station
        assert result["military_retire_date"] == military_retire_date
        assert result["military_non_avail_cert_on_file"] == military_non_avail_cert_on_file
        assert result["baby_coverage"] == baby_coverage
        assert result["combine_baby_bill"] == combine_baby_bill
        assert result["blood_deductible"] == blood_deductible
        assert result["special_coverage_approval_title"] == special_coverage_approval_title
        assert result["protection_indicator"] == protection_indicator
        assert result["insureds_employment_start_date"] == insureds_employment_start_date
        assert result["employment_stop_date"] == employment_stop_date
        assert result["job_title"] == job_title
        assert result["relationship_to_the_patient_start_date"] == relationship_to_the_patient_start_date
        assert result["suspend_flag"] == suspend_flag
        assert result["copay_limit_flag"] == copay_limit_flag
        assert result["stoploss_limit_flag"] == stoploss_limit_flag
