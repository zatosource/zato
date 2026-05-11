from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import RXC


rx_component_type = "test_rx_component_type"
component_amount = "test_component_amount"
component_strength = "test_component_strength"
component_drug_strength_volume = "test_component_drug_stren"
dispense_amount = "test_dispense_amount"


class TestRXC:
    """Comprehensive tests for RXC segment."""

    def test_rxc_build_and_verify(self):
        seg = RXC()

        seg.rx_component_type = rx_component_type
        seg.component_amount = component_amount
        seg.component_strength = component_strength
        seg.component_drug_strength_volume = component_drug_strength_volume
        seg.dispense_amount = dispense_amount

        assert seg.rx_component_type == rx_component_type
        assert seg.component_amount == component_amount
        assert seg.component_strength == component_strength
        assert seg.component_drug_strength_volume == component_drug_strength_volume
        assert seg.dispense_amount == dispense_amount

    def test_rxc_to_dict(self):
        seg = RXC()

        seg.rx_component_type = rx_component_type
        seg.component_amount = component_amount
        seg.component_strength = component_strength
        seg.component_drug_strength_volume = component_drug_strength_volume
        seg.dispense_amount = dispense_amount

        result = seg.to_dict()

        assert result["_segment_id"] == "RXC"
        assert result["rx_component_type"] == rx_component_type
        assert result["component_amount"] == component_amount
        assert result["component_strength"] == component_strength
        assert result["component_drug_strength_volume"] == component_drug_strength_volume
        assert result["dispense_amount"] == dispense_amount

    def test_rxc_to_json(self):
        seg = RXC()

        seg.rx_component_type = rx_component_type
        seg.component_amount = component_amount
        seg.component_strength = component_strength
        seg.component_drug_strength_volume = component_drug_strength_volume
        seg.dispense_amount = dispense_amount

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "RXC"
        assert result["rx_component_type"] == rx_component_type
        assert result["component_amount"] == component_amount
        assert result["component_strength"] == component_strength
        assert result["component_drug_strength_volume"] == component_drug_strength_volume
        assert result["dispense_amount"] == dispense_amount
