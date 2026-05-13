from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import IN3


set_id_in3 = "test_set_id_in3"
certification_required = "test_certification_requir"
certification_date_time = "test_certification_date_t"
certification_modify_date_time = "test_certification_modify"
certification_begin_date = "test_certification_begin_"
certification_end_date = "test_certification_end_da"
non_concur_effective_date_time = "test_non_concur_effective"
certification_contact = "test_certification_contac"
case_manager = "test_case_manager"
second_opinion_date = "test_second_opinion_date"
online_verification_date_time = "test_online_verification_"
online_verification_result_check_digit = "test_online_verification_"


class TestIN3:
    """Comprehensive tests for IN3 segment."""

    def test_in3_build_and_verify(self):
        seg = IN3()

        seg.set_id_in3 = set_id_in3
        seg.certification_required = certification_required
        seg.certification_date_time = certification_date_time
        seg.certification_modify_date_time = certification_modify_date_time
        seg.certification_begin_date = certification_begin_date
        seg.certification_end_date = certification_end_date
        seg.non_concur_effective_date_time = non_concur_effective_date_time
        seg.certification_contact = certification_contact
        seg.case_manager = case_manager
        seg.second_opinion_date = second_opinion_date
        seg.online_verification_date_time = online_verification_date_time
        seg.online_verification_result_check_digit = online_verification_result_check_digit

        assert seg.set_id_in3 == set_id_in3
        assert seg.certification_required == certification_required
        assert seg.certification_date_time == certification_date_time
        assert seg.certification_modify_date_time == certification_modify_date_time
        assert seg.certification_begin_date == certification_begin_date
        assert seg.certification_end_date == certification_end_date
        assert seg.non_concur_effective_date_time == non_concur_effective_date_time
        assert seg.certification_contact == certification_contact
        assert seg.case_manager == case_manager
        assert seg.second_opinion_date == second_opinion_date
        assert seg.online_verification_date_time == online_verification_date_time
        assert seg.online_verification_result_check_digit == online_verification_result_check_digit

    def test_in3_to_dict(self):
        seg = IN3()

        seg.set_id_in3 = set_id_in3
        seg.certification_required = certification_required
        seg.certification_date_time = certification_date_time
        seg.certification_modify_date_time = certification_modify_date_time
        seg.certification_begin_date = certification_begin_date
        seg.certification_end_date = certification_end_date
        seg.non_concur_effective_date_time = non_concur_effective_date_time
        seg.certification_contact = certification_contact
        seg.case_manager = case_manager
        seg.second_opinion_date = second_opinion_date
        seg.online_verification_date_time = online_verification_date_time
        seg.online_verification_result_check_digit = online_verification_result_check_digit

        result = seg.to_dict()

        assert result["_segment_id"] == "IN3"
        assert result["set_id_in3"] == set_id_in3
        assert result["certification_required"] == certification_required
        assert result["certification_date_time"] == certification_date_time
        assert result["certification_modify_date_time"] == certification_modify_date_time
        assert result["certification_begin_date"] == certification_begin_date
        assert result["certification_end_date"] == certification_end_date
        assert result["non_concur_effective_date_time"] == non_concur_effective_date_time
        assert result["certification_contact"] == certification_contact
        assert result["case_manager"] == case_manager
        assert result["second_opinion_date"] == second_opinion_date
        assert result["online_verification_date_time"] == online_verification_date_time
        assert result["online_verification_result_check_digit"] == online_verification_result_check_digit

    def test_in3_to_json(self):
        seg = IN3()

        seg.set_id_in3 = set_id_in3
        seg.certification_required = certification_required
        seg.certification_date_time = certification_date_time
        seg.certification_modify_date_time = certification_modify_date_time
        seg.certification_begin_date = certification_begin_date
        seg.certification_end_date = certification_end_date
        seg.non_concur_effective_date_time = non_concur_effective_date_time
        seg.certification_contact = certification_contact
        seg.case_manager = case_manager
        seg.second_opinion_date = second_opinion_date
        seg.online_verification_date_time = online_verification_date_time
        seg.online_verification_result_check_digit = online_verification_result_check_digit

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "IN3"
        assert result["set_id_in3"] == set_id_in3
        assert result["certification_required"] == certification_required
        assert result["certification_date_time"] == certification_date_time
        assert result["certification_modify_date_time"] == certification_modify_date_time
        assert result["certification_begin_date"] == certification_begin_date
        assert result["certification_end_date"] == certification_end_date
        assert result["non_concur_effective_date_time"] == non_concur_effective_date_time
        assert result["certification_contact"] == certification_contact
        assert result["case_manager"] == case_manager
        assert result["second_opinion_date"] == second_opinion_date
        assert result["online_verification_date_time"] == online_verification_date_time
        assert result["online_verification_result_check_digit"] == online_verification_result_check_digit
