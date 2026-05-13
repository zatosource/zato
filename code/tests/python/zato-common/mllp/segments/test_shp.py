from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import SHP


shipment_status_date_time = "test_shipment_status_date"
shipment_status_reason = "test_shipment_status_reas"
number_of_packages_in_shipment = "test_number_of_packages_i"
action_code = "test_action_code"


class TestSHP:
    """Comprehensive tests for SHP segment."""

    def test_shp_build_and_verify(self):
        seg = SHP()

        seg.shipment_status_date_time = shipment_status_date_time
        seg.shipment_status_reason = shipment_status_reason
        seg.number_of_packages_in_shipment = number_of_packages_in_shipment
        seg.action_code = action_code

        assert seg.shipment_status_date_time == shipment_status_date_time
        assert seg.shipment_status_reason == shipment_status_reason
        assert seg.number_of_packages_in_shipment == number_of_packages_in_shipment
        assert seg.action_code == action_code

    def test_shp_to_dict(self):
        seg = SHP()

        seg.shipment_status_date_time = shipment_status_date_time
        seg.shipment_status_reason = shipment_status_reason
        seg.number_of_packages_in_shipment = number_of_packages_in_shipment
        seg.action_code = action_code

        result = seg.to_dict()

        assert result["_segment_id"] == "SHP"
        assert result["shipment_status_date_time"] == shipment_status_date_time
        assert result["shipment_status_reason"] == shipment_status_reason
        assert result["number_of_packages_in_shipment"] == number_of_packages_in_shipment
        assert result["action_code"] == action_code

    def test_shp_to_json(self):
        seg = SHP()

        seg.shipment_status_date_time = shipment_status_date_time
        seg.shipment_status_reason = shipment_status_reason
        seg.number_of_packages_in_shipment = number_of_packages_in_shipment
        seg.action_code = action_code

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "SHP"
        assert result["shipment_status_date_time"] == shipment_status_date_time
        assert result["shipment_status_reason"] == shipment_status_reason
        assert result["number_of_packages_in_shipment"] == number_of_packages_in_shipment
        assert result["action_code"] == action_code
