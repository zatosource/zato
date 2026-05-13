from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import PRT


action_code = "test_action_code"
begin_date_time_arrival_time = "test_begin_date_time_arri"
end_date_time_departure_time = "test_end_date_time_depart"
device_manufacture_date = "test_device_manufacture_d"
device_expiry_date = "test_device_expiry_date"
device_lot_number = "test_device_lot_number"
device_serial_number = "test_device_serial_number"


class TestPRT:
    """Comprehensive tests for PRT segment."""

    def test_prt_build_and_verify(self):
        seg = PRT()

        seg.action_code = action_code
        seg.begin_date_time_arrival_time = begin_date_time_arrival_time
        seg.end_date_time_departure_time = end_date_time_departure_time
        seg.device_manufacture_date = device_manufacture_date
        seg.device_expiry_date = device_expiry_date
        seg.device_lot_number = device_lot_number
        seg.device_serial_number = device_serial_number

        assert seg.action_code == action_code
        assert seg.begin_date_time_arrival_time == begin_date_time_arrival_time
        assert seg.end_date_time_departure_time == end_date_time_departure_time
        assert seg.device_manufacture_date == device_manufacture_date
        assert seg.device_expiry_date == device_expiry_date
        assert seg.device_lot_number == device_lot_number
        assert seg.device_serial_number == device_serial_number

    def test_prt_to_dict(self):
        seg = PRT()

        seg.action_code = action_code
        seg.begin_date_time_arrival_time = begin_date_time_arrival_time
        seg.end_date_time_departure_time = end_date_time_departure_time
        seg.device_manufacture_date = device_manufacture_date
        seg.device_expiry_date = device_expiry_date
        seg.device_lot_number = device_lot_number
        seg.device_serial_number = device_serial_number

        result = seg.to_dict()

        assert result["_segment_id"] == "PRT"
        assert result["action_code"] == action_code
        assert result["begin_date_time_arrival_time"] == begin_date_time_arrival_time
        assert result["end_date_time_departure_time"] == end_date_time_departure_time
        assert result["device_manufacture_date"] == device_manufacture_date
        assert result["device_expiry_date"] == device_expiry_date
        assert result["device_lot_number"] == device_lot_number
        assert result["device_serial_number"] == device_serial_number

    def test_prt_to_json(self):
        seg = PRT()

        seg.action_code = action_code
        seg.begin_date_time_arrival_time = begin_date_time_arrival_time
        seg.end_date_time_departure_time = end_date_time_departure_time
        seg.device_manufacture_date = device_manufacture_date
        seg.device_expiry_date = device_expiry_date
        seg.device_lot_number = device_lot_number
        seg.device_serial_number = device_serial_number

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "PRT"
        assert result["action_code"] == action_code
        assert result["begin_date_time_arrival_time"] == begin_date_time_arrival_time
        assert result["end_date_time_departure_time"] == end_date_time_departure_time
        assert result["device_manufacture_date"] == device_manufacture_date
        assert result["device_expiry_date"] == device_expiry_date
        assert result["device_lot_number"] == device_lot_number
        assert result["device_serial_number"] == device_serial_number
