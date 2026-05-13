from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import PV2


patient_valuables_location = "test_patient_valuables_lo"
expected_admit_date_time = "test_expected_admit_date_"
expected_discharge_date_time = "test_expected_discharge_d"
estimated_length_of_inpatient_stay = "test_estimated_length_of_"
actual_length_of_inpatient_stay = "test_actual_length_of_inp"
visit_description = "test_visit_description"
previous_service_date = "test_previous_service_dat"
employment_illness_related_indicator = "test_employment_illness_r"
purge_status_date = "test_purge_status_date"
retention_indicator = "test_retention_indicator"
expected_number_of_insurance_plans = "test_expected_number_of_i"
visit_protection_indicator = "test_visit_protection_ind"
previous_treatment_date = "test_previous_treatment_d"
signature_on_file_date = "test_signature_on_file_da"
first_similar_illness_date = "test_first_similar_illnes"
billing_media_code = "test_billing_media_code"
expected_surgery_date_and_time = "test_expected_surgery_dat"
military_partnership_code = "test_military_partnership"
military_non_availability_code = "test_military_non_availab"
newborn_baby_indicator = "test_newborn_baby_indicat"
baby_detained_indicator = "test_baby_detained_indica"
patient_status_effective_date = "test_patient_status_effec"
expected_loa_return_date_time = "test_expected_loa_return_"
expected_pre_admission_testing_date_time = "test_expected_pre_admissi"
advance_directive_last_verified_date = "test_advance_directive_la"


class TestPV2:
    """Comprehensive tests for PV2 segment."""

    def test_pv2_build_and_verify(self):
        seg = PV2()

        seg.patient_valuables_location = patient_valuables_location
        seg.expected_admit_date_time = expected_admit_date_time
        seg.expected_discharge_date_time = expected_discharge_date_time
        seg.estimated_length_of_inpatient_stay = estimated_length_of_inpatient_stay
        seg.actual_length_of_inpatient_stay = actual_length_of_inpatient_stay
        seg.visit_description = visit_description
        seg.previous_service_date = previous_service_date
        seg.employment_illness_related_indicator = employment_illness_related_indicator
        seg.purge_status_date = purge_status_date
        seg.retention_indicator = retention_indicator
        seg.expected_number_of_insurance_plans = expected_number_of_insurance_plans
        seg.visit_protection_indicator = visit_protection_indicator
        seg.previous_treatment_date = previous_treatment_date
        seg.signature_on_file_date = signature_on_file_date
        seg.first_similar_illness_date = first_similar_illness_date
        seg.billing_media_code = billing_media_code
        seg.expected_surgery_date_and_time = expected_surgery_date_and_time
        seg.military_partnership_code = military_partnership_code
        seg.military_non_availability_code = military_non_availability_code
        seg.newborn_baby_indicator = newborn_baby_indicator
        seg.baby_detained_indicator = baby_detained_indicator
        seg.patient_status_effective_date = patient_status_effective_date
        seg.expected_loa_return_date_time = expected_loa_return_date_time
        seg.expected_pre_admission_testing_date_time = expected_pre_admission_testing_date_time
        seg.advance_directive_last_verified_date = advance_directive_last_verified_date

        assert seg.patient_valuables_location == patient_valuables_location
        assert seg.expected_admit_date_time == expected_admit_date_time
        assert seg.expected_discharge_date_time == expected_discharge_date_time
        assert seg.estimated_length_of_inpatient_stay == estimated_length_of_inpatient_stay
        assert seg.actual_length_of_inpatient_stay == actual_length_of_inpatient_stay
        assert seg.visit_description == visit_description
        assert seg.previous_service_date == previous_service_date
        assert seg.employment_illness_related_indicator == employment_illness_related_indicator
        assert seg.purge_status_date == purge_status_date
        assert seg.retention_indicator == retention_indicator
        assert seg.expected_number_of_insurance_plans == expected_number_of_insurance_plans
        assert seg.visit_protection_indicator == visit_protection_indicator
        assert seg.previous_treatment_date == previous_treatment_date
        assert seg.signature_on_file_date == signature_on_file_date
        assert seg.first_similar_illness_date == first_similar_illness_date
        assert seg.billing_media_code == billing_media_code
        assert seg.expected_surgery_date_and_time == expected_surgery_date_and_time
        assert seg.military_partnership_code == military_partnership_code
        assert seg.military_non_availability_code == military_non_availability_code
        assert seg.newborn_baby_indicator == newborn_baby_indicator
        assert seg.baby_detained_indicator == baby_detained_indicator
        assert seg.patient_status_effective_date == patient_status_effective_date
        assert seg.expected_loa_return_date_time == expected_loa_return_date_time
        assert seg.expected_pre_admission_testing_date_time == expected_pre_admission_testing_date_time
        assert seg.advance_directive_last_verified_date == advance_directive_last_verified_date

    def test_pv2_to_dict(self):
        seg = PV2()

        seg.patient_valuables_location = patient_valuables_location
        seg.expected_admit_date_time = expected_admit_date_time
        seg.expected_discharge_date_time = expected_discharge_date_time
        seg.estimated_length_of_inpatient_stay = estimated_length_of_inpatient_stay
        seg.actual_length_of_inpatient_stay = actual_length_of_inpatient_stay
        seg.visit_description = visit_description
        seg.previous_service_date = previous_service_date
        seg.employment_illness_related_indicator = employment_illness_related_indicator
        seg.purge_status_date = purge_status_date
        seg.retention_indicator = retention_indicator
        seg.expected_number_of_insurance_plans = expected_number_of_insurance_plans
        seg.visit_protection_indicator = visit_protection_indicator
        seg.previous_treatment_date = previous_treatment_date
        seg.signature_on_file_date = signature_on_file_date
        seg.first_similar_illness_date = first_similar_illness_date
        seg.billing_media_code = billing_media_code
        seg.expected_surgery_date_and_time = expected_surgery_date_and_time
        seg.military_partnership_code = military_partnership_code
        seg.military_non_availability_code = military_non_availability_code
        seg.newborn_baby_indicator = newborn_baby_indicator
        seg.baby_detained_indicator = baby_detained_indicator
        seg.patient_status_effective_date = patient_status_effective_date
        seg.expected_loa_return_date_time = expected_loa_return_date_time
        seg.expected_pre_admission_testing_date_time = expected_pre_admission_testing_date_time
        seg.advance_directive_last_verified_date = advance_directive_last_verified_date

        result = seg.to_dict()

        assert result["_segment_id"] == "PV2"
        assert result["patient_valuables_location"] == patient_valuables_location
        assert result["expected_admit_date_time"] == expected_admit_date_time
        assert result["expected_discharge_date_time"] == expected_discharge_date_time
        assert result["estimated_length_of_inpatient_stay"] == estimated_length_of_inpatient_stay
        assert result["actual_length_of_inpatient_stay"] == actual_length_of_inpatient_stay
        assert result["visit_description"] == visit_description
        assert result["previous_service_date"] == previous_service_date
        assert result["employment_illness_related_indicator"] == employment_illness_related_indicator
        assert result["purge_status_date"] == purge_status_date
        assert result["retention_indicator"] == retention_indicator
        assert result["expected_number_of_insurance_plans"] == expected_number_of_insurance_plans
        assert result["visit_protection_indicator"] == visit_protection_indicator
        assert result["previous_treatment_date"] == previous_treatment_date
        assert result["signature_on_file_date"] == signature_on_file_date
        assert result["first_similar_illness_date"] == first_similar_illness_date
        assert result["billing_media_code"] == billing_media_code
        assert result["expected_surgery_date_and_time"] == expected_surgery_date_and_time
        assert result["military_partnership_code"] == military_partnership_code
        assert result["military_non_availability_code"] == military_non_availability_code
        assert result["newborn_baby_indicator"] == newborn_baby_indicator
        assert result["baby_detained_indicator"] == baby_detained_indicator
        assert result["patient_status_effective_date"] == patient_status_effective_date
        assert result["expected_loa_return_date_time"] == expected_loa_return_date_time
        assert result["expected_pre_admission_testing_date_time"] == expected_pre_admission_testing_date_time
        assert result["advance_directive_last_verified_date"] == advance_directive_last_verified_date

    def test_pv2_to_json(self):
        seg = PV2()

        seg.patient_valuables_location = patient_valuables_location
        seg.expected_admit_date_time = expected_admit_date_time
        seg.expected_discharge_date_time = expected_discharge_date_time
        seg.estimated_length_of_inpatient_stay = estimated_length_of_inpatient_stay
        seg.actual_length_of_inpatient_stay = actual_length_of_inpatient_stay
        seg.visit_description = visit_description
        seg.previous_service_date = previous_service_date
        seg.employment_illness_related_indicator = employment_illness_related_indicator
        seg.purge_status_date = purge_status_date
        seg.retention_indicator = retention_indicator
        seg.expected_number_of_insurance_plans = expected_number_of_insurance_plans
        seg.visit_protection_indicator = visit_protection_indicator
        seg.previous_treatment_date = previous_treatment_date
        seg.signature_on_file_date = signature_on_file_date
        seg.first_similar_illness_date = first_similar_illness_date
        seg.billing_media_code = billing_media_code
        seg.expected_surgery_date_and_time = expected_surgery_date_and_time
        seg.military_partnership_code = military_partnership_code
        seg.military_non_availability_code = military_non_availability_code
        seg.newborn_baby_indicator = newborn_baby_indicator
        seg.baby_detained_indicator = baby_detained_indicator
        seg.patient_status_effective_date = patient_status_effective_date
        seg.expected_loa_return_date_time = expected_loa_return_date_time
        seg.expected_pre_admission_testing_date_time = expected_pre_admission_testing_date_time
        seg.advance_directive_last_verified_date = advance_directive_last_verified_date

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "PV2"
        assert result["patient_valuables_location"] == patient_valuables_location
        assert result["expected_admit_date_time"] == expected_admit_date_time
        assert result["expected_discharge_date_time"] == expected_discharge_date_time
        assert result["estimated_length_of_inpatient_stay"] == estimated_length_of_inpatient_stay
        assert result["actual_length_of_inpatient_stay"] == actual_length_of_inpatient_stay
        assert result["visit_description"] == visit_description
        assert result["previous_service_date"] == previous_service_date
        assert result["employment_illness_related_indicator"] == employment_illness_related_indicator
        assert result["purge_status_date"] == purge_status_date
        assert result["retention_indicator"] == retention_indicator
        assert result["expected_number_of_insurance_plans"] == expected_number_of_insurance_plans
        assert result["visit_protection_indicator"] == visit_protection_indicator
        assert result["previous_treatment_date"] == previous_treatment_date
        assert result["signature_on_file_date"] == signature_on_file_date
        assert result["first_similar_illness_date"] == first_similar_illness_date
        assert result["billing_media_code"] == billing_media_code
        assert result["expected_surgery_date_and_time"] == expected_surgery_date_and_time
        assert result["military_partnership_code"] == military_partnership_code
        assert result["military_non_availability_code"] == military_non_availability_code
        assert result["newborn_baby_indicator"] == newborn_baby_indicator
        assert result["baby_detained_indicator"] == baby_detained_indicator
        assert result["patient_status_effective_date"] == patient_status_effective_date
        assert result["expected_loa_return_date_time"] == expected_loa_return_date_time
        assert result["expected_pre_admission_testing_date_time"] == expected_pre_admission_testing_date_time
        assert result["advance_directive_last_verified_date"] == advance_directive_last_verified_date
