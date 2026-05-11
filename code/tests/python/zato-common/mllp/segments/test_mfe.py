from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import MFE


record_level_event_code = "test_record_level_event_c"
mfn_control_id = "test_mfn_control_id"
effective_date_time = "test_effective_date_time"
entered_date_time = "test_entered_date_time"


class TestMFE:
    """Comprehensive tests for MFE segment."""

    def test_mfe_build_and_verify(self):
        seg = MFE()

        seg.record_level_event_code = record_level_event_code
        seg.mfn_control_id = mfn_control_id
        seg.effective_date_time = effective_date_time
        seg.entered_date_time = entered_date_time

        assert seg.record_level_event_code == record_level_event_code
        assert seg.mfn_control_id == mfn_control_id
        assert seg.effective_date_time == effective_date_time
        assert seg.entered_date_time == entered_date_time

    def test_mfe_to_dict(self):
        seg = MFE()

        seg.record_level_event_code = record_level_event_code
        seg.mfn_control_id = mfn_control_id
        seg.effective_date_time = effective_date_time
        seg.entered_date_time = entered_date_time

        result = seg.to_dict()

        assert result["_segment_id"] == "MFE"
        assert result["record_level_event_code"] == record_level_event_code
        assert result["mfn_control_id"] == mfn_control_id
        assert result["effective_date_time"] == effective_date_time
        assert result["entered_date_time"] == entered_date_time

    def test_mfe_to_json(self):
        seg = MFE()

        seg.record_level_event_code = record_level_event_code
        seg.mfn_control_id = mfn_control_id
        seg.effective_date_time = effective_date_time
        seg.entered_date_time = entered_date_time

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "MFE"
        assert result["record_level_event_code"] == record_level_event_code
        assert result["mfn_control_id"] == mfn_control_id
        assert result["effective_date_time"] == effective_date_time
        assert result["entered_date_time"] == entered_date_time
