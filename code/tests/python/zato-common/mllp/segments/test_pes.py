from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import PES


sender_sequence_number = "test_sender_sequence_numb"
sender_comment = "test_sender_comment"
sender_aware_date_time = "test_sender_aware_date_ti"
event_report_date = "test_event_report_date"
event_report_timing_type = "test_event_report_timing_"
event_report_source = "test_event_report_source"


class TestPES:
    """Comprehensive tests for PES segment."""

    def test_pes_build_and_verify(self):
        seg = PES()

        seg.sender_sequence_number = sender_sequence_number
        seg.sender_comment = sender_comment
        seg.sender_aware_date_time = sender_aware_date_time
        seg.event_report_date = event_report_date
        seg.event_report_timing_type = event_report_timing_type
        seg.event_report_source = event_report_source

        assert seg.sender_sequence_number == sender_sequence_number
        assert seg.sender_comment == sender_comment
        assert seg.sender_aware_date_time == sender_aware_date_time
        assert seg.event_report_date == event_report_date
        assert seg.event_report_timing_type == event_report_timing_type
        assert seg.event_report_source == event_report_source

    def test_pes_to_dict(self):
        seg = PES()

        seg.sender_sequence_number = sender_sequence_number
        seg.sender_comment = sender_comment
        seg.sender_aware_date_time = sender_aware_date_time
        seg.event_report_date = event_report_date
        seg.event_report_timing_type = event_report_timing_type
        seg.event_report_source = event_report_source

        result = seg.to_dict()

        assert result["_segment_id"] == "PES"
        assert result["sender_sequence_number"] == sender_sequence_number
        assert result["sender_comment"] == sender_comment
        assert result["sender_aware_date_time"] == sender_aware_date_time
        assert result["event_report_date"] == event_report_date
        assert result["event_report_timing_type"] == event_report_timing_type
        assert result["event_report_source"] == event_report_source

    def test_pes_to_json(self):
        seg = PES()

        seg.sender_sequence_number = sender_sequence_number
        seg.sender_comment = sender_comment
        seg.sender_aware_date_time = sender_aware_date_time
        seg.event_report_date = event_report_date
        seg.event_report_timing_type = event_report_timing_type
        seg.event_report_source = event_report_source

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "PES"
        assert result["sender_sequence_number"] == sender_sequence_number
        assert result["sender_comment"] == sender_comment
        assert result["sender_aware_date_time"] == sender_aware_date_time
        assert result["event_report_date"] == event_report_date
        assert result["event_report_timing_type"] == event_report_timing_type
        assert result["event_report_source"] == event_report_source
