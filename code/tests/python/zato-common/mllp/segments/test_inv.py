from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import INV


initial_quantity = "test_initial_quantity"
current_quantity = "test_current_quantity"
available_quantity = "test_available_quantity"
consumption_quantity = "test_consumption_quantity"
expiration_date_time = "test_expiration_date_time"
first_used_date_time = "test_first_used_date_time"
manufacturer_lot_number = "test_manufacturer_lot_num"


class TestINV:
    """Comprehensive tests for INV segment."""

    def test_inv_build_and_verify(self):
        seg = INV()

        seg.initial_quantity = initial_quantity
        seg.current_quantity = current_quantity
        seg.available_quantity = available_quantity
        seg.consumption_quantity = consumption_quantity
        seg.expiration_date_time = expiration_date_time
        seg.first_used_date_time = first_used_date_time
        seg.manufacturer_lot_number = manufacturer_lot_number

        assert seg.initial_quantity == initial_quantity
        assert seg.current_quantity == current_quantity
        assert seg.available_quantity == available_quantity
        assert seg.consumption_quantity == consumption_quantity
        assert seg.expiration_date_time == expiration_date_time
        assert seg.first_used_date_time == first_used_date_time
        assert seg.manufacturer_lot_number == manufacturer_lot_number

    def test_inv_to_dict(self):
        seg = INV()

        seg.initial_quantity = initial_quantity
        seg.current_quantity = current_quantity
        seg.available_quantity = available_quantity
        seg.consumption_quantity = consumption_quantity
        seg.expiration_date_time = expiration_date_time
        seg.first_used_date_time = first_used_date_time
        seg.manufacturer_lot_number = manufacturer_lot_number

        result = seg.to_dict()

        assert result["_segment_id"] == "INV"
        assert result["initial_quantity"] == initial_quantity
        assert result["current_quantity"] == current_quantity
        assert result["available_quantity"] == available_quantity
        assert result["consumption_quantity"] == consumption_quantity
        assert result["expiration_date_time"] == expiration_date_time
        assert result["first_used_date_time"] == first_used_date_time
        assert result["manufacturer_lot_number"] == manufacturer_lot_number

    def test_inv_to_json(self):
        seg = INV()

        seg.initial_quantity = initial_quantity
        seg.current_quantity = current_quantity
        seg.available_quantity = available_quantity
        seg.consumption_quantity = consumption_quantity
        seg.expiration_date_time = expiration_date_time
        seg.first_used_date_time = first_used_date_time
        seg.manufacturer_lot_number = manufacturer_lot_number

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "INV"
        assert result["initial_quantity"] == initial_quantity
        assert result["current_quantity"] == current_quantity
        assert result["available_quantity"] == available_quantity
        assert result["consumption_quantity"] == consumption_quantity
        assert result["expiration_date_time"] == expiration_date_time
        assert result["first_used_date_time"] == first_used_date_time
        assert result["manufacturer_lot_number"] == manufacturer_lot_number
