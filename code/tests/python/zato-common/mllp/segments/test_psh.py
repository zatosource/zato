from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import PSH


report_type = "test_report_type"
report_form_identifier = "test_report_form_identifi"
report_date = "test_report_date"
report_interval_start_date = "test_report_interval_star"
report_interval_end_date = "test_report_interval_end_"
quantity_distributed_method = "test_quantity_distributed"
quantity_distributed_comment = "test_quantity_distributed"
quantity_in_use_method = "test_quantity_in_use_meth"
quantity_in_use_comment = "test_quantity_in_use_comm"
number_of_product_experience_reports_filed_by_facility = "test_number_of_product_ex"
number_of_product_experience_reports_filed_by_distributor = "test_number_of_product_ex"


class TestPSH:
    """Comprehensive tests for PSH segment."""

    def test_psh_build_and_verify(self):
        seg = PSH()

        seg.report_type = report_type
        seg.report_form_identifier = report_form_identifier
        seg.report_date = report_date
        seg.report_interval_start_date = report_interval_start_date
        seg.report_interval_end_date = report_interval_end_date
        seg.quantity_distributed_method = quantity_distributed_method
        seg.quantity_distributed_comment = quantity_distributed_comment
        seg.quantity_in_use_method = quantity_in_use_method
        seg.quantity_in_use_comment = quantity_in_use_comment
        seg.number_of_product_experience_reports_filed_by_facility = number_of_product_experience_reports_filed_by_facility
        seg.number_of_product_experience_reports_filed_by_distributor = number_of_product_experience_reports_filed_by_distributor

        assert seg.report_type == report_type
        assert seg.report_form_identifier == report_form_identifier
        assert seg.report_date == report_date
        assert seg.report_interval_start_date == report_interval_start_date
        assert seg.report_interval_end_date == report_interval_end_date
        assert seg.quantity_distributed_method == quantity_distributed_method
        assert seg.quantity_distributed_comment == quantity_distributed_comment
        assert seg.quantity_in_use_method == quantity_in_use_method
        assert seg.quantity_in_use_comment == quantity_in_use_comment
        assert seg.number_of_product_experience_reports_filed_by_facility == number_of_product_experience_reports_filed_by_facility
        assert seg.number_of_product_experience_reports_filed_by_distributor == number_of_product_experience_reports_filed_by_distributor

    def test_psh_to_dict(self):
        seg = PSH()

        seg.report_type = report_type
        seg.report_form_identifier = report_form_identifier
        seg.report_date = report_date
        seg.report_interval_start_date = report_interval_start_date
        seg.report_interval_end_date = report_interval_end_date
        seg.quantity_distributed_method = quantity_distributed_method
        seg.quantity_distributed_comment = quantity_distributed_comment
        seg.quantity_in_use_method = quantity_in_use_method
        seg.quantity_in_use_comment = quantity_in_use_comment
        seg.number_of_product_experience_reports_filed_by_facility = number_of_product_experience_reports_filed_by_facility
        seg.number_of_product_experience_reports_filed_by_distributor = number_of_product_experience_reports_filed_by_distributor

        result = seg.to_dict()

        assert result["_segment_id"] == "PSH"
        assert result["report_type"] == report_type
        assert result["report_form_identifier"] == report_form_identifier
        assert result["report_date"] == report_date
        assert result["report_interval_start_date"] == report_interval_start_date
        assert result["report_interval_end_date"] == report_interval_end_date
        assert result["quantity_distributed_method"] == quantity_distributed_method
        assert result["quantity_distributed_comment"] == quantity_distributed_comment
        assert result["quantity_in_use_method"] == quantity_in_use_method
        assert result["quantity_in_use_comment"] == quantity_in_use_comment
        assert result["number_of_product_experience_reports_filed_by_facility"] == number_of_product_experience_reports_filed_by_facility
        assert result["number_of_product_experience_reports_filed_by_distributor"] == number_of_product_experience_reports_filed_by_distributor

    def test_psh_to_json(self):
        seg = PSH()

        seg.report_type = report_type
        seg.report_form_identifier = report_form_identifier
        seg.report_date = report_date
        seg.report_interval_start_date = report_interval_start_date
        seg.report_interval_end_date = report_interval_end_date
        seg.quantity_distributed_method = quantity_distributed_method
        seg.quantity_distributed_comment = quantity_distributed_comment
        seg.quantity_in_use_method = quantity_in_use_method
        seg.quantity_in_use_comment = quantity_in_use_comment
        seg.number_of_product_experience_reports_filed_by_facility = number_of_product_experience_reports_filed_by_facility
        seg.number_of_product_experience_reports_filed_by_distributor = number_of_product_experience_reports_filed_by_distributor

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "PSH"
        assert result["report_type"] == report_type
        assert result["report_form_identifier"] == report_form_identifier
        assert result["report_date"] == report_date
        assert result["report_interval_start_date"] == report_interval_start_date
        assert result["report_interval_end_date"] == report_interval_end_date
        assert result["quantity_distributed_method"] == quantity_distributed_method
        assert result["quantity_distributed_comment"] == quantity_distributed_comment
        assert result["quantity_in_use_method"] == quantity_in_use_method
        assert result["quantity_in_use_comment"] == quantity_in_use_comment
        assert result["number_of_product_experience_reports_filed_by_facility"] == number_of_product_experience_reports_filed_by_facility
        assert result["number_of_product_experience_reports_filed_by_distributor"] == number_of_product_experience_reports_filed_by_distributor
