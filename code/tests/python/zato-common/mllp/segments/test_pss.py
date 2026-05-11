from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import PSS


product_service_section_sequence_number = "test_product_service_sect"
section_description_or_heading = "test_section_description_"


class TestPSS:
    """Comprehensive tests for PSS segment."""

    def test_pss_build_and_verify(self):
        seg = PSS()

        seg.product_service_section_sequence_number = product_service_section_sequence_number
        seg.section_description_or_heading = section_description_or_heading

        assert seg.product_service_section_sequence_number == product_service_section_sequence_number
        assert seg.section_description_or_heading == section_description_or_heading

    def test_pss_to_dict(self):
        seg = PSS()

        seg.product_service_section_sequence_number = product_service_section_sequence_number
        seg.section_description_or_heading = section_description_or_heading

        result = seg.to_dict()

        assert result["_segment_id"] == "PSS"
        assert result["product_service_section_sequence_number"] == product_service_section_sequence_number
        assert result["section_description_or_heading"] == section_description_or_heading

    def test_pss_to_json(self):
        seg = PSS()

        seg.product_service_section_sequence_number = product_service_section_sequence_number
        seg.section_description_or_heading = section_description_or_heading

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "PSS"
        assert result["product_service_section_sequence_number"] == product_service_section_sequence_number
        assert result["section_description_or_heading"] == section_description_or_heading
