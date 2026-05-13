from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import LDP


active_inactive_flag = "test_active_inactive_flag"
activation_date_ldp = "test_activation_date_ldp"
inactivation_date_ldp = "test_inactivation_date_ld"
inactivated_reason = "test_inactivated_reason"


class TestLDP:
    """Comprehensive tests for LDP segment."""

    def test_ldp_build_and_verify(self):
        seg = LDP()

        seg.active_inactive_flag = active_inactive_flag
        seg.activation_date_ldp = activation_date_ldp
        seg.inactivation_date_ldp = inactivation_date_ldp
        seg.inactivated_reason = inactivated_reason

        assert seg.active_inactive_flag == active_inactive_flag
        assert seg.activation_date_ldp == activation_date_ldp
        assert seg.inactivation_date_ldp == inactivation_date_ldp
        assert seg.inactivated_reason == inactivated_reason

    def test_ldp_to_dict(self):
        seg = LDP()

        seg.active_inactive_flag = active_inactive_flag
        seg.activation_date_ldp = activation_date_ldp
        seg.inactivation_date_ldp = inactivation_date_ldp
        seg.inactivated_reason = inactivated_reason

        result = seg.to_dict()

        assert result["_segment_id"] == "LDP"
        assert result["active_inactive_flag"] == active_inactive_flag
        assert result["activation_date_ldp"] == activation_date_ldp
        assert result["inactivation_date_ldp"] == inactivation_date_ldp
        assert result["inactivated_reason"] == inactivated_reason

    def test_ldp_to_json(self):
        seg = LDP()

        seg.active_inactive_flag = active_inactive_flag
        seg.activation_date_ldp = activation_date_ldp
        seg.inactivation_date_ldp = inactivation_date_ldp
        seg.inactivated_reason = inactivated_reason

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "LDP"
        assert result["active_inactive_flag"] == active_inactive_flag
        assert result["activation_date_ldp"] == activation_date_ldp
        assert result["inactivation_date_ldp"] == inactivation_date_ldp
        assert result["inactivated_reason"] == inactivated_reason
