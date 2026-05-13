from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import PCR


generic_product = "test_generic_product"
product_manufacture_date = "test_product_manufacture_"
product_expiration_date = "test_product_expiration_d"
product_implantation_date = "test_product_implantation"
product_explantation_date = "test_product_explantation"
product_serial_lot_number = "test_product_serial_lot_n"
evaluated_product_source = "test_evaluated_product_so"
date_product_returned_to_manufacturer = "test_date_product_returne"
device_operator_qualifications = "test_device_operator_qual"
relatedness_assessment = "test_relatedness_assessme"
action_taken_in_response_to_the_event = "test_action_taken_in_resp"
event_causality_observations = "test_event_causality_obse"
indirect_exposure_mechanism = "test_indirect_exposure_me"


class TestPCR:
    """Comprehensive tests for PCR segment."""

    def test_pcr_build_and_verify(self):
        seg = PCR()

        seg.generic_product = generic_product
        seg.product_manufacture_date = product_manufacture_date
        seg.product_expiration_date = product_expiration_date
        seg.product_implantation_date = product_implantation_date
        seg.product_explantation_date = product_explantation_date
        seg.product_serial_lot_number = product_serial_lot_number
        seg.evaluated_product_source = evaluated_product_source
        seg.date_product_returned_to_manufacturer = date_product_returned_to_manufacturer
        seg.device_operator_qualifications = device_operator_qualifications
        seg.relatedness_assessment = relatedness_assessment
        seg.action_taken_in_response_to_the_event = action_taken_in_response_to_the_event
        seg.event_causality_observations = event_causality_observations
        seg.indirect_exposure_mechanism = indirect_exposure_mechanism

        assert seg.generic_product == generic_product
        assert seg.product_manufacture_date == product_manufacture_date
        assert seg.product_expiration_date == product_expiration_date
        assert seg.product_implantation_date == product_implantation_date
        assert seg.product_explantation_date == product_explantation_date
        assert seg.product_serial_lot_number == product_serial_lot_number
        assert seg.evaluated_product_source == evaluated_product_source
        assert seg.date_product_returned_to_manufacturer == date_product_returned_to_manufacturer
        assert seg.device_operator_qualifications == device_operator_qualifications
        assert seg.relatedness_assessment == relatedness_assessment
        assert seg.action_taken_in_response_to_the_event == action_taken_in_response_to_the_event
        assert seg.event_causality_observations == event_causality_observations
        assert seg.indirect_exposure_mechanism == indirect_exposure_mechanism

    def test_pcr_to_dict(self):
        seg = PCR()

        seg.generic_product = generic_product
        seg.product_manufacture_date = product_manufacture_date
        seg.product_expiration_date = product_expiration_date
        seg.product_implantation_date = product_implantation_date
        seg.product_explantation_date = product_explantation_date
        seg.product_serial_lot_number = product_serial_lot_number
        seg.evaluated_product_source = evaluated_product_source
        seg.date_product_returned_to_manufacturer = date_product_returned_to_manufacturer
        seg.device_operator_qualifications = device_operator_qualifications
        seg.relatedness_assessment = relatedness_assessment
        seg.action_taken_in_response_to_the_event = action_taken_in_response_to_the_event
        seg.event_causality_observations = event_causality_observations
        seg.indirect_exposure_mechanism = indirect_exposure_mechanism

        result = seg.to_dict()

        assert result["_segment_id"] == "PCR"
        assert result["generic_product"] == generic_product
        assert result["product_manufacture_date"] == product_manufacture_date
        assert result["product_expiration_date"] == product_expiration_date
        assert result["product_implantation_date"] == product_implantation_date
        assert result["product_explantation_date"] == product_explantation_date
        assert result["product_serial_lot_number"] == product_serial_lot_number
        assert result["evaluated_product_source"] == evaluated_product_source
        assert result["date_product_returned_to_manufacturer"] == date_product_returned_to_manufacturer
        assert result["device_operator_qualifications"] == device_operator_qualifications
        assert result["relatedness_assessment"] == relatedness_assessment
        assert result["action_taken_in_response_to_the_event"] == action_taken_in_response_to_the_event
        assert result["event_causality_observations"] == event_causality_observations
        assert result["indirect_exposure_mechanism"] == indirect_exposure_mechanism

    def test_pcr_to_json(self):
        seg = PCR()

        seg.generic_product = generic_product
        seg.product_manufacture_date = product_manufacture_date
        seg.product_expiration_date = product_expiration_date
        seg.product_implantation_date = product_implantation_date
        seg.product_explantation_date = product_explantation_date
        seg.product_serial_lot_number = product_serial_lot_number
        seg.evaluated_product_source = evaluated_product_source
        seg.date_product_returned_to_manufacturer = date_product_returned_to_manufacturer
        seg.device_operator_qualifications = device_operator_qualifications
        seg.relatedness_assessment = relatedness_assessment
        seg.action_taken_in_response_to_the_event = action_taken_in_response_to_the_event
        seg.event_causality_observations = event_causality_observations
        seg.indirect_exposure_mechanism = indirect_exposure_mechanism

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "PCR"
        assert result["generic_product"] == generic_product
        assert result["product_manufacture_date"] == product_manufacture_date
        assert result["product_expiration_date"] == product_expiration_date
        assert result["product_implantation_date"] == product_implantation_date
        assert result["product_explantation_date"] == product_explantation_date
        assert result["product_serial_lot_number"] == product_serial_lot_number
        assert result["evaluated_product_source"] == evaluated_product_source
        assert result["date_product_returned_to_manufacturer"] == date_product_returned_to_manufacturer
        assert result["device_operator_qualifications"] == device_operator_qualifications
        assert result["relatedness_assessment"] == relatedness_assessment
        assert result["action_taken_in_response_to_the_event"] == action_taken_in_response_to_the_event
        assert result["event_causality_observations"] == event_causality_observations
        assert result["indirect_exposure_mechanism"] == indirect_exposure_mechanism
