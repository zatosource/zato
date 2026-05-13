from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import ODT


text_instruction = "test_text_instruction"


class TestODT:
    """Comprehensive tests for ODT segment."""

    def test_odt_build_and_verify(self):
        seg = ODT()

        seg.text_instruction = text_instruction

        assert seg.text_instruction == text_instruction

    def test_odt_to_dict(self):
        seg = ODT()

        seg.text_instruction = text_instruction

        result = seg.to_dict()

        assert result["_segment_id"] == "ODT"
        assert result["text_instruction"] == text_instruction

    def test_odt_to_json(self):
        seg = ODT()

        seg.text_instruction = text_instruction

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "ODT"
        assert result["text_instruction"] == text_instruction
