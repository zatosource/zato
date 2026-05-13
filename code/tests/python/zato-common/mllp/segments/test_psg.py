from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import PSG


product_service_group_sequence_number = "test_product_service_grou"
adjudicate_as_group = "test_adjudicate_as_group"
product_service_group_description = "test_product_service_grou"


class TestPSG:
    """Comprehensive tests for PSG segment."""

    def test_psg_build_and_verify(self):
        seg = PSG()

        seg.product_service_group_sequence_number = product_service_group_sequence_number
        seg.adjudicate_as_group = adjudicate_as_group
        seg.product_service_group_description = product_service_group_description

        assert seg.product_service_group_sequence_number == product_service_group_sequence_number
        assert seg.adjudicate_as_group == adjudicate_as_group
        assert seg.product_service_group_description == product_service_group_description

    def test_psg_to_dict(self):
        seg = PSG()

        seg.product_service_group_sequence_number = product_service_group_sequence_number
        seg.adjudicate_as_group = adjudicate_as_group
        seg.product_service_group_description = product_service_group_description

        result = seg.to_dict()

        assert result["_segment_id"] == "PSG"
        assert result["product_service_group_sequence_number"] == product_service_group_sequence_number
        assert result["adjudicate_as_group"] == adjudicate_as_group
        assert result["product_service_group_description"] == product_service_group_description

    def test_psg_to_json(self):
        seg = PSG()

        seg.product_service_group_sequence_number = product_service_group_sequence_number
        seg.adjudicate_as_group = adjudicate_as_group
        seg.product_service_group_description = product_service_group_description

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "PSG"
        assert result["product_service_group_sequence_number"] == product_service_group_sequence_number
        assert result["adjudicate_as_group"] == adjudicate_as_group
        assert result["product_service_group_description"] == product_service_group_description
