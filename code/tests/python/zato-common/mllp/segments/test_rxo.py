from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import RXO


requested_give_amount_minimum = "test_requested_give_amoun"
requested_give_amount_maximum = "test_requested_give_amoun"
allow_substitutions = "test_allow_substitutions"
requested_dispense_amount = "test_requested_dispense_a"
number_of_refills = "test_number_of_refills"
needs_human_review = "test_needs_human_review"
requested_give_per_time_unit = "test_requested_give_per_t"
requested_give_strength = "test_requested_give_stren"
requested_give_rate_amount = "test_requested_give_rate_"
requested_drug_strength_volume = "test_requested_drug_stren"
pharmacy_order_type = "test_pharmacy_order_type"
dispensing_interval = "test_dispensing_interval"


class TestRXO:
    """Comprehensive tests for RXO segment."""

    def test_rxo_build_and_verify(self):
        seg = RXO()

        seg.requested_give_amount_minimum = requested_give_amount_minimum
        seg.requested_give_amount_maximum = requested_give_amount_maximum
        seg.allow_substitutions = allow_substitutions
        seg.requested_dispense_amount = requested_dispense_amount
        seg.number_of_refills = number_of_refills
        seg.needs_human_review = needs_human_review
        seg.requested_give_per_time_unit = requested_give_per_time_unit
        seg.requested_give_strength = requested_give_strength
        seg.requested_give_rate_amount = requested_give_rate_amount
        seg.requested_drug_strength_volume = requested_drug_strength_volume
        seg.pharmacy_order_type = pharmacy_order_type
        seg.dispensing_interval = dispensing_interval

        assert seg.requested_give_amount_minimum == requested_give_amount_minimum
        assert seg.requested_give_amount_maximum == requested_give_amount_maximum
        assert seg.allow_substitutions == allow_substitutions
        assert seg.requested_dispense_amount == requested_dispense_amount
        assert seg.number_of_refills == number_of_refills
        assert seg.needs_human_review == needs_human_review
        assert seg.requested_give_per_time_unit == requested_give_per_time_unit
        assert seg.requested_give_strength == requested_give_strength
        assert seg.requested_give_rate_amount == requested_give_rate_amount
        assert seg.requested_drug_strength_volume == requested_drug_strength_volume
        assert seg.pharmacy_order_type == pharmacy_order_type
        assert seg.dispensing_interval == dispensing_interval

    def test_rxo_to_dict(self):
        seg = RXO()

        seg.requested_give_amount_minimum = requested_give_amount_minimum
        seg.requested_give_amount_maximum = requested_give_amount_maximum
        seg.allow_substitutions = allow_substitutions
        seg.requested_dispense_amount = requested_dispense_amount
        seg.number_of_refills = number_of_refills
        seg.needs_human_review = needs_human_review
        seg.requested_give_per_time_unit = requested_give_per_time_unit
        seg.requested_give_strength = requested_give_strength
        seg.requested_give_rate_amount = requested_give_rate_amount
        seg.requested_drug_strength_volume = requested_drug_strength_volume
        seg.pharmacy_order_type = pharmacy_order_type
        seg.dispensing_interval = dispensing_interval

        result = seg.to_dict()

        assert result["_segment_id"] == "RXO"
        assert result["requested_give_amount_minimum"] == requested_give_amount_minimum
        assert result["requested_give_amount_maximum"] == requested_give_amount_maximum
        assert result["allow_substitutions"] == allow_substitutions
        assert result["requested_dispense_amount"] == requested_dispense_amount
        assert result["number_of_refills"] == number_of_refills
        assert result["needs_human_review"] == needs_human_review
        assert result["requested_give_per_time_unit"] == requested_give_per_time_unit
        assert result["requested_give_strength"] == requested_give_strength
        assert result["requested_give_rate_amount"] == requested_give_rate_amount
        assert result["requested_drug_strength_volume"] == requested_drug_strength_volume
        assert result["pharmacy_order_type"] == pharmacy_order_type
        assert result["dispensing_interval"] == dispensing_interval

    def test_rxo_to_json(self):
        seg = RXO()

        seg.requested_give_amount_minimum = requested_give_amount_minimum
        seg.requested_give_amount_maximum = requested_give_amount_maximum
        seg.allow_substitutions = allow_substitutions
        seg.requested_dispense_amount = requested_dispense_amount
        seg.number_of_refills = number_of_refills
        seg.needs_human_review = needs_human_review
        seg.requested_give_per_time_unit = requested_give_per_time_unit
        seg.requested_give_strength = requested_give_strength
        seg.requested_give_rate_amount = requested_give_rate_amount
        seg.requested_drug_strength_volume = requested_drug_strength_volume
        seg.pharmacy_order_type = pharmacy_order_type
        seg.dispensing_interval = dispensing_interval

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "RXO"
        assert result["requested_give_amount_minimum"] == requested_give_amount_minimum
        assert result["requested_give_amount_maximum"] == requested_give_amount_maximum
        assert result["allow_substitutions"] == allow_substitutions
        assert result["requested_dispense_amount"] == requested_dispense_amount
        assert result["number_of_refills"] == number_of_refills
        assert result["needs_human_review"] == needs_human_review
        assert result["requested_give_per_time_unit"] == requested_give_per_time_unit
        assert result["requested_give_strength"] == requested_give_strength
        assert result["requested_give_rate_amount"] == requested_give_rate_amount
        assert result["requested_drug_strength_volume"] == requested_drug_strength_volume
        assert result["pharmacy_order_type"] == pharmacy_order_type
        assert result["dispensing_interval"] == dispensing_interval
