from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import MSA


acknowledgment_code = "test_acknowledgment_code"
message_control_id = "test_message_control_id"
expected_sequence_number = "test_expected_sequence_nu"
message_waiting_number = "test_message_waiting_numb"
message_waiting_priority = "test_message_waiting_prio"


class TestMSA:
    """Comprehensive tests for MSA segment."""

    def test_msa_build_and_verify(self):
        seg = MSA()

        seg.acknowledgment_code = acknowledgment_code
        seg.message_control_id = message_control_id
        seg.expected_sequence_number = expected_sequence_number
        seg.message_waiting_number = message_waiting_number
        seg.message_waiting_priority = message_waiting_priority

        assert seg.acknowledgment_code == acknowledgment_code
        assert seg.message_control_id == message_control_id
        assert seg.expected_sequence_number == expected_sequence_number
        assert seg.message_waiting_number == message_waiting_number
        assert seg.message_waiting_priority == message_waiting_priority

    def test_msa_to_dict(self):
        seg = MSA()

        seg.acknowledgment_code = acknowledgment_code
        seg.message_control_id = message_control_id
        seg.expected_sequence_number = expected_sequence_number
        seg.message_waiting_number = message_waiting_number
        seg.message_waiting_priority = message_waiting_priority

        result = seg.to_dict()

        assert result["_segment_id"] == "MSA"
        assert result["acknowledgment_code"] == acknowledgment_code
        assert result["message_control_id"] == message_control_id
        assert result["expected_sequence_number"] == expected_sequence_number
        assert result["message_waiting_number"] == message_waiting_number
        assert result["message_waiting_priority"] == message_waiting_priority

    def test_msa_to_json(self):
        seg = MSA()

        seg.acknowledgment_code = acknowledgment_code
        seg.message_control_id = message_control_id
        seg.expected_sequence_number = expected_sequence_number
        seg.message_waiting_number = message_waiting_number
        seg.message_waiting_priority = message_waiting_priority

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "MSA"
        assert result["acknowledgment_code"] == acknowledgment_code
        assert result["message_control_id"] == message_control_id
        assert result["expected_sequence_number"] == expected_sequence_number
        assert result["message_waiting_number"] == message_waiting_number
        assert result["message_waiting_priority"] == message_waiting_priority
