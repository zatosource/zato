from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import PSL


product_service_line_item_sequence_number = "test_product_service_line"
product_service_code_description = "test_product_service_code"
product_service_effective_date = "test_product_service_effe"
product_service_expiration_date = "test_product_service_expi"
number_of_items_per_unit = "test_number_of_items_per_"
product_service_clarification_code_value = "test_product_service_clar"
restricted_disclosure_indicator = "test_restricted_disclosur"
product_service_cost_factor = "test_product_service_cost"
days_without_billing = "test_days_without_billing"
session_no = "test_session_no"
number_of_t_ps_pp = "test_number_of_t_ps_pp"
internal_scaling_factor_pp = "test_internal_scaling_fac"
external_scaling_factor_pp = "test_external_scaling_fac"
number_of_t_ps_technical_part = "test_number_of_t_ps_techn"
internal_scaling_factor_technical_part = "test_internal_scaling_fac"
external_scaling_factor_technical_part = "test_external_scaling_fac"
vat_rate = "test_vat_rate"
main_service = "test_main_service"
validation = "test_validation"
comment = "test_comment"


class TestPSL:
    """Comprehensive tests for PSL segment."""

    def test_psl_build_and_verify(self):
        seg = PSL()

        seg.product_service_line_item_sequence_number = product_service_line_item_sequence_number
        seg.product_service_code_description = product_service_code_description
        seg.product_service_effective_date = product_service_effective_date
        seg.product_service_expiration_date = product_service_expiration_date
        seg.number_of_items_per_unit = number_of_items_per_unit
        seg.product_service_clarification_code_value = product_service_clarification_code_value
        seg.restricted_disclosure_indicator = restricted_disclosure_indicator
        seg.product_service_cost_factor = product_service_cost_factor
        seg.days_without_billing = days_without_billing
        seg.session_no = session_no
        seg.number_of_t_ps_pp = number_of_t_ps_pp
        seg.internal_scaling_factor_pp = internal_scaling_factor_pp
        seg.external_scaling_factor_pp = external_scaling_factor_pp
        seg.number_of_t_ps_technical_part = number_of_t_ps_technical_part
        seg.internal_scaling_factor_technical_part = internal_scaling_factor_technical_part
        seg.external_scaling_factor_technical_part = external_scaling_factor_technical_part
        seg.vat_rate = vat_rate
        seg.main_service = main_service
        seg.validation = validation
        seg.comment = comment

        assert seg.product_service_line_item_sequence_number == product_service_line_item_sequence_number
        assert seg.product_service_code_description == product_service_code_description
        assert seg.product_service_effective_date == product_service_effective_date
        assert seg.product_service_expiration_date == product_service_expiration_date
        assert seg.number_of_items_per_unit == number_of_items_per_unit
        assert seg.product_service_clarification_code_value == product_service_clarification_code_value
        assert seg.restricted_disclosure_indicator == restricted_disclosure_indicator
        assert seg.product_service_cost_factor == product_service_cost_factor
        assert seg.days_without_billing == days_without_billing
        assert seg.session_no == session_no
        assert seg.number_of_t_ps_pp == number_of_t_ps_pp
        assert seg.internal_scaling_factor_pp == internal_scaling_factor_pp
        assert seg.external_scaling_factor_pp == external_scaling_factor_pp
        assert seg.number_of_t_ps_technical_part == number_of_t_ps_technical_part
        assert seg.internal_scaling_factor_technical_part == internal_scaling_factor_technical_part
        assert seg.external_scaling_factor_technical_part == external_scaling_factor_technical_part
        assert seg.vat_rate == vat_rate
        assert seg.main_service == main_service
        assert seg.validation == validation
        assert seg.comment == comment

    def test_psl_to_dict(self):
        seg = PSL()

        seg.product_service_line_item_sequence_number = product_service_line_item_sequence_number
        seg.product_service_code_description = product_service_code_description
        seg.product_service_effective_date = product_service_effective_date
        seg.product_service_expiration_date = product_service_expiration_date
        seg.number_of_items_per_unit = number_of_items_per_unit
        seg.product_service_clarification_code_value = product_service_clarification_code_value
        seg.restricted_disclosure_indicator = restricted_disclosure_indicator
        seg.product_service_cost_factor = product_service_cost_factor
        seg.days_without_billing = days_without_billing
        seg.session_no = session_no
        seg.number_of_t_ps_pp = number_of_t_ps_pp
        seg.internal_scaling_factor_pp = internal_scaling_factor_pp
        seg.external_scaling_factor_pp = external_scaling_factor_pp
        seg.number_of_t_ps_technical_part = number_of_t_ps_technical_part
        seg.internal_scaling_factor_technical_part = internal_scaling_factor_technical_part
        seg.external_scaling_factor_technical_part = external_scaling_factor_technical_part
        seg.vat_rate = vat_rate
        seg.main_service = main_service
        seg.validation = validation
        seg.comment = comment

        result = seg.to_dict()

        assert result["_segment_id"] == "PSL"
        assert result["product_service_line_item_sequence_number"] == product_service_line_item_sequence_number
        assert result["product_service_code_description"] == product_service_code_description
        assert result["product_service_effective_date"] == product_service_effective_date
        assert result["product_service_expiration_date"] == product_service_expiration_date
        assert result["number_of_items_per_unit"] == number_of_items_per_unit
        assert result["product_service_clarification_code_value"] == product_service_clarification_code_value
        assert result["restricted_disclosure_indicator"] == restricted_disclosure_indicator
        assert result["product_service_cost_factor"] == product_service_cost_factor
        assert result["days_without_billing"] == days_without_billing
        assert result["session_no"] == session_no
        assert result["number_of_t_ps_pp"] == number_of_t_ps_pp
        assert result["internal_scaling_factor_pp"] == internal_scaling_factor_pp
        assert result["external_scaling_factor_pp"] == external_scaling_factor_pp
        assert result["number_of_t_ps_technical_part"] == number_of_t_ps_technical_part
        assert result["internal_scaling_factor_technical_part"] == internal_scaling_factor_technical_part
        assert result["external_scaling_factor_technical_part"] == external_scaling_factor_technical_part
        assert result["vat_rate"] == vat_rate
        assert result["main_service"] == main_service
        assert result["validation"] == validation
        assert result["comment"] == comment

    def test_psl_to_json(self):
        seg = PSL()

        seg.product_service_line_item_sequence_number = product_service_line_item_sequence_number
        seg.product_service_code_description = product_service_code_description
        seg.product_service_effective_date = product_service_effective_date
        seg.product_service_expiration_date = product_service_expiration_date
        seg.number_of_items_per_unit = number_of_items_per_unit
        seg.product_service_clarification_code_value = product_service_clarification_code_value
        seg.restricted_disclosure_indicator = restricted_disclosure_indicator
        seg.product_service_cost_factor = product_service_cost_factor
        seg.days_without_billing = days_without_billing
        seg.session_no = session_no
        seg.number_of_t_ps_pp = number_of_t_ps_pp
        seg.internal_scaling_factor_pp = internal_scaling_factor_pp
        seg.external_scaling_factor_pp = external_scaling_factor_pp
        seg.number_of_t_ps_technical_part = number_of_t_ps_technical_part
        seg.internal_scaling_factor_technical_part = internal_scaling_factor_technical_part
        seg.external_scaling_factor_technical_part = external_scaling_factor_technical_part
        seg.vat_rate = vat_rate
        seg.main_service = main_service
        seg.validation = validation
        seg.comment = comment

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "PSL"
        assert result["product_service_line_item_sequence_number"] == product_service_line_item_sequence_number
        assert result["product_service_code_description"] == product_service_code_description
        assert result["product_service_effective_date"] == product_service_effective_date
        assert result["product_service_expiration_date"] == product_service_expiration_date
        assert result["number_of_items_per_unit"] == number_of_items_per_unit
        assert result["product_service_clarification_code_value"] == product_service_clarification_code_value
        assert result["restricted_disclosure_indicator"] == restricted_disclosure_indicator
        assert result["product_service_cost_factor"] == product_service_cost_factor
        assert result["days_without_billing"] == days_without_billing
        assert result["session_no"] == session_no
        assert result["number_of_t_ps_pp"] == number_of_t_ps_pp
        assert result["internal_scaling_factor_pp"] == internal_scaling_factor_pp
        assert result["external_scaling_factor_pp"] == external_scaling_factor_pp
        assert result["number_of_t_ps_technical_part"] == number_of_t_ps_technical_part
        assert result["internal_scaling_factor_technical_part"] == internal_scaling_factor_technical_part
        assert result["external_scaling_factor_technical_part"] == external_scaling_factor_technical_part
        assert result["vat_rate"] == vat_rate
        assert result["main_service"] == main_service
        assert result["validation"] == validation
        assert result["comment"] == comment
