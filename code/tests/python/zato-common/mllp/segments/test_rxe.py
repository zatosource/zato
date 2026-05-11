from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import RXE


give_amount_minimum = "test_give_amount_minimum"
give_amount_maximum = "test_give_amount_maximum"
substitution_status = "test_substitution_status"
dispense_amount = "test_dispense_amount"
number_of_refills = "test_number_of_refills"
prescription_number = "test_prescription_number"
number_of_refills_remaining = "test_number_of_refills_re"
number_of_refills_doses_dispensed = "test_number_of_refills_do"
dt_of_most_recent_refill_or_dose_dispensed = "test_dt_of_most_recent_re"
needs_human_review = "test_needs_human_review"
give_per_time_unit = "test_give_per_time_unit"
give_rate_amount = "test_give_rate_amount"
give_strength = "test_give_strength"
dispense_package_size = "test_dispense_package_siz"
dispense_package_method = "test_dispense_package_met"
original_order_date_time = "test_original_order_date_"
give_drug_strength_volume = "test_give_drug_strength_v"
formulary_status = "test_formulary_status"
initial_dispense_amount = "test_initial_dispense_amo"
pharmacy_order_type = "test_pharmacy_order_type"


class TestRXE:
    """Comprehensive tests for RXE segment."""

    def test_rxe_build_and_verify(self):
        seg = RXE()

        seg.give_amount_minimum = give_amount_minimum
        seg.give_amount_maximum = give_amount_maximum
        seg.substitution_status = substitution_status
        seg.dispense_amount = dispense_amount
        seg.number_of_refills = number_of_refills
        seg.prescription_number = prescription_number
        seg.number_of_refills_remaining = number_of_refills_remaining
        seg.number_of_refills_doses_dispensed = number_of_refills_doses_dispensed
        seg.dt_of_most_recent_refill_or_dose_dispensed = dt_of_most_recent_refill_or_dose_dispensed
        seg.needs_human_review = needs_human_review
        seg.give_per_time_unit = give_per_time_unit
        seg.give_rate_amount = give_rate_amount
        seg.give_strength = give_strength
        seg.dispense_package_size = dispense_package_size
        seg.dispense_package_method = dispense_package_method
        seg.original_order_date_time = original_order_date_time
        seg.give_drug_strength_volume = give_drug_strength_volume
        seg.formulary_status = formulary_status
        seg.initial_dispense_amount = initial_dispense_amount
        seg.pharmacy_order_type = pharmacy_order_type

        assert seg.give_amount_minimum == give_amount_minimum
        assert seg.give_amount_maximum == give_amount_maximum
        assert seg.substitution_status == substitution_status
        assert seg.dispense_amount == dispense_amount
        assert seg.number_of_refills == number_of_refills
        assert seg.prescription_number == prescription_number
        assert seg.number_of_refills_remaining == number_of_refills_remaining
        assert seg.number_of_refills_doses_dispensed == number_of_refills_doses_dispensed
        assert seg.dt_of_most_recent_refill_or_dose_dispensed == dt_of_most_recent_refill_or_dose_dispensed
        assert seg.needs_human_review == needs_human_review
        assert seg.give_per_time_unit == give_per_time_unit
        assert seg.give_rate_amount == give_rate_amount
        assert seg.give_strength == give_strength
        assert seg.dispense_package_size == dispense_package_size
        assert seg.dispense_package_method == dispense_package_method
        assert seg.original_order_date_time == original_order_date_time
        assert seg.give_drug_strength_volume == give_drug_strength_volume
        assert seg.formulary_status == formulary_status
        assert seg.initial_dispense_amount == initial_dispense_amount
        assert seg.pharmacy_order_type == pharmacy_order_type

    def test_rxe_to_dict(self):
        seg = RXE()

        seg.give_amount_minimum = give_amount_minimum
        seg.give_amount_maximum = give_amount_maximum
        seg.substitution_status = substitution_status
        seg.dispense_amount = dispense_amount
        seg.number_of_refills = number_of_refills
        seg.prescription_number = prescription_number
        seg.number_of_refills_remaining = number_of_refills_remaining
        seg.number_of_refills_doses_dispensed = number_of_refills_doses_dispensed
        seg.dt_of_most_recent_refill_or_dose_dispensed = dt_of_most_recent_refill_or_dose_dispensed
        seg.needs_human_review = needs_human_review
        seg.give_per_time_unit = give_per_time_unit
        seg.give_rate_amount = give_rate_amount
        seg.give_strength = give_strength
        seg.dispense_package_size = dispense_package_size
        seg.dispense_package_method = dispense_package_method
        seg.original_order_date_time = original_order_date_time
        seg.give_drug_strength_volume = give_drug_strength_volume
        seg.formulary_status = formulary_status
        seg.initial_dispense_amount = initial_dispense_amount
        seg.pharmacy_order_type = pharmacy_order_type

        result = seg.to_dict()

        assert result["_segment_id"] == "RXE"
        assert result["give_amount_minimum"] == give_amount_minimum
        assert result["give_amount_maximum"] == give_amount_maximum
        assert result["substitution_status"] == substitution_status
        assert result["dispense_amount"] == dispense_amount
        assert result["number_of_refills"] == number_of_refills
        assert result["prescription_number"] == prescription_number
        assert result["number_of_refills_remaining"] == number_of_refills_remaining
        assert result["number_of_refills_doses_dispensed"] == number_of_refills_doses_dispensed
        assert result["dt_of_most_recent_refill_or_dose_dispensed"] == dt_of_most_recent_refill_or_dose_dispensed
        assert result["needs_human_review"] == needs_human_review
        assert result["give_per_time_unit"] == give_per_time_unit
        assert result["give_rate_amount"] == give_rate_amount
        assert result["give_strength"] == give_strength
        assert result["dispense_package_size"] == dispense_package_size
        assert result["dispense_package_method"] == dispense_package_method
        assert result["original_order_date_time"] == original_order_date_time
        assert result["give_drug_strength_volume"] == give_drug_strength_volume
        assert result["formulary_status"] == formulary_status
        assert result["initial_dispense_amount"] == initial_dispense_amount
        assert result["pharmacy_order_type"] == pharmacy_order_type

    def test_rxe_to_json(self):
        seg = RXE()

        seg.give_amount_minimum = give_amount_minimum
        seg.give_amount_maximum = give_amount_maximum
        seg.substitution_status = substitution_status
        seg.dispense_amount = dispense_amount
        seg.number_of_refills = number_of_refills
        seg.prescription_number = prescription_number
        seg.number_of_refills_remaining = number_of_refills_remaining
        seg.number_of_refills_doses_dispensed = number_of_refills_doses_dispensed
        seg.dt_of_most_recent_refill_or_dose_dispensed = dt_of_most_recent_refill_or_dose_dispensed
        seg.needs_human_review = needs_human_review
        seg.give_per_time_unit = give_per_time_unit
        seg.give_rate_amount = give_rate_amount
        seg.give_strength = give_strength
        seg.dispense_package_size = dispense_package_size
        seg.dispense_package_method = dispense_package_method
        seg.original_order_date_time = original_order_date_time
        seg.give_drug_strength_volume = give_drug_strength_volume
        seg.formulary_status = formulary_status
        seg.initial_dispense_amount = initial_dispense_amount
        seg.pharmacy_order_type = pharmacy_order_type

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "RXE"
        assert result["give_amount_minimum"] == give_amount_minimum
        assert result["give_amount_maximum"] == give_amount_maximum
        assert result["substitution_status"] == substitution_status
        assert result["dispense_amount"] == dispense_amount
        assert result["number_of_refills"] == number_of_refills
        assert result["prescription_number"] == prescription_number
        assert result["number_of_refills_remaining"] == number_of_refills_remaining
        assert result["number_of_refills_doses_dispensed"] == number_of_refills_doses_dispensed
        assert result["dt_of_most_recent_refill_or_dose_dispensed"] == dt_of_most_recent_refill_or_dose_dispensed
        assert result["needs_human_review"] == needs_human_review
        assert result["give_per_time_unit"] == give_per_time_unit
        assert result["give_rate_amount"] == give_rate_amount
        assert result["give_strength"] == give_strength
        assert result["dispense_package_size"] == dispense_package_size
        assert result["dispense_package_method"] == dispense_package_method
        assert result["original_order_date_time"] == original_order_date_time
        assert result["give_drug_strength_volume"] == give_drug_strength_volume
        assert result["formulary_status"] == formulary_status
        assert result["initial_dispense_amount"] == initial_dispense_amount
        assert result["pharmacy_order_type"] == pharmacy_order_type
