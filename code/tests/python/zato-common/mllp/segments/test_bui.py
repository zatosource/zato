from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import BUI


set_id_bui = "test_set_id_bui"
blood_unit_weight = "test_blood_unit_weight"
blood_unit_volume = "test_blood_unit_volume"
container_catalog_number = "test_container_catalog_nu"
container_lot_number = "test_container_lot_number"
action_code = "test_action_code"


class TestBUI:
    """Comprehensive tests for BUI segment."""

    def test_bui_build_and_verify(self):
        seg = BUI()

        seg.set_id_bui = set_id_bui
        seg.blood_unit_weight = blood_unit_weight
        seg.blood_unit_volume = blood_unit_volume
        seg.container_catalog_number = container_catalog_number
        seg.container_lot_number = container_lot_number
        seg.action_code = action_code

        assert seg.set_id_bui == set_id_bui
        assert seg.blood_unit_weight == blood_unit_weight
        assert seg.blood_unit_volume == blood_unit_volume
        assert seg.container_catalog_number == container_catalog_number
        assert seg.container_lot_number == container_lot_number
        assert seg.action_code == action_code

    def test_bui_to_dict(self):
        seg = BUI()

        seg.set_id_bui = set_id_bui
        seg.blood_unit_weight = blood_unit_weight
        seg.blood_unit_volume = blood_unit_volume
        seg.container_catalog_number = container_catalog_number
        seg.container_lot_number = container_lot_number
        seg.action_code = action_code

        result = seg.to_dict()

        assert result["_segment_id"] == "BUI"
        assert result["set_id_bui"] == set_id_bui
        assert result["blood_unit_weight"] == blood_unit_weight
        assert result["blood_unit_volume"] == blood_unit_volume
        assert result["container_catalog_number"] == container_catalog_number
        assert result["container_lot_number"] == container_lot_number
        assert result["action_code"] == action_code

    def test_bui_to_json(self):
        seg = BUI()

        seg.set_id_bui = set_id_bui
        seg.blood_unit_weight = blood_unit_weight
        seg.blood_unit_volume = blood_unit_volume
        seg.container_catalog_number = container_catalog_number
        seg.container_lot_number = container_lot_number
        seg.action_code = action_code

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "BUI"
        assert result["set_id_bui"] == set_id_bui
        assert result["blood_unit_weight"] == blood_unit_weight
        assert result["blood_unit_volume"] == blood_unit_volume
        assert result["container_catalog_number"] == container_catalog_number
        assert result["container_lot_number"] == container_lot_number
        assert result["action_code"] == action_code
