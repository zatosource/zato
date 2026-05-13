from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import IN1


set_id_in1 = "test_set_id_in1"
group_number = "test_group_number"
plan_effective_date = "test_plan_effective_date"
plan_expiration_date = "test_plan_expiration_date"
insureds_date_of_birth = "test_insureds_date_of_bir"
coord_of_ben_priority = "test_coord_of_ben_priorit"
notice_of_admission_flag = "test_notice_of_admission_"
notice_of_admission_date = "test_notice_of_admission_"
report_of_eligibility_flag = "test_report_of_eligibilit"
report_of_eligibility_date = "test_report_of_eligibilit"
pre_admit_cert_pac = "test_pre_admit_cert_pac"
verification_date_time = "test_verification_date_ti"
lifetime_reserve_days = "test_lifetime_reserve_day"
delay_before_lr_day = "test_delay_before_lr_day"
policy_number = "test_policy_number"
policy_limit_days = "test_policy_limit_days"
verification_status = "test_verification_status"
signature_code_date = "test_signature_code_date"
insureds_birth_place = "test_insureds_birth_place"
insurance_action_code = "test_insurance_action_cod"


class TestIN1:
    """Comprehensive tests for IN1 segment."""

    def test_in1_build_and_verify(self):
        seg = IN1()

        seg.set_id_in1 = set_id_in1
        seg.group_number = group_number
        seg.plan_effective_date = plan_effective_date
        seg.plan_expiration_date = plan_expiration_date
        seg.insureds_date_of_birth = insureds_date_of_birth
        seg.coord_of_ben_priority = coord_of_ben_priority
        seg.notice_of_admission_flag = notice_of_admission_flag
        seg.notice_of_admission_date = notice_of_admission_date
        seg.report_of_eligibility_flag = report_of_eligibility_flag
        seg.report_of_eligibility_date = report_of_eligibility_date
        seg.pre_admit_cert_pac = pre_admit_cert_pac
        seg.verification_date_time = verification_date_time
        seg.lifetime_reserve_days = lifetime_reserve_days
        seg.delay_before_lr_day = delay_before_lr_day
        seg.policy_number = policy_number
        seg.policy_limit_days = policy_limit_days
        seg.verification_status = verification_status
        seg.signature_code_date = signature_code_date
        seg.insureds_birth_place = insureds_birth_place
        seg.insurance_action_code = insurance_action_code

        assert seg.set_id_in1 == set_id_in1
        assert seg.group_number == group_number
        assert seg.plan_effective_date == plan_effective_date
        assert seg.plan_expiration_date == plan_expiration_date
        assert seg.insureds_date_of_birth == insureds_date_of_birth
        assert seg.coord_of_ben_priority == coord_of_ben_priority
        assert seg.notice_of_admission_flag == notice_of_admission_flag
        assert seg.notice_of_admission_date == notice_of_admission_date
        assert seg.report_of_eligibility_flag == report_of_eligibility_flag
        assert seg.report_of_eligibility_date == report_of_eligibility_date
        assert seg.pre_admit_cert_pac == pre_admit_cert_pac
        assert seg.verification_date_time == verification_date_time
        assert seg.lifetime_reserve_days == lifetime_reserve_days
        assert seg.delay_before_lr_day == delay_before_lr_day
        assert seg.policy_number == policy_number
        assert seg.policy_limit_days == policy_limit_days
        assert seg.verification_status == verification_status
        assert seg.signature_code_date == signature_code_date
        assert seg.insureds_birth_place == insureds_birth_place
        assert seg.insurance_action_code == insurance_action_code

    def test_in1_to_dict(self):
        seg = IN1()

        seg.set_id_in1 = set_id_in1
        seg.group_number = group_number
        seg.plan_effective_date = plan_effective_date
        seg.plan_expiration_date = plan_expiration_date
        seg.insureds_date_of_birth = insureds_date_of_birth
        seg.coord_of_ben_priority = coord_of_ben_priority
        seg.notice_of_admission_flag = notice_of_admission_flag
        seg.notice_of_admission_date = notice_of_admission_date
        seg.report_of_eligibility_flag = report_of_eligibility_flag
        seg.report_of_eligibility_date = report_of_eligibility_date
        seg.pre_admit_cert_pac = pre_admit_cert_pac
        seg.verification_date_time = verification_date_time
        seg.lifetime_reserve_days = lifetime_reserve_days
        seg.delay_before_lr_day = delay_before_lr_day
        seg.policy_number = policy_number
        seg.policy_limit_days = policy_limit_days
        seg.verification_status = verification_status
        seg.signature_code_date = signature_code_date
        seg.insureds_birth_place = insureds_birth_place
        seg.insurance_action_code = insurance_action_code

        result = seg.to_dict()

        assert result["_segment_id"] == "IN1"
        assert result["set_id_in1"] == set_id_in1
        assert result["group_number"] == group_number
        assert result["plan_effective_date"] == plan_effective_date
        assert result["plan_expiration_date"] == plan_expiration_date
        assert result["insureds_date_of_birth"] == insureds_date_of_birth
        assert result["coord_of_ben_priority"] == coord_of_ben_priority
        assert result["notice_of_admission_flag"] == notice_of_admission_flag
        assert result["notice_of_admission_date"] == notice_of_admission_date
        assert result["report_of_eligibility_flag"] == report_of_eligibility_flag
        assert result["report_of_eligibility_date"] == report_of_eligibility_date
        assert result["pre_admit_cert_pac"] == pre_admit_cert_pac
        assert result["verification_date_time"] == verification_date_time
        assert result["lifetime_reserve_days"] == lifetime_reserve_days
        assert result["delay_before_lr_day"] == delay_before_lr_day
        assert result["policy_number"] == policy_number
        assert result["policy_limit_days"] == policy_limit_days
        assert result["verification_status"] == verification_status
        assert result["signature_code_date"] == signature_code_date
        assert result["insureds_birth_place"] == insureds_birth_place
        assert result["insurance_action_code"] == insurance_action_code

    def test_in1_to_json(self):
        seg = IN1()

        seg.set_id_in1 = set_id_in1
        seg.group_number = group_number
        seg.plan_effective_date = plan_effective_date
        seg.plan_expiration_date = plan_expiration_date
        seg.insureds_date_of_birth = insureds_date_of_birth
        seg.coord_of_ben_priority = coord_of_ben_priority
        seg.notice_of_admission_flag = notice_of_admission_flag
        seg.notice_of_admission_date = notice_of_admission_date
        seg.report_of_eligibility_flag = report_of_eligibility_flag
        seg.report_of_eligibility_date = report_of_eligibility_date
        seg.pre_admit_cert_pac = pre_admit_cert_pac
        seg.verification_date_time = verification_date_time
        seg.lifetime_reserve_days = lifetime_reserve_days
        seg.delay_before_lr_day = delay_before_lr_day
        seg.policy_number = policy_number
        seg.policy_limit_days = policy_limit_days
        seg.verification_status = verification_status
        seg.signature_code_date = signature_code_date
        seg.insureds_birth_place = insureds_birth_place
        seg.insurance_action_code = insurance_action_code

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "IN1"
        assert result["set_id_in1"] == set_id_in1
        assert result["group_number"] == group_number
        assert result["plan_effective_date"] == plan_effective_date
        assert result["plan_expiration_date"] == plan_expiration_date
        assert result["insureds_date_of_birth"] == insureds_date_of_birth
        assert result["coord_of_ben_priority"] == coord_of_ben_priority
        assert result["notice_of_admission_flag"] == notice_of_admission_flag
        assert result["notice_of_admission_date"] == notice_of_admission_date
        assert result["report_of_eligibility_flag"] == report_of_eligibility_flag
        assert result["report_of_eligibility_date"] == report_of_eligibility_date
        assert result["pre_admit_cert_pac"] == pre_admit_cert_pac
        assert result["verification_date_time"] == verification_date_time
        assert result["lifetime_reserve_days"] == lifetime_reserve_days
        assert result["delay_before_lr_day"] == delay_before_lr_day
        assert result["policy_number"] == policy_number
        assert result["policy_limit_days"] == policy_limit_days
        assert result["verification_status"] == verification_status
        assert result["signature_code_date"] == signature_code_date
        assert result["insureds_birth_place"] == insureds_birth_place
        assert result["insurance_action_code"] == insurance_action_code
