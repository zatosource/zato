from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import UB2


set_id_ub2 = "test_set_id_ub2"
co_insurance_days_9 = "test_co_insurance_days_9"
covered_days_7 = "test_covered_days_7"
non_covered_days_8 = "test_non_covered_days_8"
uniform_billing_locator_2_state = "test_uniform_billing_loca"
uniform_billing_locator_11_state = "test_uniform_billing_loca"
uniform_billing_locator_31_national = "test_uniform_billing_loca"
document_control_number = "test_document_control_num"
uniform_billing_locator_49_national = "test_uniform_billing_loca"
uniform_billing_locator_56_state = "test_uniform_billing_loca"
uniform_billing_locator_57_sational = "test_uniform_billing_loca"
uniform_billing_locator_78_state = "test_uniform_billing_loca"
special_visit_count = "test_special_visit_count"


class TestUB2:
    """Comprehensive tests for UB2 segment."""

    def test_ub2_build_and_verify(self):
        seg = UB2()

        seg.set_id_ub2 = set_id_ub2
        seg.co_insurance_days_9 = co_insurance_days_9
        seg.covered_days_7 = covered_days_7
        seg.non_covered_days_8 = non_covered_days_8
        seg.uniform_billing_locator_2_state = uniform_billing_locator_2_state
        seg.uniform_billing_locator_11_state = uniform_billing_locator_11_state
        seg.uniform_billing_locator_31_national = uniform_billing_locator_31_national
        seg.document_control_number = document_control_number
        seg.uniform_billing_locator_49_national = uniform_billing_locator_49_national
        seg.uniform_billing_locator_56_state = uniform_billing_locator_56_state
        seg.uniform_billing_locator_57_sational = uniform_billing_locator_57_sational
        seg.uniform_billing_locator_78_state = uniform_billing_locator_78_state
        seg.special_visit_count = special_visit_count

        assert seg.set_id_ub2 == set_id_ub2
        assert seg.co_insurance_days_9 == co_insurance_days_9
        assert seg.covered_days_7 == covered_days_7
        assert seg.non_covered_days_8 == non_covered_days_8
        assert seg.uniform_billing_locator_2_state == uniform_billing_locator_2_state
        assert seg.uniform_billing_locator_11_state == uniform_billing_locator_11_state
        assert seg.uniform_billing_locator_31_national == uniform_billing_locator_31_national
        assert seg.document_control_number == document_control_number
        assert seg.uniform_billing_locator_49_national == uniform_billing_locator_49_national
        assert seg.uniform_billing_locator_56_state == uniform_billing_locator_56_state
        assert seg.uniform_billing_locator_57_sational == uniform_billing_locator_57_sational
        assert seg.uniform_billing_locator_78_state == uniform_billing_locator_78_state
        assert seg.special_visit_count == special_visit_count

    def test_ub2_to_dict(self):
        seg = UB2()

        seg.set_id_ub2 = set_id_ub2
        seg.co_insurance_days_9 = co_insurance_days_9
        seg.covered_days_7 = covered_days_7
        seg.non_covered_days_8 = non_covered_days_8
        seg.uniform_billing_locator_2_state = uniform_billing_locator_2_state
        seg.uniform_billing_locator_11_state = uniform_billing_locator_11_state
        seg.uniform_billing_locator_31_national = uniform_billing_locator_31_national
        seg.document_control_number = document_control_number
        seg.uniform_billing_locator_49_national = uniform_billing_locator_49_national
        seg.uniform_billing_locator_56_state = uniform_billing_locator_56_state
        seg.uniform_billing_locator_57_sational = uniform_billing_locator_57_sational
        seg.uniform_billing_locator_78_state = uniform_billing_locator_78_state
        seg.special_visit_count = special_visit_count

        result = seg.to_dict()

        assert result["_segment_id"] == "UB2"
        assert result["set_id_ub2"] == set_id_ub2
        assert result["co_insurance_days_9"] == co_insurance_days_9
        assert result["covered_days_7"] == covered_days_7
        assert result["non_covered_days_8"] == non_covered_days_8
        assert result["uniform_billing_locator_2_state"] == uniform_billing_locator_2_state
        assert result["uniform_billing_locator_11_state"] == uniform_billing_locator_11_state
        assert result["uniform_billing_locator_31_national"] == uniform_billing_locator_31_national
        assert result["document_control_number"] == document_control_number
        assert result["uniform_billing_locator_49_national"] == uniform_billing_locator_49_national
        assert result["uniform_billing_locator_56_state"] == uniform_billing_locator_56_state
        assert result["uniform_billing_locator_57_sational"] == uniform_billing_locator_57_sational
        assert result["uniform_billing_locator_78_state"] == uniform_billing_locator_78_state
        assert result["special_visit_count"] == special_visit_count

    def test_ub2_to_json(self):
        seg = UB2()

        seg.set_id_ub2 = set_id_ub2
        seg.co_insurance_days_9 = co_insurance_days_9
        seg.covered_days_7 = covered_days_7
        seg.non_covered_days_8 = non_covered_days_8
        seg.uniform_billing_locator_2_state = uniform_billing_locator_2_state
        seg.uniform_billing_locator_11_state = uniform_billing_locator_11_state
        seg.uniform_billing_locator_31_national = uniform_billing_locator_31_national
        seg.document_control_number = document_control_number
        seg.uniform_billing_locator_49_national = uniform_billing_locator_49_national
        seg.uniform_billing_locator_56_state = uniform_billing_locator_56_state
        seg.uniform_billing_locator_57_sational = uniform_billing_locator_57_sational
        seg.uniform_billing_locator_78_state = uniform_billing_locator_78_state
        seg.special_visit_count = special_visit_count

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "UB2"
        assert result["set_id_ub2"] == set_id_ub2
        assert result["co_insurance_days_9"] == co_insurance_days_9
        assert result["covered_days_7"] == covered_days_7
        assert result["non_covered_days_8"] == non_covered_days_8
        assert result["uniform_billing_locator_2_state"] == uniform_billing_locator_2_state
        assert result["uniform_billing_locator_11_state"] == uniform_billing_locator_11_state
        assert result["uniform_billing_locator_31_national"] == uniform_billing_locator_31_national
        assert result["document_control_number"] == document_control_number
        assert result["uniform_billing_locator_49_national"] == uniform_billing_locator_49_national
        assert result["uniform_billing_locator_56_state"] == uniform_billing_locator_56_state
        assert result["uniform_billing_locator_57_sational"] == uniform_billing_locator_57_sational
        assert result["uniform_billing_locator_78_state"] == uniform_billing_locator_78_state
        assert result["special_visit_count"] == special_visit_count
