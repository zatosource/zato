from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import MSH


field_separator = "test_field_separator"
encoding_characters = "test_encoding_characters"
date_time_of_message = "test_date_time_of_message"
security = "test_security"
message_control_id = "test_message_control_id"
sequence_number = "test_sequence_number"
continuation_pointer = "test_continuation_pointer"
accept_acknowledgment = "test_accept_acknowledgmen"
application_acknowledgment_type = "test_application_acknowle"
country_code = "test_country_code"
alternate_character_set_handling_scheme = "test_alternate_character_"


class TestMSH:
    """Comprehensive tests for MSH segment."""

    def test_msh_build_and_verify(self):
        seg = MSH()

        seg.field_separator = field_separator
        seg.encoding_characters = encoding_characters
        seg.date_time_of_message = date_time_of_message
        seg.security = security
        seg.message_control_id = message_control_id
        seg.sequence_number = sequence_number
        seg.continuation_pointer = continuation_pointer
        seg.accept_acknowledgment = accept_acknowledgment
        seg.application_acknowledgment_type = application_acknowledgment_type
        seg.country_code = country_code
        seg.alternate_character_set_handling_scheme = alternate_character_set_handling_scheme

        assert seg.field_separator == field_separator
        assert seg.encoding_characters == encoding_characters
        assert seg.date_time_of_message == date_time_of_message
        assert seg.security == security
        assert seg.message_control_id == message_control_id
        assert seg.sequence_number == sequence_number
        assert seg.continuation_pointer == continuation_pointer
        assert seg.accept_acknowledgment == accept_acknowledgment
        assert seg.application_acknowledgment_type == application_acknowledgment_type
        assert seg.country_code == country_code
        assert seg.alternate_character_set_handling_scheme == alternate_character_set_handling_scheme

    def test_msh_to_dict(self):
        seg = MSH()

        seg.field_separator = field_separator
        seg.encoding_characters = encoding_characters
        seg.date_time_of_message = date_time_of_message
        seg.security = security
        seg.message_control_id = message_control_id
        seg.sequence_number = sequence_number
        seg.continuation_pointer = continuation_pointer
        seg.accept_acknowledgment = accept_acknowledgment
        seg.application_acknowledgment_type = application_acknowledgment_type
        seg.country_code = country_code
        seg.alternate_character_set_handling_scheme = alternate_character_set_handling_scheme

        result = seg.to_dict()

        assert result["_segment_id"] == "MSH"
        assert result["field_separator"] == field_separator
        assert result["encoding_characters"] == encoding_characters
        assert result["date_time_of_message"] == date_time_of_message
        assert result["security"] == security
        assert result["message_control_id"] == message_control_id
        assert result["sequence_number"] == sequence_number
        assert result["continuation_pointer"] == continuation_pointer
        assert result["accept_acknowledgment"] == accept_acknowledgment
        assert result["application_acknowledgment_type"] == application_acknowledgment_type
        assert result["country_code"] == country_code
        assert result["alternate_character_set_handling_scheme"] == alternate_character_set_handling_scheme

    def test_msh_to_json(self):
        seg = MSH()

        seg.field_separator = field_separator
        seg.encoding_characters = encoding_characters
        seg.date_time_of_message = date_time_of_message
        seg.security = security
        seg.message_control_id = message_control_id
        seg.sequence_number = sequence_number
        seg.continuation_pointer = continuation_pointer
        seg.accept_acknowledgment = accept_acknowledgment
        seg.application_acknowledgment_type = application_acknowledgment_type
        seg.country_code = country_code
        seg.alternate_character_set_handling_scheme = alternate_character_set_handling_scheme

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "MSH"
        assert result["field_separator"] == field_separator
        assert result["encoding_characters"] == encoding_characters
        assert result["date_time_of_message"] == date_time_of_message
        assert result["security"] == security
        assert result["message_control_id"] == message_control_id
        assert result["sequence_number"] == sequence_number
        assert result["continuation_pointer"] == continuation_pointer
        assert result["accept_acknowledgment"] == accept_acknowledgment
        assert result["application_acknowledgment_type"] == application_acknowledgment_type
        assert result["country_code"] == country_code
        assert result["alternate_character_set_handling_scheme"] == alternate_character_set_handling_scheme
