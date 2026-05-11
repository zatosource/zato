from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import BPO


set_id_bpo = "test_set_id_bpo"
bp_quantity = "test_bp_quantity"
bp_amount = "test_bp_amount"
bp_intended_use_date_time = "test_bp_intended_use_date"
bp_requested_dispense_date_time = "test_bp_requested_dispens"
bp_informed_consent_indicator = "test_bp_informed_consent_"


class TestBPO:
    """Comprehensive tests for BPO segment."""

    def test_bpo_build_and_verify(self):
        seg = BPO()

        seg.set_id_bpo = set_id_bpo
        seg.bp_quantity = bp_quantity
        seg.bp_amount = bp_amount
        seg.bp_intended_use_date_time = bp_intended_use_date_time
        seg.bp_requested_dispense_date_time = bp_requested_dispense_date_time
        seg.bp_informed_consent_indicator = bp_informed_consent_indicator

        assert seg.set_id_bpo == set_id_bpo
        assert seg.bp_quantity == bp_quantity
        assert seg.bp_amount == bp_amount
        assert seg.bp_intended_use_date_time == bp_intended_use_date_time
        assert seg.bp_requested_dispense_date_time == bp_requested_dispense_date_time
        assert seg.bp_informed_consent_indicator == bp_informed_consent_indicator

    def test_bpo_to_dict(self):
        seg = BPO()

        seg.set_id_bpo = set_id_bpo
        seg.bp_quantity = bp_quantity
        seg.bp_amount = bp_amount
        seg.bp_intended_use_date_time = bp_intended_use_date_time
        seg.bp_requested_dispense_date_time = bp_requested_dispense_date_time
        seg.bp_informed_consent_indicator = bp_informed_consent_indicator

        result = seg.to_dict()

        assert result["_segment_id"] == "BPO"
        assert result["set_id_bpo"] == set_id_bpo
        assert result["bp_quantity"] == bp_quantity
        assert result["bp_amount"] == bp_amount
        assert result["bp_intended_use_date_time"] == bp_intended_use_date_time
        assert result["bp_requested_dispense_date_time"] == bp_requested_dispense_date_time
        assert result["bp_informed_consent_indicator"] == bp_informed_consent_indicator

    def test_bpo_to_json(self):
        seg = BPO()

        seg.set_id_bpo = set_id_bpo
        seg.bp_quantity = bp_quantity
        seg.bp_amount = bp_amount
        seg.bp_intended_use_date_time = bp_intended_use_date_time
        seg.bp_requested_dispense_date_time = bp_requested_dispense_date_time
        seg.bp_informed_consent_indicator = bp_informed_consent_indicator

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "BPO"
        assert result["set_id_bpo"] == set_id_bpo
        assert result["bp_quantity"] == bp_quantity
        assert result["bp_amount"] == bp_amount
        assert result["bp_intended_use_date_time"] == bp_intended_use_date_time
        assert result["bp_requested_dispense_date_time"] == bp_requested_dispense_date_time
        assert result["bp_informed_consent_indicator"] == bp_informed_consent_indicator
