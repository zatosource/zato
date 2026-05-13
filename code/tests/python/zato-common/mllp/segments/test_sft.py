from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import SFT


software_certified_version_or_release_number = "test_software_certified_v"
software_product_name = "test_software_product_nam"
software_binary_id = "test_software_binary_id"
software_product_information = "test_software_product_inf"
software_install_date = "test_software_install_dat"


class TestSFT:
    """Comprehensive tests for SFT segment."""

    def test_sft_build_and_verify(self):
        seg = SFT()

        seg.software_certified_version_or_release_number = software_certified_version_or_release_number
        seg.software_product_name = software_product_name
        seg.software_binary_id = software_binary_id
        seg.software_product_information = software_product_information
        seg.software_install_date = software_install_date

        assert seg.software_certified_version_or_release_number == software_certified_version_or_release_number
        assert seg.software_product_name == software_product_name
        assert seg.software_binary_id == software_binary_id
        assert seg.software_product_information == software_product_information
        assert seg.software_install_date == software_install_date

    def test_sft_to_dict(self):
        seg = SFT()

        seg.software_certified_version_or_release_number = software_certified_version_or_release_number
        seg.software_product_name = software_product_name
        seg.software_binary_id = software_binary_id
        seg.software_product_information = software_product_information
        seg.software_install_date = software_install_date

        result = seg.to_dict()

        assert result["_segment_id"] == "SFT"
        assert result["software_certified_version_or_release_number"] == software_certified_version_or_release_number
        assert result["software_product_name"] == software_product_name
        assert result["software_binary_id"] == software_binary_id
        assert result["software_product_information"] == software_product_information
        assert result["software_install_date"] == software_install_date

    def test_sft_to_json(self):
        seg = SFT()

        seg.software_certified_version_or_release_number = software_certified_version_or_release_number
        seg.software_product_name = software_product_name
        seg.software_binary_id = software_binary_id
        seg.software_product_information = software_product_information
        seg.software_install_date = software_install_date

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "SFT"
        assert result["software_certified_version_or_release_number"] == software_certified_version_or_release_number
        assert result["software_product_name"] == software_product_name
        assert result["software_binary_id"] == software_binary_id
        assert result["software_product_information"] == software_product_information
        assert result["software_install_date"] == software_install_date
