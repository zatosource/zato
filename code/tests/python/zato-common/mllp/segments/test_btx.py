from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import BTX


set_id_btx = "test_set_id_btx"
bp_quantity = "test_bp_quantity"
bp_amount = "test_bp_amount"
bp_message_status = "test_bp_message_status"
bp_date_time_of_status = "test_bp_date_time_of_stat"
bp_transfusion_start_date_time_of_status = "test_bp_transfusion_start"
bp_transfusion_end_date_time_of_status = "test_bp_transfusion_end_d"
action_code = "test_action_code"


class TestBTX:
    """Comprehensive tests for BTX segment."""

    def test_btx_build_and_verify(self):
        seg = BTX()

        seg.set_id_btx = set_id_btx
        seg.bp_quantity = bp_quantity
        seg.bp_amount = bp_amount
        seg.bp_message_status = bp_message_status
        seg.bp_date_time_of_status = bp_date_time_of_status
        seg.bp_transfusion_start_date_time_of_status = bp_transfusion_start_date_time_of_status
        seg.bp_transfusion_end_date_time_of_status = bp_transfusion_end_date_time_of_status
        seg.action_code = action_code

        assert seg.set_id_btx == set_id_btx
        assert seg.bp_quantity == bp_quantity
        assert seg.bp_amount == bp_amount
        assert seg.bp_message_status == bp_message_status
        assert seg.bp_date_time_of_status == bp_date_time_of_status
        assert seg.bp_transfusion_start_date_time_of_status == bp_transfusion_start_date_time_of_status
        assert seg.bp_transfusion_end_date_time_of_status == bp_transfusion_end_date_time_of_status
        assert seg.action_code == action_code

    def test_btx_to_dict(self):
        seg = BTX()

        seg.set_id_btx = set_id_btx
        seg.bp_quantity = bp_quantity
        seg.bp_amount = bp_amount
        seg.bp_message_status = bp_message_status
        seg.bp_date_time_of_status = bp_date_time_of_status
        seg.bp_transfusion_start_date_time_of_status = bp_transfusion_start_date_time_of_status
        seg.bp_transfusion_end_date_time_of_status = bp_transfusion_end_date_time_of_status
        seg.action_code = action_code

        result = seg.to_dict()

        assert result["_segment_id"] == "BTX"
        assert result["set_id_btx"] == set_id_btx
        assert result["bp_quantity"] == bp_quantity
        assert result["bp_amount"] == bp_amount
        assert result["bp_message_status"] == bp_message_status
        assert result["bp_date_time_of_status"] == bp_date_time_of_status
        assert result["bp_transfusion_start_date_time_of_status"] == bp_transfusion_start_date_time_of_status
        assert result["bp_transfusion_end_date_time_of_status"] == bp_transfusion_end_date_time_of_status
        assert result["action_code"] == action_code

    def test_btx_to_json(self):
        seg = BTX()

        seg.set_id_btx = set_id_btx
        seg.bp_quantity = bp_quantity
        seg.bp_amount = bp_amount
        seg.bp_message_status = bp_message_status
        seg.bp_date_time_of_status = bp_date_time_of_status
        seg.bp_transfusion_start_date_time_of_status = bp_transfusion_start_date_time_of_status
        seg.bp_transfusion_end_date_time_of_status = bp_transfusion_end_date_time_of_status
        seg.action_code = action_code

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "BTX"
        assert result["set_id_btx"] == set_id_btx
        assert result["bp_quantity"] == bp_quantity
        assert result["bp_amount"] == bp_amount
        assert result["bp_message_status"] == bp_message_status
        assert result["bp_date_time_of_status"] == bp_date_time_of_status
        assert result["bp_transfusion_start_date_time_of_status"] == bp_transfusion_start_date_time_of_status
        assert result["bp_transfusion_end_date_time_of_status"] == bp_transfusion_end_date_time_of_status
        assert result["action_code"] == action_code
