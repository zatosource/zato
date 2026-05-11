from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import IIM


inventory_lot_number = "test_inventory_lot_number"
inventory_expiration_date = "test_inventory_expiration"
inventory_received_date = "test_inventory_received_d"
inventory_received_quantity = "test_inventory_received_q"
inventory_on_hand_date = "test_inventory_on_hand_da"
inventory_on_hand_quantity = "test_inventory_on_hand_qu"


class TestIIM:
    """Comprehensive tests for IIM segment."""

    def test_iim_build_and_verify(self):
        seg = IIM()

        seg.inventory_lot_number = inventory_lot_number
        seg.inventory_expiration_date = inventory_expiration_date
        seg.inventory_received_date = inventory_received_date
        seg.inventory_received_quantity = inventory_received_quantity
        seg.inventory_on_hand_date = inventory_on_hand_date
        seg.inventory_on_hand_quantity = inventory_on_hand_quantity

        assert seg.inventory_lot_number == inventory_lot_number
        assert seg.inventory_expiration_date == inventory_expiration_date
        assert seg.inventory_received_date == inventory_received_date
        assert seg.inventory_received_quantity == inventory_received_quantity
        assert seg.inventory_on_hand_date == inventory_on_hand_date
        assert seg.inventory_on_hand_quantity == inventory_on_hand_quantity

    def test_iim_to_dict(self):
        seg = IIM()

        seg.inventory_lot_number = inventory_lot_number
        seg.inventory_expiration_date = inventory_expiration_date
        seg.inventory_received_date = inventory_received_date
        seg.inventory_received_quantity = inventory_received_quantity
        seg.inventory_on_hand_date = inventory_on_hand_date
        seg.inventory_on_hand_quantity = inventory_on_hand_quantity

        result = seg.to_dict()

        assert result["_segment_id"] == "IIM"
        assert result["inventory_lot_number"] == inventory_lot_number
        assert result["inventory_expiration_date"] == inventory_expiration_date
        assert result["inventory_received_date"] == inventory_received_date
        assert result["inventory_received_quantity"] == inventory_received_quantity
        assert result["inventory_on_hand_date"] == inventory_on_hand_date
        assert result["inventory_on_hand_quantity"] == inventory_on_hand_quantity

    def test_iim_to_json(self):
        seg = IIM()

        seg.inventory_lot_number = inventory_lot_number
        seg.inventory_expiration_date = inventory_expiration_date
        seg.inventory_received_date = inventory_received_date
        seg.inventory_received_quantity = inventory_received_quantity
        seg.inventory_on_hand_date = inventory_on_hand_date
        seg.inventory_on_hand_quantity = inventory_on_hand_quantity

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "IIM"
        assert result["inventory_lot_number"] == inventory_lot_number
        assert result["inventory_expiration_date"] == inventory_expiration_date
        assert result["inventory_received_date"] == inventory_received_date
        assert result["inventory_received_quantity"] == inventory_received_quantity
        assert result["inventory_on_hand_date"] == inventory_on_hand_date
        assert result["inventory_on_hand_quantity"] == inventory_on_hand_quantity
