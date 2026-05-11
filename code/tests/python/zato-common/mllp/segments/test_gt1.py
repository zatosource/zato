from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import GT1


set_id_gt1 = "test_set_id_gt1"
guarantor_date_time_of_birth = "test_guarantor_date_time_"
guarantor_ssn = "test_guarantor_ssn"
guarantor_date_begin = "test_guarantor_date_begin"
guarantor_date_end = "test_guarantor_date_end"
guarantor_priority = "test_guarantor_priority"
guarantor_billing_hold_flag = "test_guarantor_billing_ho"
guarantor_death_date_and_time = "test_guarantor_death_date"
guarantor_death_flag = "test_guarantor_death_flag"
guarantor_household_size = "test_guarantor_household_"
guarantor_hire_effective_date = "test_guarantor_hire_effec"
employment_stop_date = "test_employment_stop_date"
protection_indicator = "test_protection_indicator"
job_title = "test_job_title"
guarantor_birth_place = "test_guarantor_birth_plac"


class TestGT1:
    """Comprehensive tests for GT1 segment."""

    def test_gt1_build_and_verify(self):
        seg = GT1()

        seg.set_id_gt1 = set_id_gt1
        seg.guarantor_date_time_of_birth = guarantor_date_time_of_birth
        seg.guarantor_ssn = guarantor_ssn
        seg.guarantor_date_begin = guarantor_date_begin
        seg.guarantor_date_end = guarantor_date_end
        seg.guarantor_priority = guarantor_priority
        seg.guarantor_billing_hold_flag = guarantor_billing_hold_flag
        seg.guarantor_death_date_and_time = guarantor_death_date_and_time
        seg.guarantor_death_flag = guarantor_death_flag
        seg.guarantor_household_size = guarantor_household_size
        seg.guarantor_hire_effective_date = guarantor_hire_effective_date
        seg.employment_stop_date = employment_stop_date
        seg.protection_indicator = protection_indicator
        seg.job_title = job_title
        seg.guarantor_birth_place = guarantor_birth_place

        assert seg.set_id_gt1 == set_id_gt1
        assert seg.guarantor_date_time_of_birth == guarantor_date_time_of_birth
        assert seg.guarantor_ssn == guarantor_ssn
        assert seg.guarantor_date_begin == guarantor_date_begin
        assert seg.guarantor_date_end == guarantor_date_end
        assert seg.guarantor_priority == guarantor_priority
        assert seg.guarantor_billing_hold_flag == guarantor_billing_hold_flag
        assert seg.guarantor_death_date_and_time == guarantor_death_date_and_time
        assert seg.guarantor_death_flag == guarantor_death_flag
        assert seg.guarantor_household_size == guarantor_household_size
        assert seg.guarantor_hire_effective_date == guarantor_hire_effective_date
        assert seg.employment_stop_date == employment_stop_date
        assert seg.protection_indicator == protection_indicator
        assert seg.job_title == job_title
        assert seg.guarantor_birth_place == guarantor_birth_place

    def test_gt1_to_dict(self):
        seg = GT1()

        seg.set_id_gt1 = set_id_gt1
        seg.guarantor_date_time_of_birth = guarantor_date_time_of_birth
        seg.guarantor_ssn = guarantor_ssn
        seg.guarantor_date_begin = guarantor_date_begin
        seg.guarantor_date_end = guarantor_date_end
        seg.guarantor_priority = guarantor_priority
        seg.guarantor_billing_hold_flag = guarantor_billing_hold_flag
        seg.guarantor_death_date_and_time = guarantor_death_date_and_time
        seg.guarantor_death_flag = guarantor_death_flag
        seg.guarantor_household_size = guarantor_household_size
        seg.guarantor_hire_effective_date = guarantor_hire_effective_date
        seg.employment_stop_date = employment_stop_date
        seg.protection_indicator = protection_indicator
        seg.job_title = job_title
        seg.guarantor_birth_place = guarantor_birth_place

        result = seg.to_dict()

        assert result["_segment_id"] == "GT1"
        assert result["set_id_gt1"] == set_id_gt1
        assert result["guarantor_date_time_of_birth"] == guarantor_date_time_of_birth
        assert result["guarantor_ssn"] == guarantor_ssn
        assert result["guarantor_date_begin"] == guarantor_date_begin
        assert result["guarantor_date_end"] == guarantor_date_end
        assert result["guarantor_priority"] == guarantor_priority
        assert result["guarantor_billing_hold_flag"] == guarantor_billing_hold_flag
        assert result["guarantor_death_date_and_time"] == guarantor_death_date_and_time
        assert result["guarantor_death_flag"] == guarantor_death_flag
        assert result["guarantor_household_size"] == guarantor_household_size
        assert result["guarantor_hire_effective_date"] == guarantor_hire_effective_date
        assert result["employment_stop_date"] == employment_stop_date
        assert result["protection_indicator"] == protection_indicator
        assert result["job_title"] == job_title
        assert result["guarantor_birth_place"] == guarantor_birth_place

    def test_gt1_to_json(self):
        seg = GT1()

        seg.set_id_gt1 = set_id_gt1
        seg.guarantor_date_time_of_birth = guarantor_date_time_of_birth
        seg.guarantor_ssn = guarantor_ssn
        seg.guarantor_date_begin = guarantor_date_begin
        seg.guarantor_date_end = guarantor_date_end
        seg.guarantor_priority = guarantor_priority
        seg.guarantor_billing_hold_flag = guarantor_billing_hold_flag
        seg.guarantor_death_date_and_time = guarantor_death_date_and_time
        seg.guarantor_death_flag = guarantor_death_flag
        seg.guarantor_household_size = guarantor_household_size
        seg.guarantor_hire_effective_date = guarantor_hire_effective_date
        seg.employment_stop_date = employment_stop_date
        seg.protection_indicator = protection_indicator
        seg.job_title = job_title
        seg.guarantor_birth_place = guarantor_birth_place

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "GT1"
        assert result["set_id_gt1"] == set_id_gt1
        assert result["guarantor_date_time_of_birth"] == guarantor_date_time_of_birth
        assert result["guarantor_ssn"] == guarantor_ssn
        assert result["guarantor_date_begin"] == guarantor_date_begin
        assert result["guarantor_date_end"] == guarantor_date_end
        assert result["guarantor_priority"] == guarantor_priority
        assert result["guarantor_billing_hold_flag"] == guarantor_billing_hold_flag
        assert result["guarantor_death_date_and_time"] == guarantor_death_date_and_time
        assert result["guarantor_death_flag"] == guarantor_death_flag
        assert result["guarantor_household_size"] == guarantor_household_size
        assert result["guarantor_hire_effective_date"] == guarantor_hire_effective_date
        assert result["employment_stop_date"] == employment_stop_date
        assert result["protection_indicator"] == protection_indicator
        assert result["job_title"] == job_title
        assert result["guarantor_birth_place"] == guarantor_birth_place
