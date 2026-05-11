from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import FHS


file_field_separator = "test_file_field_separator"
file_encoding_characters = "test_file_encoding_charac"
file_creation_date_time = "test_file_creation_date_t"
file_security = "test_file_security"
file_name_id = "test_file_name_id"
file_header_comment = "test_file_header_comment"
file_control_id = "test_file_control_id"
reference_file_control_id = "test_reference_file_contr"


class TestFHS:
    """Comprehensive tests for FHS segment."""

    def test_fhs_build_and_verify(self):
        seg = FHS()

        seg.file_field_separator = file_field_separator
        seg.file_encoding_characters = file_encoding_characters
        seg.file_creation_date_time = file_creation_date_time
        seg.file_security = file_security
        seg.file_name_id = file_name_id
        seg.file_header_comment = file_header_comment
        seg.file_control_id = file_control_id
        seg.reference_file_control_id = reference_file_control_id

        assert seg.file_field_separator == file_field_separator
        assert seg.file_encoding_characters == file_encoding_characters
        assert seg.file_creation_date_time == file_creation_date_time
        assert seg.file_security == file_security
        assert seg.file_name_id == file_name_id
        assert seg.file_header_comment == file_header_comment
        assert seg.file_control_id == file_control_id
        assert seg.reference_file_control_id == reference_file_control_id

    def test_fhs_to_dict(self):
        seg = FHS()

        seg.file_field_separator = file_field_separator
        seg.file_encoding_characters = file_encoding_characters
        seg.file_creation_date_time = file_creation_date_time
        seg.file_security = file_security
        seg.file_name_id = file_name_id
        seg.file_header_comment = file_header_comment
        seg.file_control_id = file_control_id
        seg.reference_file_control_id = reference_file_control_id

        result = seg.to_dict()

        assert result["_segment_id"] == "FHS"
        assert result["file_field_separator"] == file_field_separator
        assert result["file_encoding_characters"] == file_encoding_characters
        assert result["file_creation_date_time"] == file_creation_date_time
        assert result["file_security"] == file_security
        assert result["file_name_id"] == file_name_id
        assert result["file_header_comment"] == file_header_comment
        assert result["file_control_id"] == file_control_id
        assert result["reference_file_control_id"] == reference_file_control_id

    def test_fhs_to_json(self):
        seg = FHS()

        seg.file_field_separator = file_field_separator
        seg.file_encoding_characters = file_encoding_characters
        seg.file_creation_date_time = file_creation_date_time
        seg.file_security = file_security
        seg.file_name_id = file_name_id
        seg.file_header_comment = file_header_comment
        seg.file_control_id = file_control_id
        seg.reference_file_control_id = reference_file_control_id

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "FHS"
        assert result["file_field_separator"] == file_field_separator
        assert result["file_encoding_characters"] == file_encoding_characters
        assert result["file_creation_date_time"] == file_creation_date_time
        assert result["file_security"] == file_security
        assert result["file_name_id"] == file_name_id
        assert result["file_header_comment"] == file_header_comment
        assert result["file_control_id"] == file_control_id
        assert result["reference_file_control_id"] == reference_file_control_id
