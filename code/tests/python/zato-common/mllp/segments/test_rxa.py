from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import RXA


give_sub_id_counter = "test_give_sub_id_counter"
administration_sub_id_counter = "test_administration_sub_i"
date_time_start_of_administration = "test_date_time_start_of_a"
date_time_end_of_administration = "test_date_time_end_of_adm"
administered_amount = "test_administered_amount"
administered_per_time_unit = "test_administered_per_tim"
administered_strength = "test_administered_strengt"
completion_status = "test_completion_status"
action_code_rxa = "test_action_code_rxa"
system_entry_date_time = "test_system_entry_date_ti"
administered_drug_strength_volume = "test_administered_drug_st"
pharmacy_order_type = "test_pharmacy_order_type"


class TestRXA:
    """Comprehensive tests for RXA segment."""

    def test_rxa_build_and_verify(self):
        seg = RXA()

        seg.give_sub_id_counter = give_sub_id_counter
        seg.administration_sub_id_counter = administration_sub_id_counter
        seg.date_time_start_of_administration = date_time_start_of_administration
        seg.date_time_end_of_administration = date_time_end_of_administration
        seg.administered_amount = administered_amount
        seg.administered_per_time_unit = administered_per_time_unit
        seg.administered_strength = administered_strength
        seg.completion_status = completion_status
        seg.action_code_rxa = action_code_rxa
        seg.system_entry_date_time = system_entry_date_time
        seg.administered_drug_strength_volume = administered_drug_strength_volume
        seg.pharmacy_order_type = pharmacy_order_type

        assert seg.give_sub_id_counter == give_sub_id_counter
        assert seg.administration_sub_id_counter == administration_sub_id_counter
        assert seg.date_time_start_of_administration == date_time_start_of_administration
        assert seg.date_time_end_of_administration == date_time_end_of_administration
        assert seg.administered_amount == administered_amount
        assert seg.administered_per_time_unit == administered_per_time_unit
        assert seg.administered_strength == administered_strength
        assert seg.completion_status == completion_status
        assert seg.action_code_rxa == action_code_rxa
        assert seg.system_entry_date_time == system_entry_date_time
        assert seg.administered_drug_strength_volume == administered_drug_strength_volume
        assert seg.pharmacy_order_type == pharmacy_order_type

    def test_rxa_to_dict(self):
        seg = RXA()

        seg.give_sub_id_counter = give_sub_id_counter
        seg.administration_sub_id_counter = administration_sub_id_counter
        seg.date_time_start_of_administration = date_time_start_of_administration
        seg.date_time_end_of_administration = date_time_end_of_administration
        seg.administered_amount = administered_amount
        seg.administered_per_time_unit = administered_per_time_unit
        seg.administered_strength = administered_strength
        seg.completion_status = completion_status
        seg.action_code_rxa = action_code_rxa
        seg.system_entry_date_time = system_entry_date_time
        seg.administered_drug_strength_volume = administered_drug_strength_volume
        seg.pharmacy_order_type = pharmacy_order_type

        result = seg.to_dict()

        assert result["_segment_id"] == "RXA"
        assert result["give_sub_id_counter"] == give_sub_id_counter
        assert result["administration_sub_id_counter"] == administration_sub_id_counter
        assert result["date_time_start_of_administration"] == date_time_start_of_administration
        assert result["date_time_end_of_administration"] == date_time_end_of_administration
        assert result["administered_amount"] == administered_amount
        assert result["administered_per_time_unit"] == administered_per_time_unit
        assert result["administered_strength"] == administered_strength
        assert result["completion_status"] == completion_status
        assert result["action_code_rxa"] == action_code_rxa
        assert result["system_entry_date_time"] == system_entry_date_time
        assert result["administered_drug_strength_volume"] == administered_drug_strength_volume
        assert result["pharmacy_order_type"] == pharmacy_order_type

    def test_rxa_to_json(self):
        seg = RXA()

        seg.give_sub_id_counter = give_sub_id_counter
        seg.administration_sub_id_counter = administration_sub_id_counter
        seg.date_time_start_of_administration = date_time_start_of_administration
        seg.date_time_end_of_administration = date_time_end_of_administration
        seg.administered_amount = administered_amount
        seg.administered_per_time_unit = administered_per_time_unit
        seg.administered_strength = administered_strength
        seg.completion_status = completion_status
        seg.action_code_rxa = action_code_rxa
        seg.system_entry_date_time = system_entry_date_time
        seg.administered_drug_strength_volume = administered_drug_strength_volume
        seg.pharmacy_order_type = pharmacy_order_type

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "RXA"
        assert result["give_sub_id_counter"] == give_sub_id_counter
        assert result["administration_sub_id_counter"] == administration_sub_id_counter
        assert result["date_time_start_of_administration"] == date_time_start_of_administration
        assert result["date_time_end_of_administration"] == date_time_end_of_administration
        assert result["administered_amount"] == administered_amount
        assert result["administered_per_time_unit"] == administered_per_time_unit
        assert result["administered_strength"] == administered_strength
        assert result["completion_status"] == completion_status
        assert result["action_code_rxa"] == action_code_rxa
        assert result["system_entry_date_time"] == system_entry_date_time
        assert result["administered_drug_strength_volume"] == administered_drug_strength_volume
        assert result["pharmacy_order_type"] == pharmacy_order_type
