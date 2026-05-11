from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import ITM


item_description = "test_item_description"
manufacturer_name = "test_manufacturer_name"
manufacturer_catalog_number = "test_manufacturer_catalog"
approved_to_buy_quantity = "test_approved_to_buy_quan"
class_of_trade = "test_class_of_trade"
field_level_event_code = "test_field_level_event_co"


class TestITM:
    """Comprehensive tests for ITM segment."""

    def test_itm_build_and_verify(self):
        seg = ITM()

        seg.item_description = item_description
        seg.manufacturer_name = manufacturer_name
        seg.manufacturer_catalog_number = manufacturer_catalog_number
        seg.approved_to_buy_quantity = approved_to_buy_quantity
        seg.class_of_trade = class_of_trade
        seg.field_level_event_code = field_level_event_code

        assert seg.item_description == item_description
        assert seg.manufacturer_name == manufacturer_name
        assert seg.manufacturer_catalog_number == manufacturer_catalog_number
        assert seg.approved_to_buy_quantity == approved_to_buy_quantity
        assert seg.class_of_trade == class_of_trade
        assert seg.field_level_event_code == field_level_event_code

    def test_itm_to_dict(self):
        seg = ITM()

        seg.item_description = item_description
        seg.manufacturer_name = manufacturer_name
        seg.manufacturer_catalog_number = manufacturer_catalog_number
        seg.approved_to_buy_quantity = approved_to_buy_quantity
        seg.class_of_trade = class_of_trade
        seg.field_level_event_code = field_level_event_code

        result = seg.to_dict()

        assert result["_segment_id"] == "ITM"
        assert result["item_description"] == item_description
        assert result["manufacturer_name"] == manufacturer_name
        assert result["manufacturer_catalog_number"] == manufacturer_catalog_number
        assert result["approved_to_buy_quantity"] == approved_to_buy_quantity
        assert result["class_of_trade"] == class_of_trade
        assert result["field_level_event_code"] == field_level_event_code

    def test_itm_to_json(self):
        seg = ITM()

        seg.item_description = item_description
        seg.manufacturer_name = manufacturer_name
        seg.manufacturer_catalog_number = manufacturer_catalog_number
        seg.approved_to_buy_quantity = approved_to_buy_quantity
        seg.class_of_trade = class_of_trade
        seg.field_level_event_code = field_level_event_code

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "ITM"
        assert result["item_description"] == item_description
        assert result["manufacturer_name"] == manufacturer_name
        assert result["manufacturer_catalog_number"] == manufacturer_catalog_number
        assert result["approved_to_buy_quantity"] == approved_to_buy_quantity
        assert result["class_of_trade"] == class_of_trade
        assert result["field_level_event_code"] == field_level_event_code
