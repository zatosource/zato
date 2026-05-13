from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import RXD


dispense_sub_id_counter = "test_dispense_sub_id_coun"
date_time_dispensed = "test_date_time_dispensed"
actual_dispense_amount = "test_actual_dispense_amou"
prescription_number = "test_prescription_number"
number_of_refills_remaining = "test_number_of_refills_re"
substitution_status = "test_substitution_status"
needs_human_review = "test_needs_human_review"
actual_strength = "test_actual_strength"
dispense_package_size = "test_dispense_package_siz"
dispense_package_method = "test_dispense_package_met"
actual_drug_strength_volume = "test_actual_drug_strength"
pharmacy_order_type = "test_pharmacy_order_type"


class TestRXD:
    """Comprehensive tests for RXD segment."""

    def test_rxd_build_and_verify(self):
        seg = RXD()

        seg.dispense_sub_id_counter = dispense_sub_id_counter
        seg.date_time_dispensed = date_time_dispensed
        seg.actual_dispense_amount = actual_dispense_amount
        seg.prescription_number = prescription_number
        seg.number_of_refills_remaining = number_of_refills_remaining
        seg.substitution_status = substitution_status
        seg.needs_human_review = needs_human_review
        seg.actual_strength = actual_strength
        seg.dispense_package_size = dispense_package_size
        seg.dispense_package_method = dispense_package_method
        seg.actual_drug_strength_volume = actual_drug_strength_volume
        seg.pharmacy_order_type = pharmacy_order_type

        assert seg.dispense_sub_id_counter == dispense_sub_id_counter
        assert seg.date_time_dispensed == date_time_dispensed
        assert seg.actual_dispense_amount == actual_dispense_amount
        assert seg.prescription_number == prescription_number
        assert seg.number_of_refills_remaining == number_of_refills_remaining
        assert seg.substitution_status == substitution_status
        assert seg.needs_human_review == needs_human_review
        assert seg.actual_strength == actual_strength
        assert seg.dispense_package_size == dispense_package_size
        assert seg.dispense_package_method == dispense_package_method
        assert seg.actual_drug_strength_volume == actual_drug_strength_volume
        assert seg.pharmacy_order_type == pharmacy_order_type

    def test_rxd_to_dict(self):
        seg = RXD()

        seg.dispense_sub_id_counter = dispense_sub_id_counter
        seg.date_time_dispensed = date_time_dispensed
        seg.actual_dispense_amount = actual_dispense_amount
        seg.prescription_number = prescription_number
        seg.number_of_refills_remaining = number_of_refills_remaining
        seg.substitution_status = substitution_status
        seg.needs_human_review = needs_human_review
        seg.actual_strength = actual_strength
        seg.dispense_package_size = dispense_package_size
        seg.dispense_package_method = dispense_package_method
        seg.actual_drug_strength_volume = actual_drug_strength_volume
        seg.pharmacy_order_type = pharmacy_order_type

        result = seg.to_dict()

        assert result["_segment_id"] == "RXD"
        assert result["dispense_sub_id_counter"] == dispense_sub_id_counter
        assert result["date_time_dispensed"] == date_time_dispensed
        assert result["actual_dispense_amount"] == actual_dispense_amount
        assert result["prescription_number"] == prescription_number
        assert result["number_of_refills_remaining"] == number_of_refills_remaining
        assert result["substitution_status"] == substitution_status
        assert result["needs_human_review"] == needs_human_review
        assert result["actual_strength"] == actual_strength
        assert result["dispense_package_size"] == dispense_package_size
        assert result["dispense_package_method"] == dispense_package_method
        assert result["actual_drug_strength_volume"] == actual_drug_strength_volume
        assert result["pharmacy_order_type"] == pharmacy_order_type

    def test_rxd_to_json(self):
        seg = RXD()

        seg.dispense_sub_id_counter = dispense_sub_id_counter
        seg.date_time_dispensed = date_time_dispensed
        seg.actual_dispense_amount = actual_dispense_amount
        seg.prescription_number = prescription_number
        seg.number_of_refills_remaining = number_of_refills_remaining
        seg.substitution_status = substitution_status
        seg.needs_human_review = needs_human_review
        seg.actual_strength = actual_strength
        seg.dispense_package_size = dispense_package_size
        seg.dispense_package_method = dispense_package_method
        seg.actual_drug_strength_volume = actual_drug_strength_volume
        seg.pharmacy_order_type = pharmacy_order_type

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "RXD"
        assert result["dispense_sub_id_counter"] == dispense_sub_id_counter
        assert result["date_time_dispensed"] == date_time_dispensed
        assert result["actual_dispense_amount"] == actual_dispense_amount
        assert result["prescription_number"] == prescription_number
        assert result["number_of_refills_remaining"] == number_of_refills_remaining
        assert result["substitution_status"] == substitution_status
        assert result["needs_human_review"] == needs_human_review
        assert result["actual_strength"] == actual_strength
        assert result["dispense_package_size"] == dispense_package_size
        assert result["dispense_package_method"] == dispense_package_method
        assert result["actual_drug_strength_volume"] == actual_drug_strength_volume
        assert result["pharmacy_order_type"] == pharmacy_order_type
