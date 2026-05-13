from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import ILT


set_id_ilt = "test_set_id_ilt"
inventory_lot_number = "test_inventory_lot_number"
inventory_expiration_date = "test_inventory_expiration"
inventory_received_date = "test_inventory_received_d"
inventory_received_quantity = "test_inventory_received_q"
inventory_on_hand_date = "test_inventory_on_hand_da"
inventory_on_hand_quantity = "test_inventory_on_hand_qu"


class TestILT:
    """Comprehensive tests for ILT segment."""

    def test_ilt_build_and_verify(self):
        seg = ILT()

        seg.set_id_ilt = set_id_ilt
        seg.inventory_lot_number = inventory_lot_number
        seg.inventory_expiration_date = inventory_expiration_date
        seg.inventory_received_date = inventory_received_date
        seg.inventory_received_quantity = inventory_received_quantity
        seg.inventory_on_hand_date = inventory_on_hand_date
        seg.inventory_on_hand_quantity = inventory_on_hand_quantity

        assert seg.set_id_ilt == set_id_ilt
        assert seg.inventory_lot_number == inventory_lot_number
        assert seg.inventory_expiration_date == inventory_expiration_date
        assert seg.inventory_received_date == inventory_received_date
        assert seg.inventory_received_quantity == inventory_received_quantity
        assert seg.inventory_on_hand_date == inventory_on_hand_date
        assert seg.inventory_on_hand_quantity == inventory_on_hand_quantity

    def test_ilt_to_dict(self):
        seg = ILT()

        seg.set_id_ilt = set_id_ilt
        seg.inventory_lot_number = inventory_lot_number
        seg.inventory_expiration_date = inventory_expiration_date
        seg.inventory_received_date = inventory_received_date
        seg.inventory_received_quantity = inventory_received_quantity
        seg.inventory_on_hand_date = inventory_on_hand_date
        seg.inventory_on_hand_quantity = inventory_on_hand_quantity

        result = seg.to_dict()

        assert result["_segment_id"] == "ILT"
        assert result["set_id_ilt"] == set_id_ilt
        assert result["inventory_lot_number"] == inventory_lot_number
        assert result["inventory_expiration_date"] == inventory_expiration_date
        assert result["inventory_received_date"] == inventory_received_date
        assert result["inventory_received_quantity"] == inventory_received_quantity
        assert result["inventory_on_hand_date"] == inventory_on_hand_date
        assert result["inventory_on_hand_quantity"] == inventory_on_hand_quantity

    def test_ilt_to_json(self):
        seg = ILT()

        seg.set_id_ilt = set_id_ilt
        seg.inventory_lot_number = inventory_lot_number
        seg.inventory_expiration_date = inventory_expiration_date
        seg.inventory_received_date = inventory_received_date
        seg.inventory_received_quantity = inventory_received_quantity
        seg.inventory_on_hand_date = inventory_on_hand_date
        seg.inventory_on_hand_quantity = inventory_on_hand_quantity

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "ILT"
        assert result["set_id_ilt"] == set_id_ilt
        assert result["inventory_lot_number"] == inventory_lot_number
        assert result["inventory_expiration_date"] == inventory_expiration_date
        assert result["inventory_received_date"] == inventory_received_date
        assert result["inventory_received_quantity"] == inventory_received_quantity
        assert result["inventory_on_hand_date"] == inventory_on_hand_date
        assert result["inventory_on_hand_quantity"] == inventory_on_hand_quantity
