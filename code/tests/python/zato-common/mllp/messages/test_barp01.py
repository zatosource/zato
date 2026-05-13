from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import BarP01
from zato.hl7v2.v2_9.segments import ACC, DG1, DRG, EVN, IN1, IN2, MSH, PD1, PID, PR1, PV1, PV2, UAC, UB2


class TestBarP01:
    """Comprehensive tests for BarP01 message."""

    def test_bar_p01_create(self):
        msg = BarP01()
        assert msg._structure_id == "BAR_P01"

    def test_bar_p01_segment_access(self):
        msg = BarP01()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.evn._segment_id == "EVN"
        assert msg.pid._segment_id == "PID"
        assert msg.pd1._segment_id == "PD1"
        assert msg.pv1._segment_id == "PV1"
        assert msg.pv2._segment_id == "PV2"
        assert msg.dg1._segment_id == "DG1"
        assert msg.drg._segment_id == "DRG"
        assert msg.pr1._segment_id == "PR1"
        assert msg.in1._segment_id == "IN1"
        assert msg.in2._segment_id == "IN2"
        assert msg.acc._segment_id == "ACC"
        assert msg.ub2._segment_id == "UB2"

    def test_bar_p01_to_dict(self):
        msg = BarP01()

        result = msg.to_dict()

        assert result["_structure_id"] == "BAR_P01"

    def test_bar_p01_to_json(self):
        msg = BarP01()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "BAR_P01"
