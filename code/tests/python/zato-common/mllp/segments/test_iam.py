from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import IAM


set_id_iam = "test_set_id_iam"
action_reason = "test_action_reason"
onset_date = "test_onset_date"
onset_date_text = "test_onset_date_text"
reported_date_time = "test_reported_date_time"
statused_at_date_time = "test_statused_at_date_tim"
inactivated_date_time = "test_inactivated_date_tim"
initially_recorded_date_time = "test_initially_recorded_d"
modified_date_time = "test_modified_date_time"


class TestIAM:
    """Comprehensive tests for IAM segment."""

    def test_iam_build_and_verify(self):
        seg = IAM()

        seg.set_id_iam = set_id_iam
        seg.action_reason = action_reason
        seg.onset_date = onset_date
        seg.onset_date_text = onset_date_text
        seg.reported_date_time = reported_date_time
        seg.statused_at_date_time = statused_at_date_time
        seg.inactivated_date_time = inactivated_date_time
        seg.initially_recorded_date_time = initially_recorded_date_time
        seg.modified_date_time = modified_date_time

        assert seg.set_id_iam == set_id_iam
        assert seg.action_reason == action_reason
        assert seg.onset_date == onset_date
        assert seg.onset_date_text == onset_date_text
        assert seg.reported_date_time == reported_date_time
        assert seg.statused_at_date_time == statused_at_date_time
        assert seg.inactivated_date_time == inactivated_date_time
        assert seg.initially_recorded_date_time == initially_recorded_date_time
        assert seg.modified_date_time == modified_date_time

    def test_iam_to_dict(self):
        seg = IAM()

        seg.set_id_iam = set_id_iam
        seg.action_reason = action_reason
        seg.onset_date = onset_date
        seg.onset_date_text = onset_date_text
        seg.reported_date_time = reported_date_time
        seg.statused_at_date_time = statused_at_date_time
        seg.inactivated_date_time = inactivated_date_time
        seg.initially_recorded_date_time = initially_recorded_date_time
        seg.modified_date_time = modified_date_time

        result = seg.to_dict()

        assert result["_segment_id"] == "IAM"
        assert result["set_id_iam"] == set_id_iam
        assert result["action_reason"] == action_reason
        assert result["onset_date"] == onset_date
        assert result["onset_date_text"] == onset_date_text
        assert result["reported_date_time"] == reported_date_time
        assert result["statused_at_date_time"] == statused_at_date_time
        assert result["inactivated_date_time"] == inactivated_date_time
        assert result["initially_recorded_date_time"] == initially_recorded_date_time
        assert result["modified_date_time"] == modified_date_time

    def test_iam_to_json(self):
        seg = IAM()

        seg.set_id_iam = set_id_iam
        seg.action_reason = action_reason
        seg.onset_date = onset_date
        seg.onset_date_text = onset_date_text
        seg.reported_date_time = reported_date_time
        seg.statused_at_date_time = statused_at_date_time
        seg.inactivated_date_time = inactivated_date_time
        seg.initially_recorded_date_time = initially_recorded_date_time
        seg.modified_date_time = modified_date_time

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "IAM"
        assert result["set_id_iam"] == set_id_iam
        assert result["action_reason"] == action_reason
        assert result["onset_date"] == onset_date
        assert result["onset_date_text"] == onset_date_text
        assert result["reported_date_time"] == reported_date_time
        assert result["statused_at_date_time"] == statused_at_date_time
        assert result["inactivated_date_time"] == inactivated_date_time
        assert result["initially_recorded_date_time"] == initially_recorded_date_time
        assert result["modified_date_time"] == modified_date_time
