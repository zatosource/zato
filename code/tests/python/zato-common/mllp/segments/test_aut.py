from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import AUT


authorizing_payor_company_name = "test_authorizing_payor_co"
authorization_effective_date = "test_authorization_effect"
authorization_expiration_date = "test_authorization_expira"
process_date = "test_process_date"
planned_treatment_stop_date = "test_planned_treatment_st"
reason_text = "test_reason_text"
source_text = "test_source_text"
source_date = "test_source_date"
comment = "test_comment"
action_code = "test_action_code"


class TestAUT:
    """Comprehensive tests for AUT segment."""

    def test_aut_build_and_verify(self):
        seg = AUT()

        seg.authorizing_payor_company_name = authorizing_payor_company_name
        seg.authorization_effective_date = authorization_effective_date
        seg.authorization_expiration_date = authorization_expiration_date
        seg.process_date = process_date
        seg.planned_treatment_stop_date = planned_treatment_stop_date
        seg.reason_text = reason_text
        seg.source_text = source_text
        seg.source_date = source_date
        seg.comment = comment
        seg.action_code = action_code

        assert seg.authorizing_payor_company_name == authorizing_payor_company_name
        assert seg.authorization_effective_date == authorization_effective_date
        assert seg.authorization_expiration_date == authorization_expiration_date
        assert seg.process_date == process_date
        assert seg.planned_treatment_stop_date == planned_treatment_stop_date
        assert seg.reason_text == reason_text
        assert seg.source_text == source_text
        assert seg.source_date == source_date
        assert seg.comment == comment
        assert seg.action_code == action_code

    def test_aut_to_dict(self):
        seg = AUT()

        seg.authorizing_payor_company_name = authorizing_payor_company_name
        seg.authorization_effective_date = authorization_effective_date
        seg.authorization_expiration_date = authorization_expiration_date
        seg.process_date = process_date
        seg.planned_treatment_stop_date = planned_treatment_stop_date
        seg.reason_text = reason_text
        seg.source_text = source_text
        seg.source_date = source_date
        seg.comment = comment
        seg.action_code = action_code

        result = seg.to_dict()

        assert result["_segment_id"] == "AUT"
        assert result["authorizing_payor_company_name"] == authorizing_payor_company_name
        assert result["authorization_effective_date"] == authorization_effective_date
        assert result["authorization_expiration_date"] == authorization_expiration_date
        assert result["process_date"] == process_date
        assert result["planned_treatment_stop_date"] == planned_treatment_stop_date
        assert result["reason_text"] == reason_text
        assert result["source_text"] == source_text
        assert result["source_date"] == source_date
        assert result["comment"] == comment
        assert result["action_code"] == action_code

    def test_aut_to_json(self):
        seg = AUT()

        seg.authorizing_payor_company_name = authorizing_payor_company_name
        seg.authorization_effective_date = authorization_effective_date
        seg.authorization_expiration_date = authorization_expiration_date
        seg.process_date = process_date
        seg.planned_treatment_stop_date = planned_treatment_stop_date
        seg.reason_text = reason_text
        seg.source_text = source_text
        seg.source_date = source_date
        seg.comment = comment
        seg.action_code = action_code

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "AUT"
        assert result["authorizing_payor_company_name"] == authorizing_payor_company_name
        assert result["authorization_effective_date"] == authorization_effective_date
        assert result["authorization_expiration_date"] == authorization_expiration_date
        assert result["process_date"] == process_date
        assert result["planned_treatment_stop_date"] == planned_treatment_stop_date
        assert result["reason_text"] == reason_text
        assert result["source_text"] == source_text
        assert result["source_date"] == source_date
        assert result["comment"] == comment
        assert result["action_code"] == action_code
