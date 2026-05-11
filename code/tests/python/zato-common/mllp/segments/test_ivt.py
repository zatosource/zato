from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import IVT


set_id_ivt = "test_set_id_ivt"
inventory_location_name = "test_inventory_location_n"
source_location_name = "test_source_location_name"
recommended_safety_stock_days = "test_recommended_safety_s"
recommended_maximum_days_inventory = "test_recommended_maximum_"
recommended_order_point = "test_recommended_order_po"
recommended_order_amount = "test_recommended_order_am"


class TestIVT:
    """Comprehensive tests for IVT segment."""

    def test_ivt_build_and_verify(self):
        seg = IVT()

        seg.set_id_ivt = set_id_ivt
        seg.inventory_location_name = inventory_location_name
        seg.source_location_name = source_location_name
        seg.recommended_safety_stock_days = recommended_safety_stock_days
        seg.recommended_maximum_days_inventory = recommended_maximum_days_inventory
        seg.recommended_order_point = recommended_order_point
        seg.recommended_order_amount = recommended_order_amount

        assert seg.set_id_ivt == set_id_ivt
        assert seg.inventory_location_name == inventory_location_name
        assert seg.source_location_name == source_location_name
        assert seg.recommended_safety_stock_days == recommended_safety_stock_days
        assert seg.recommended_maximum_days_inventory == recommended_maximum_days_inventory
        assert seg.recommended_order_point == recommended_order_point
        assert seg.recommended_order_amount == recommended_order_amount

    def test_ivt_to_dict(self):
        seg = IVT()

        seg.set_id_ivt = set_id_ivt
        seg.inventory_location_name = inventory_location_name
        seg.source_location_name = source_location_name
        seg.recommended_safety_stock_days = recommended_safety_stock_days
        seg.recommended_maximum_days_inventory = recommended_maximum_days_inventory
        seg.recommended_order_point = recommended_order_point
        seg.recommended_order_amount = recommended_order_amount

        result = seg.to_dict()

        assert result["_segment_id"] == "IVT"
        assert result["set_id_ivt"] == set_id_ivt
        assert result["inventory_location_name"] == inventory_location_name
        assert result["source_location_name"] == source_location_name
        assert result["recommended_safety_stock_days"] == recommended_safety_stock_days
        assert result["recommended_maximum_days_inventory"] == recommended_maximum_days_inventory
        assert result["recommended_order_point"] == recommended_order_point
        assert result["recommended_order_amount"] == recommended_order_amount

    def test_ivt_to_json(self):
        seg = IVT()

        seg.set_id_ivt = set_id_ivt
        seg.inventory_location_name = inventory_location_name
        seg.source_location_name = source_location_name
        seg.recommended_safety_stock_days = recommended_safety_stock_days
        seg.recommended_maximum_days_inventory = recommended_maximum_days_inventory
        seg.recommended_order_point = recommended_order_point
        seg.recommended_order_amount = recommended_order_amount

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "IVT"
        assert result["set_id_ivt"] == set_id_ivt
        assert result["inventory_location_name"] == inventory_location_name
        assert result["source_location_name"] == source_location_name
        assert result["recommended_safety_stock_days"] == recommended_safety_stock_days
        assert result["recommended_maximum_days_inventory"] == recommended_maximum_days_inventory
        assert result["recommended_order_point"] == recommended_order_point
        assert result["recommended_order_amount"] == recommended_order_amount
