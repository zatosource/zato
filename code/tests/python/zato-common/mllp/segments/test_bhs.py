from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import BHS


batch_field_separator = "test_batch_field_separato"
batch_encoding_characters = "test_batch_encoding_chara"
batch_creation_date_time = "test_batch_creation_date_"
batch_security = "test_batch_security"
batch_name_id_type = "test_batch_name_id_type"
batch_comment = "test_batch_comment"
batch_control_id = "test_batch_control_id"
reference_batch_control_id = "test_reference_batch_cont"


class TestBHS:
    """Comprehensive tests for BHS segment."""

    def test_bhs_build_and_verify(self):
        seg = BHS()

        seg.batch_field_separator = batch_field_separator
        seg.batch_encoding_characters = batch_encoding_characters
        seg.batch_creation_date_time = batch_creation_date_time
        seg.batch_security = batch_security
        seg.batch_name_id_type = batch_name_id_type
        seg.batch_comment = batch_comment
        seg.batch_control_id = batch_control_id
        seg.reference_batch_control_id = reference_batch_control_id

        assert seg.batch_field_separator == batch_field_separator
        assert seg.batch_encoding_characters == batch_encoding_characters
        assert seg.batch_creation_date_time == batch_creation_date_time
        assert seg.batch_security == batch_security
        assert seg.batch_name_id_type == batch_name_id_type
        assert seg.batch_comment == batch_comment
        assert seg.batch_control_id == batch_control_id
        assert seg.reference_batch_control_id == reference_batch_control_id

    def test_bhs_to_dict(self):
        seg = BHS()

        seg.batch_field_separator = batch_field_separator
        seg.batch_encoding_characters = batch_encoding_characters
        seg.batch_creation_date_time = batch_creation_date_time
        seg.batch_security = batch_security
        seg.batch_name_id_type = batch_name_id_type
        seg.batch_comment = batch_comment
        seg.batch_control_id = batch_control_id
        seg.reference_batch_control_id = reference_batch_control_id

        result = seg.to_dict()

        assert result["_segment_id"] == "BHS"
        assert result["batch_field_separator"] == batch_field_separator
        assert result["batch_encoding_characters"] == batch_encoding_characters
        assert result["batch_creation_date_time"] == batch_creation_date_time
        assert result["batch_security"] == batch_security
        assert result["batch_name_id_type"] == batch_name_id_type
        assert result["batch_comment"] == batch_comment
        assert result["batch_control_id"] == batch_control_id
        assert result["reference_batch_control_id"] == reference_batch_control_id

    def test_bhs_to_json(self):
        seg = BHS()

        seg.batch_field_separator = batch_field_separator
        seg.batch_encoding_characters = batch_encoding_characters
        seg.batch_creation_date_time = batch_creation_date_time
        seg.batch_security = batch_security
        seg.batch_name_id_type = batch_name_id_type
        seg.batch_comment = batch_comment
        seg.batch_control_id = batch_control_id
        seg.reference_batch_control_id = reference_batch_control_id

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "BHS"
        assert result["batch_field_separator"] == batch_field_separator
        assert result["batch_encoding_characters"] == batch_encoding_characters
        assert result["batch_creation_date_time"] == batch_creation_date_time
        assert result["batch_security"] == batch_security
        assert result["batch_name_id_type"] == batch_name_id_type
        assert result["batch_comment"] == batch_comment
        assert result["batch_control_id"] == batch_control_id
        assert result["reference_batch_control_id"] == reference_batch_control_id
