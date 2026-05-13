from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import NST


statistics_available = "test_statistics_available"
source_identifier = "test_source_identifier"
source_type = "test_source_type"
statistics_start = "test_statistics_start"
statistics_end = "test_statistics_end"
receive_character_count = "test_receive_character_co"
send_character_count = "test_send_character_count"
messages_received = "test_messages_received"
messages_sent = "test_messages_sent"
checksum_errors_received = "test_checksum_errors_rece"
length_errors_received = "test_length_errors_receiv"
other_errors_received = "test_other_errors_receive"
connect_timeouts = "test_connect_timeouts"
receive_timeouts = "test_receive_timeouts"
application_control_level_errors = "test_application_control_"


class TestNST:
    """Comprehensive tests for NST segment."""

    def test_nst_build_and_verify(self):
        seg = NST()

        seg.statistics_available = statistics_available
        seg.source_identifier = source_identifier
        seg.source_type = source_type
        seg.statistics_start = statistics_start
        seg.statistics_end = statistics_end
        seg.receive_character_count = receive_character_count
        seg.send_character_count = send_character_count
        seg.messages_received = messages_received
        seg.messages_sent = messages_sent
        seg.checksum_errors_received = checksum_errors_received
        seg.length_errors_received = length_errors_received
        seg.other_errors_received = other_errors_received
        seg.connect_timeouts = connect_timeouts
        seg.receive_timeouts = receive_timeouts
        seg.application_control_level_errors = application_control_level_errors

        assert seg.statistics_available == statistics_available
        assert seg.source_identifier == source_identifier
        assert seg.source_type == source_type
        assert seg.statistics_start == statistics_start
        assert seg.statistics_end == statistics_end
        assert seg.receive_character_count == receive_character_count
        assert seg.send_character_count == send_character_count
        assert seg.messages_received == messages_received
        assert seg.messages_sent == messages_sent
        assert seg.checksum_errors_received == checksum_errors_received
        assert seg.length_errors_received == length_errors_received
        assert seg.other_errors_received == other_errors_received
        assert seg.connect_timeouts == connect_timeouts
        assert seg.receive_timeouts == receive_timeouts
        assert seg.application_control_level_errors == application_control_level_errors

    def test_nst_to_dict(self):
        seg = NST()

        seg.statistics_available = statistics_available
        seg.source_identifier = source_identifier
        seg.source_type = source_type
        seg.statistics_start = statistics_start
        seg.statistics_end = statistics_end
        seg.receive_character_count = receive_character_count
        seg.send_character_count = send_character_count
        seg.messages_received = messages_received
        seg.messages_sent = messages_sent
        seg.checksum_errors_received = checksum_errors_received
        seg.length_errors_received = length_errors_received
        seg.other_errors_received = other_errors_received
        seg.connect_timeouts = connect_timeouts
        seg.receive_timeouts = receive_timeouts
        seg.application_control_level_errors = application_control_level_errors

        result = seg.to_dict()

        assert result["_segment_id"] == "NST"
        assert result["statistics_available"] == statistics_available
        assert result["source_identifier"] == source_identifier
        assert result["source_type"] == source_type
        assert result["statistics_start"] == statistics_start
        assert result["statistics_end"] == statistics_end
        assert result["receive_character_count"] == receive_character_count
        assert result["send_character_count"] == send_character_count
        assert result["messages_received"] == messages_received
        assert result["messages_sent"] == messages_sent
        assert result["checksum_errors_received"] == checksum_errors_received
        assert result["length_errors_received"] == length_errors_received
        assert result["other_errors_received"] == other_errors_received
        assert result["connect_timeouts"] == connect_timeouts
        assert result["receive_timeouts"] == receive_timeouts
        assert result["application_control_level_errors"] == application_control_level_errors

    def test_nst_to_json(self):
        seg = NST()

        seg.statistics_available = statistics_available
        seg.source_identifier = source_identifier
        seg.source_type = source_type
        seg.statistics_start = statistics_start
        seg.statistics_end = statistics_end
        seg.receive_character_count = receive_character_count
        seg.send_character_count = send_character_count
        seg.messages_received = messages_received
        seg.messages_sent = messages_sent
        seg.checksum_errors_received = checksum_errors_received
        seg.length_errors_received = length_errors_received
        seg.other_errors_received = other_errors_received
        seg.connect_timeouts = connect_timeouts
        seg.receive_timeouts = receive_timeouts
        seg.application_control_level_errors = application_control_level_errors

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "NST"
        assert result["statistics_available"] == statistics_available
        assert result["source_identifier"] == source_identifier
        assert result["source_type"] == source_type
        assert result["statistics_start"] == statistics_start
        assert result["statistics_end"] == statistics_end
        assert result["receive_character_count"] == receive_character_count
        assert result["send_character_count"] == send_character_count
        assert result["messages_received"] == messages_received
        assert result["messages_sent"] == messages_sent
        assert result["checksum_errors_received"] == checksum_errors_received
        assert result["length_errors_received"] == length_errors_received
        assert result["other_errors_received"] == other_errors_received
        assert result["connect_timeouts"] == connect_timeouts
        assert result["receive_timeouts"] == receive_timeouts
        assert result["application_control_level_errors"] == application_control_level_errors
