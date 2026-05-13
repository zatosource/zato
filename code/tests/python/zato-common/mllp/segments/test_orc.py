from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import ORC


order_control = "test_order_control"
order_status = "test_order_status"
response_flag = "test_response_flag"
date_time_of_order_event = "test_date_time_of_order_e"
order_effective_date_time = "test_order_effective_date"
fillers_expected_availability_date_time = "test_fillers_expected_ava"
advanced_beneficiary_notice_date = "test_advanced_beneficiary"
action_code = "test_action_code"
order_creation_date_time = "test_order_creation_date_"


class TestORC:
    """Comprehensive tests for ORC segment."""

    def test_orc_build_and_verify(self):
        seg = ORC()

        seg.order_control = order_control
        seg.order_status = order_status
        seg.response_flag = response_flag
        seg.date_time_of_order_event = date_time_of_order_event
        seg.order_effective_date_time = order_effective_date_time
        seg.fillers_expected_availability_date_time = fillers_expected_availability_date_time
        seg.advanced_beneficiary_notice_date = advanced_beneficiary_notice_date
        seg.action_code = action_code
        seg.order_creation_date_time = order_creation_date_time

        assert seg.order_control == order_control
        assert seg.order_status == order_status
        assert seg.response_flag == response_flag
        assert seg.date_time_of_order_event == date_time_of_order_event
        assert seg.order_effective_date_time == order_effective_date_time
        assert seg.fillers_expected_availability_date_time == fillers_expected_availability_date_time
        assert seg.advanced_beneficiary_notice_date == advanced_beneficiary_notice_date
        assert seg.action_code == action_code
        assert seg.order_creation_date_time == order_creation_date_time

    def test_orc_to_dict(self):
        seg = ORC()

        seg.order_control = order_control
        seg.order_status = order_status
        seg.response_flag = response_flag
        seg.date_time_of_order_event = date_time_of_order_event
        seg.order_effective_date_time = order_effective_date_time
        seg.fillers_expected_availability_date_time = fillers_expected_availability_date_time
        seg.advanced_beneficiary_notice_date = advanced_beneficiary_notice_date
        seg.action_code = action_code
        seg.order_creation_date_time = order_creation_date_time

        result = seg.to_dict()

        assert result["_segment_id"] == "ORC"
        assert result["order_control"] == order_control
        assert result["order_status"] == order_status
        assert result["response_flag"] == response_flag
        assert result["date_time_of_order_event"] == date_time_of_order_event
        assert result["order_effective_date_time"] == order_effective_date_time
        assert result["fillers_expected_availability_date_time"] == fillers_expected_availability_date_time
        assert result["advanced_beneficiary_notice_date"] == advanced_beneficiary_notice_date
        assert result["action_code"] == action_code
        assert result["order_creation_date_time"] == order_creation_date_time

    def test_orc_to_json(self):
        seg = ORC()

        seg.order_control = order_control
        seg.order_status = order_status
        seg.response_flag = response_flag
        seg.date_time_of_order_event = date_time_of_order_event
        seg.order_effective_date_time = order_effective_date_time
        seg.fillers_expected_availability_date_time = fillers_expected_availability_date_time
        seg.advanced_beneficiary_notice_date = advanced_beneficiary_notice_date
        seg.action_code = action_code
        seg.order_creation_date_time = order_creation_date_time

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "ORC"
        assert result["order_control"] == order_control
        assert result["order_status"] == order_status
        assert result["response_flag"] == response_flag
        assert result["date_time_of_order_event"] == date_time_of_order_event
        assert result["order_effective_date_time"] == order_effective_date_time
        assert result["fillers_expected_availability_date_time"] == fillers_expected_availability_date_time
        assert result["advanced_beneficiary_notice_date"] == advanced_beneficiary_notice_date
        assert result["action_code"] == action_code
        assert result["order_creation_date_time"] == order_creation_date_time
