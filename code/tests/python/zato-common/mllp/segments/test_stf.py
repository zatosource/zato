from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import STF


date_time_of_birth = "test_date_time_of_birth"
active_inactive_flag = "test_active_inactive_flag"
job_title = "test_job_title"
additional_insured_on_auto = "test_additional_insured_o"
copy_auto_ins = "test_copy_auto_ins"
auto_ins_expires = "test_auto_ins_expires"
date_last_dmv_review = "test_date_last_dmv_review"
date_next_dmv_review = "test_date_next_dmv_review"
re_activation_approval_indicator = "test_re_activation_approv"
date_time_of_death = "test_date_time_of_death"
death_indicator = "test_death_indicator"
expected_return_date = "test_expected_return_date"
generic_classification_indicator = "test_generic_classificati"


class TestSTF:
    """Comprehensive tests for STF segment."""

    def test_stf_build_and_verify(self):
        seg = STF()

        seg.date_time_of_birth = date_time_of_birth
        seg.active_inactive_flag = active_inactive_flag
        seg.job_title = job_title
        seg.additional_insured_on_auto = additional_insured_on_auto
        seg.copy_auto_ins = copy_auto_ins
        seg.auto_ins_expires = auto_ins_expires
        seg.date_last_dmv_review = date_last_dmv_review
        seg.date_next_dmv_review = date_next_dmv_review
        seg.re_activation_approval_indicator = re_activation_approval_indicator
        seg.date_time_of_death = date_time_of_death
        seg.death_indicator = death_indicator
        seg.expected_return_date = expected_return_date
        seg.generic_classification_indicator = generic_classification_indicator

        assert seg.date_time_of_birth == date_time_of_birth
        assert seg.active_inactive_flag == active_inactive_flag
        assert seg.job_title == job_title
        assert seg.additional_insured_on_auto == additional_insured_on_auto
        assert seg.copy_auto_ins == copy_auto_ins
        assert seg.auto_ins_expires == auto_ins_expires
        assert seg.date_last_dmv_review == date_last_dmv_review
        assert seg.date_next_dmv_review == date_next_dmv_review
        assert seg.re_activation_approval_indicator == re_activation_approval_indicator
        assert seg.date_time_of_death == date_time_of_death
        assert seg.death_indicator == death_indicator
        assert seg.expected_return_date == expected_return_date
        assert seg.generic_classification_indicator == generic_classification_indicator

    def test_stf_to_dict(self):
        seg = STF()

        seg.date_time_of_birth = date_time_of_birth
        seg.active_inactive_flag = active_inactive_flag
        seg.job_title = job_title
        seg.additional_insured_on_auto = additional_insured_on_auto
        seg.copy_auto_ins = copy_auto_ins
        seg.auto_ins_expires = auto_ins_expires
        seg.date_last_dmv_review = date_last_dmv_review
        seg.date_next_dmv_review = date_next_dmv_review
        seg.re_activation_approval_indicator = re_activation_approval_indicator
        seg.date_time_of_death = date_time_of_death
        seg.death_indicator = death_indicator
        seg.expected_return_date = expected_return_date
        seg.generic_classification_indicator = generic_classification_indicator

        result = seg.to_dict()

        assert result["_segment_id"] == "STF"
        assert result["date_time_of_birth"] == date_time_of_birth
        assert result["active_inactive_flag"] == active_inactive_flag
        assert result["job_title"] == job_title
        assert result["additional_insured_on_auto"] == additional_insured_on_auto
        assert result["copy_auto_ins"] == copy_auto_ins
        assert result["auto_ins_expires"] == auto_ins_expires
        assert result["date_last_dmv_review"] == date_last_dmv_review
        assert result["date_next_dmv_review"] == date_next_dmv_review
        assert result["re_activation_approval_indicator"] == re_activation_approval_indicator
        assert result["date_time_of_death"] == date_time_of_death
        assert result["death_indicator"] == death_indicator
        assert result["expected_return_date"] == expected_return_date
        assert result["generic_classification_indicator"] == generic_classification_indicator

    def test_stf_to_json(self):
        seg = STF()

        seg.date_time_of_birth = date_time_of_birth
        seg.active_inactive_flag = active_inactive_flag
        seg.job_title = job_title
        seg.additional_insured_on_auto = additional_insured_on_auto
        seg.copy_auto_ins = copy_auto_ins
        seg.auto_ins_expires = auto_ins_expires
        seg.date_last_dmv_review = date_last_dmv_review
        seg.date_next_dmv_review = date_next_dmv_review
        seg.re_activation_approval_indicator = re_activation_approval_indicator
        seg.date_time_of_death = date_time_of_death
        seg.death_indicator = death_indicator
        seg.expected_return_date = expected_return_date
        seg.generic_classification_indicator = generic_classification_indicator

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "STF"
        assert result["date_time_of_birth"] == date_time_of_birth
        assert result["active_inactive_flag"] == active_inactive_flag
        assert result["job_title"] == job_title
        assert result["additional_insured_on_auto"] == additional_insured_on_auto
        assert result["copy_auto_ins"] == copy_auto_ins
        assert result["auto_ins_expires"] == auto_ins_expires
        assert result["date_last_dmv_review"] == date_last_dmv_review
        assert result["date_next_dmv_review"] == date_next_dmv_review
        assert result["re_activation_approval_indicator"] == re_activation_approval_indicator
        assert result["date_time_of_death"] == date_time_of_death
        assert result["death_indicator"] == death_indicator
        assert result["expected_return_date"] == expected_return_date
        assert result["generic_classification_indicator"] == generic_classification_indicator
