from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import MFA


record_level_event_code = "test_record_level_event_c"
mfn_control_id = "test_mfn_control_id"
event_completion_date_time = "test_event_completion_dat"


class TestMFA:
    """Comprehensive tests for MFA segment."""

    def test_mfa_build_and_verify(self):
        seg = MFA()

        seg.record_level_event_code = record_level_event_code
        seg.mfn_control_id = mfn_control_id
        seg.event_completion_date_time = event_completion_date_time

        assert seg.record_level_event_code == record_level_event_code
        assert seg.mfn_control_id == mfn_control_id
        assert seg.event_completion_date_time == event_completion_date_time

    def test_mfa_to_dict(self):
        seg = MFA()

        seg.record_level_event_code = record_level_event_code
        seg.mfn_control_id = mfn_control_id
        seg.event_completion_date_time = event_completion_date_time

        result = seg.to_dict()

        assert result["_segment_id"] == "MFA"
        assert result["record_level_event_code"] == record_level_event_code
        assert result["mfn_control_id"] == mfn_control_id
        assert result["event_completion_date_time"] == event_completion_date_time

    def test_mfa_to_json(self):
        seg = MFA()

        seg.record_level_event_code = record_level_event_code
        seg.mfn_control_id = mfn_control_id
        seg.event_completion_date_time = event_completion_date_time

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "MFA"
        assert result["record_level_event_code"] == record_level_event_code
        assert result["mfn_control_id"] == mfn_control_id
        assert result["event_completion_date_time"] == event_completion_date_time
