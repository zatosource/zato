from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import BPX


set_id_bpx = "test_set_id_bpx"
bp_status = "test_bp_status"
bp_date_time_of_status = "test_bp_date_time_of_stat"
bp_expiration_date_time = "test_bp_expiration_date_t"
bp_quantity = "test_bp_quantity"
bp_amount = "test_bp_amount"
action_code = "test_action_code"


class TestBPX:
    """Comprehensive tests for BPX segment."""

    def test_bpx_build_and_verify(self):
        seg = BPX()

        seg.set_id_bpx = set_id_bpx
        seg.bp_status = bp_status
        seg.bp_date_time_of_status = bp_date_time_of_status
        seg.bp_expiration_date_time = bp_expiration_date_time
        seg.bp_quantity = bp_quantity
        seg.bp_amount = bp_amount
        seg.action_code = action_code

        assert seg.set_id_bpx == set_id_bpx
        assert seg.bp_status == bp_status
        assert seg.bp_date_time_of_status == bp_date_time_of_status
        assert seg.bp_expiration_date_time == bp_expiration_date_time
        assert seg.bp_quantity == bp_quantity
        assert seg.bp_amount == bp_amount
        assert seg.action_code == action_code

    def test_bpx_to_dict(self):
        seg = BPX()

        seg.set_id_bpx = set_id_bpx
        seg.bp_status = bp_status
        seg.bp_date_time_of_status = bp_date_time_of_status
        seg.bp_expiration_date_time = bp_expiration_date_time
        seg.bp_quantity = bp_quantity
        seg.bp_amount = bp_amount
        seg.action_code = action_code

        result = seg.to_dict()

        assert result["_segment_id"] == "BPX"
        assert result["set_id_bpx"] == set_id_bpx
        assert result["bp_status"] == bp_status
        assert result["bp_date_time_of_status"] == bp_date_time_of_status
        assert result["bp_expiration_date_time"] == bp_expiration_date_time
        assert result["bp_quantity"] == bp_quantity
        assert result["bp_amount"] == bp_amount
        assert result["action_code"] == action_code

    def test_bpx_to_json(self):
        seg = BPX()

        seg.set_id_bpx = set_id_bpx
        seg.bp_status = bp_status
        seg.bp_date_time_of_status = bp_date_time_of_status
        seg.bp_expiration_date_time = bp_expiration_date_time
        seg.bp_quantity = bp_quantity
        seg.bp_amount = bp_amount
        seg.action_code = action_code

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "BPX"
        assert result["set_id_bpx"] == set_id_bpx
        assert result["bp_status"] == bp_status
        assert result["bp_date_time_of_status"] == bp_date_time_of_status
        assert result["bp_expiration_date_time"] == bp_expiration_date_time
        assert result["bp_quantity"] == bp_quantity
        assert result["bp_amount"] == bp_amount
        assert result["action_code"] == action_code
