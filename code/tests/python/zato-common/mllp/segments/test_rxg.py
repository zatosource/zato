from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import RXG


give_sub_id_counter = "test_give_sub_id_counter"
dispense_sub_id_counter = "test_dispense_sub_id_coun"
give_amount_minimum = "test_give_amount_minimum"
give_amount_maximum = "test_give_amount_maximum"
substitution_status = "test_substitution_status"
needs_human_review = "test_needs_human_review"
give_per_time_unit = "test_give_per_time_unit"
give_rate_amount = "test_give_rate_amount"
give_strength = "test_give_strength"
give_drug_strength_volume = "test_give_drug_strength_v"
pharmacy_order_type = "test_pharmacy_order_type"
dispense_amount = "test_dispense_amount"


class TestRXG:
    """Comprehensive tests for RXG segment."""

    def test_rxg_build_and_verify(self):
        seg = RXG()

        seg.give_sub_id_counter = give_sub_id_counter
        seg.dispense_sub_id_counter = dispense_sub_id_counter
        seg.give_amount_minimum = give_amount_minimum
        seg.give_amount_maximum = give_amount_maximum
        seg.substitution_status = substitution_status
        seg.needs_human_review = needs_human_review
        seg.give_per_time_unit = give_per_time_unit
        seg.give_rate_amount = give_rate_amount
        seg.give_strength = give_strength
        seg.give_drug_strength_volume = give_drug_strength_volume
        seg.pharmacy_order_type = pharmacy_order_type
        seg.dispense_amount = dispense_amount

        assert seg.give_sub_id_counter == give_sub_id_counter
        assert seg.dispense_sub_id_counter == dispense_sub_id_counter
        assert seg.give_amount_minimum == give_amount_minimum
        assert seg.give_amount_maximum == give_amount_maximum
        assert seg.substitution_status == substitution_status
        assert seg.needs_human_review == needs_human_review
        assert seg.give_per_time_unit == give_per_time_unit
        assert seg.give_rate_amount == give_rate_amount
        assert seg.give_strength == give_strength
        assert seg.give_drug_strength_volume == give_drug_strength_volume
        assert seg.pharmacy_order_type == pharmacy_order_type
        assert seg.dispense_amount == dispense_amount

    def test_rxg_to_dict(self):
        seg = RXG()

        seg.give_sub_id_counter = give_sub_id_counter
        seg.dispense_sub_id_counter = dispense_sub_id_counter
        seg.give_amount_minimum = give_amount_minimum
        seg.give_amount_maximum = give_amount_maximum
        seg.substitution_status = substitution_status
        seg.needs_human_review = needs_human_review
        seg.give_per_time_unit = give_per_time_unit
        seg.give_rate_amount = give_rate_amount
        seg.give_strength = give_strength
        seg.give_drug_strength_volume = give_drug_strength_volume
        seg.pharmacy_order_type = pharmacy_order_type
        seg.dispense_amount = dispense_amount

        result = seg.to_dict()

        assert result["_segment_id"] == "RXG"
        assert result["give_sub_id_counter"] == give_sub_id_counter
        assert result["dispense_sub_id_counter"] == dispense_sub_id_counter
        assert result["give_amount_minimum"] == give_amount_minimum
        assert result["give_amount_maximum"] == give_amount_maximum
        assert result["substitution_status"] == substitution_status
        assert result["needs_human_review"] == needs_human_review
        assert result["give_per_time_unit"] == give_per_time_unit
        assert result["give_rate_amount"] == give_rate_amount
        assert result["give_strength"] == give_strength
        assert result["give_drug_strength_volume"] == give_drug_strength_volume
        assert result["pharmacy_order_type"] == pharmacy_order_type
        assert result["dispense_amount"] == dispense_amount

    def test_rxg_to_json(self):
        seg = RXG()

        seg.give_sub_id_counter = give_sub_id_counter
        seg.dispense_sub_id_counter = dispense_sub_id_counter
        seg.give_amount_minimum = give_amount_minimum
        seg.give_amount_maximum = give_amount_maximum
        seg.substitution_status = substitution_status
        seg.needs_human_review = needs_human_review
        seg.give_per_time_unit = give_per_time_unit
        seg.give_rate_amount = give_rate_amount
        seg.give_strength = give_strength
        seg.give_drug_strength_volume = give_drug_strength_volume
        seg.pharmacy_order_type = pharmacy_order_type
        seg.dispense_amount = dispense_amount

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "RXG"
        assert result["give_sub_id_counter"] == give_sub_id_counter
        assert result["dispense_sub_id_counter"] == dispense_sub_id_counter
        assert result["give_amount_minimum"] == give_amount_minimum
        assert result["give_amount_maximum"] == give_amount_maximum
        assert result["substitution_status"] == substitution_status
        assert result["needs_human_review"] == needs_human_review
        assert result["give_per_time_unit"] == give_per_time_unit
        assert result["give_rate_amount"] == give_rate_amount
        assert result["give_strength"] == give_strength
        assert result["give_drug_strength_volume"] == give_drug_strength_volume
        assert result["pharmacy_order_type"] == pharmacy_order_type
        assert result["dispense_amount"] == dispense_amount
