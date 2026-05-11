from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import RQ1


anticipated_price = "test_anticipated_price"
manufacturers_catalog = "test_manufacturers_catalo"
vendor_catalog = "test_vendor_catalog"
taxable = "test_taxable"
substitute_allowed = "test_substitute_allowed"


class TestRQ1:
    """Comprehensive tests for RQ1 segment."""

    def test_rq1_build_and_verify(self):
        seg = RQ1()

        seg.anticipated_price = anticipated_price
        seg.manufacturers_catalog = manufacturers_catalog
        seg.vendor_catalog = vendor_catalog
        seg.taxable = taxable
        seg.substitute_allowed = substitute_allowed

        assert seg.anticipated_price == anticipated_price
        assert seg.manufacturers_catalog == manufacturers_catalog
        assert seg.vendor_catalog == vendor_catalog
        assert seg.taxable == taxable
        assert seg.substitute_allowed == substitute_allowed

    def test_rq1_to_dict(self):
        seg = RQ1()

        seg.anticipated_price = anticipated_price
        seg.manufacturers_catalog = manufacturers_catalog
        seg.vendor_catalog = vendor_catalog
        seg.taxable = taxable
        seg.substitute_allowed = substitute_allowed

        result = seg.to_dict()

        assert result["_segment_id"] == "RQ1"
        assert result["anticipated_price"] == anticipated_price
        assert result["manufacturers_catalog"] == manufacturers_catalog
        assert result["vendor_catalog"] == vendor_catalog
        assert result["taxable"] == taxable
        assert result["substitute_allowed"] == substitute_allowed

    def test_rq1_to_json(self):
        seg = RQ1()

        seg.anticipated_price = anticipated_price
        seg.manufacturers_catalog = manufacturers_catalog
        seg.vendor_catalog = vendor_catalog
        seg.taxable = taxable
        seg.substitute_allowed = substitute_allowed

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "RQ1"
        assert result["anticipated_price"] == anticipated_price
        assert result["manufacturers_catalog"] == manufacturers_catalog
        assert result["vendor_catalog"] == vendor_catalog
        assert result["taxable"] == taxable
        assert result["substitute_allowed"] == substitute_allowed
