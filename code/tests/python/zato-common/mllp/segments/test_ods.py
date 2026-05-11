from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import ODS


type_ = "test_type_"
text_instruction = "test_text_instruction"


class TestODS:
    """Comprehensive tests for ODS segment."""

    def test_ods_build_and_verify(self):
        seg = ODS()

        seg.type_ = type_
        seg.text_instruction = text_instruction

        assert seg.type_ == type_
        assert seg.text_instruction == text_instruction

    def test_ods_to_dict(self):
        seg = ODS()

        seg.type_ = type_
        seg.text_instruction = text_instruction

        result = seg.to_dict()

        assert result["_segment_id"] == "ODS"
        assert result["type_"] == type_
        assert result["text_instruction"] == text_instruction

    def test_ods_to_json(self):
        seg = ODS()

        seg.type_ = type_
        seg.text_instruction = text_instruction

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "ODS"
        assert result["type_"] == type_
        assert result["text_instruction"] == text_instruction
