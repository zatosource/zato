from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import PKG


set_id_pkg = "test_set_id_pkg"
package_quantity = "test_package_quantity"
future_item_price_effective_date = "test_future_item_price_ef"
quantity_of_each = "test_quantity_of_each"


class TestPKG:
    """Comprehensive tests for PKG segment."""

    def test_pkg_build_and_verify(self):
        seg = PKG()

        seg.set_id_pkg = set_id_pkg
        seg.package_quantity = package_quantity
        seg.future_item_price_effective_date = future_item_price_effective_date
        seg.quantity_of_each = quantity_of_each

        assert seg.set_id_pkg == set_id_pkg
        assert seg.package_quantity == package_quantity
        assert seg.future_item_price_effective_date == future_item_price_effective_date
        assert seg.quantity_of_each == quantity_of_each

    def test_pkg_to_dict(self):
        seg = PKG()

        seg.set_id_pkg = set_id_pkg
        seg.package_quantity = package_quantity
        seg.future_item_price_effective_date = future_item_price_effective_date
        seg.quantity_of_each = quantity_of_each

        result = seg.to_dict()

        assert result["_segment_id"] == "PKG"
        assert result["set_id_pkg"] == set_id_pkg
        assert result["package_quantity"] == package_quantity
        assert result["future_item_price_effective_date"] == future_item_price_effective_date
        assert result["quantity_of_each"] == quantity_of_each

    def test_pkg_to_json(self):
        seg = PKG()

        seg.set_id_pkg = set_id_pkg
        seg.package_quantity = package_quantity
        seg.future_item_price_effective_date = future_item_price_effective_date
        seg.quantity_of_each = quantity_of_each

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "PKG"
        assert result["set_id_pkg"] == set_id_pkg
        assert result["package_quantity"] == package_quantity
        assert result["future_item_price_effective_date"] == future_item_price_effective_date
        assert result["quantity_of_each"] == quantity_of_each
