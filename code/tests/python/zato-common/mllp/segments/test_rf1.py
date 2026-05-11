from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import RF1


effective_date = "test_effective_date"
expiration_date = "test_expiration_date"
process_date = "test_process_date"
planned_treatment_stop_date = "test_planned_treatment_st"
referral_reason_text = "test_referral_reason_text"
source_text = "test_source_text"
source_date = "test_source_date"
comment = "test_comment"
action_code = "test_action_code"


class TestRF1:
    """Comprehensive tests for RF1 segment."""

    def test_rf1_build_and_verify(self):
        seg = RF1()

        seg.effective_date = effective_date
        seg.expiration_date = expiration_date
        seg.process_date = process_date
        seg.planned_treatment_stop_date = planned_treatment_stop_date
        seg.referral_reason_text = referral_reason_text
        seg.source_text = source_text
        seg.source_date = source_date
        seg.comment = comment
        seg.action_code = action_code

        assert seg.effective_date == effective_date
        assert seg.expiration_date == expiration_date
        assert seg.process_date == process_date
        assert seg.planned_treatment_stop_date == planned_treatment_stop_date
        assert seg.referral_reason_text == referral_reason_text
        assert seg.source_text == source_text
        assert seg.source_date == source_date
        assert seg.comment == comment
        assert seg.action_code == action_code

    def test_rf1_to_dict(self):
        seg = RF1()

        seg.effective_date = effective_date
        seg.expiration_date = expiration_date
        seg.process_date = process_date
        seg.planned_treatment_stop_date = planned_treatment_stop_date
        seg.referral_reason_text = referral_reason_text
        seg.source_text = source_text
        seg.source_date = source_date
        seg.comment = comment
        seg.action_code = action_code

        result = seg.to_dict()

        assert result["_segment_id"] == "RF1"
        assert result["effective_date"] == effective_date
        assert result["expiration_date"] == expiration_date
        assert result["process_date"] == process_date
        assert result["planned_treatment_stop_date"] == planned_treatment_stop_date
        assert result["referral_reason_text"] == referral_reason_text
        assert result["source_text"] == source_text
        assert result["source_date"] == source_date
        assert result["comment"] == comment
        assert result["action_code"] == action_code

    def test_rf1_to_json(self):
        seg = RF1()

        seg.effective_date = effective_date
        seg.expiration_date = expiration_date
        seg.process_date = process_date
        seg.planned_treatment_stop_date = planned_treatment_stop_date
        seg.referral_reason_text = referral_reason_text
        seg.source_text = source_text
        seg.source_date = source_date
        seg.comment = comment
        seg.action_code = action_code

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "RF1"
        assert result["effective_date"] == effective_date
        assert result["expiration_date"] == expiration_date
        assert result["process_date"] == process_date
        assert result["planned_treatment_stop_date"] == planned_treatment_stop_date
        assert result["referral_reason_text"] == referral_reason_text
        assert result["source_text"] == source_text
        assert result["source_date"] == source_date
        assert result["comment"] == comment
        assert result["action_code"] == action_code
