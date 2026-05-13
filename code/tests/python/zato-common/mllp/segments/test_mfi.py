from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import MFI


file_level_event_code = "test_file_level_event_cod"
entered_date_time = "test_entered_date_time"
effective_date_time = "test_effective_date_time"
response_level_code = "test_response_level_code"


class TestMFI:
    """Comprehensive tests for MFI segment."""

    def test_mfi_build_and_verify(self):
        seg = MFI()

        seg.file_level_event_code = file_level_event_code
        seg.entered_date_time = entered_date_time
        seg.effective_date_time = effective_date_time
        seg.response_level_code = response_level_code

        assert seg.file_level_event_code == file_level_event_code
        assert seg.entered_date_time == entered_date_time
        assert seg.effective_date_time == effective_date_time
        assert seg.response_level_code == response_level_code

    def test_mfi_to_dict(self):
        seg = MFI()

        seg.file_level_event_code = file_level_event_code
        seg.entered_date_time = entered_date_time
        seg.effective_date_time = effective_date_time
        seg.response_level_code = response_level_code

        result = seg.to_dict()

        assert result["_segment_id"] == "MFI"
        assert result["file_level_event_code"] == file_level_event_code
        assert result["entered_date_time"] == entered_date_time
        assert result["effective_date_time"] == effective_date_time
        assert result["response_level_code"] == response_level_code

    def test_mfi_to_json(self):
        seg = MFI()

        seg.file_level_event_code = file_level_event_code
        seg.entered_date_time = entered_date_time
        seg.effective_date_time = effective_date_time
        seg.response_level_code = response_level_code

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "MFI"
        assert result["file_level_event_code"] == file_level_event_code
        assert result["entered_date_time"] == entered_date_time
        assert result["effective_date_time"] == effective_date_time
        assert result["response_level_code"] == response_level_code
