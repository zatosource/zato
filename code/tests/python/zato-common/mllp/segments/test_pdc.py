from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import PDC


brand_name = "test_brand_name"
device_family_name = "test_device_family_name"
catalogue_identifier = "test_catalogue_identifier"
marketing_basis = "test_marketing_basis"
marketing_approval_id = "test_marketing_approval_i"
date_first_marketed = "test_date_first_marketed"
date_last_marketed = "test_date_last_marketed"


class TestPDC:
    """Comprehensive tests for PDC segment."""

    def test_pdc_build_and_verify(self):
        seg = PDC()

        seg.brand_name = brand_name
        seg.device_family_name = device_family_name
        seg.catalogue_identifier = catalogue_identifier
        seg.marketing_basis = marketing_basis
        seg.marketing_approval_id = marketing_approval_id
        seg.date_first_marketed = date_first_marketed
        seg.date_last_marketed = date_last_marketed

        assert seg.brand_name == brand_name
        assert seg.device_family_name == device_family_name
        assert seg.catalogue_identifier == catalogue_identifier
        assert seg.marketing_basis == marketing_basis
        assert seg.marketing_approval_id == marketing_approval_id
        assert seg.date_first_marketed == date_first_marketed
        assert seg.date_last_marketed == date_last_marketed

    def test_pdc_to_dict(self):
        seg = PDC()

        seg.brand_name = brand_name
        seg.device_family_name = device_family_name
        seg.catalogue_identifier = catalogue_identifier
        seg.marketing_basis = marketing_basis
        seg.marketing_approval_id = marketing_approval_id
        seg.date_first_marketed = date_first_marketed
        seg.date_last_marketed = date_last_marketed

        result = seg.to_dict()

        assert result["_segment_id"] == "PDC"
        assert result["brand_name"] == brand_name
        assert result["device_family_name"] == device_family_name
        assert result["catalogue_identifier"] == catalogue_identifier
        assert result["marketing_basis"] == marketing_basis
        assert result["marketing_approval_id"] == marketing_approval_id
        assert result["date_first_marketed"] == date_first_marketed
        assert result["date_last_marketed"] == date_last_marketed

    def test_pdc_to_json(self):
        seg = PDC()

        seg.brand_name = brand_name
        seg.device_family_name = device_family_name
        seg.catalogue_identifier = catalogue_identifier
        seg.marketing_basis = marketing_basis
        seg.marketing_approval_id = marketing_approval_id
        seg.date_first_marketed = date_first_marketed
        seg.date_last_marketed = date_last_marketed

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "PDC"
        assert result["brand_name"] == brand_name
        assert result["device_family_name"] == device_family_name
        assert result["catalogue_identifier"] == catalogue_identifier
        assert result["marketing_basis"] == marketing_basis
        assert result["marketing_approval_id"] == marketing_approval_id
        assert result["date_first_marketed"] == date_first_marketed
        assert result["date_last_marketed"] == date_last_marketed
