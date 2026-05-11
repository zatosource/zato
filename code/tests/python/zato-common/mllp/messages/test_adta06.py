from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import AdtA06
from zato.hl7v2.v2_9.segments import ACC, DRG, EVN, IN1, IN2, MRG, MSH, NK1, OBX, OH3, PD1, PID, PR1, PV1, PV2, UAC, UB2


class TestAdtA06:
    """Comprehensive tests for AdtA06 message."""

    def test_adt_a06_create(self):
        msg = AdtA06()
        assert msg._structure_id == "ADT_A06"

    def test_adt_a06_segment_access(self):
        msg = AdtA06()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.evn._segment_id == "EVN"
        assert msg.pid._segment_id == "PID"
        assert msg.pd1._segment_id == "PD1"
        assert msg.oh3._segment_id == "OH3"
        assert msg.mrg._segment_id == "MRG"
        assert msg.nk1._segment_id == "NK1"
        assert msg.oh3._segment_id == "OH3"
        assert msg.pv1._segment_id == "PV1"
        assert msg.pv2._segment_id == "PV2"
        assert msg.obx._segment_id == "OBX"
        assert msg.drg._segment_id == "DRG"
        assert msg.pr1._segment_id == "PR1"
        assert msg.in1._segment_id == "IN1"
        assert msg.in2._segment_id == "IN2"
        assert msg.acc._segment_id == "ACC"
        assert msg.ub2._segment_id == "UB2"

    def test_adt_a06_to_dict(self):
        msg = AdtA06()

        result = msg.to_dict()

        assert result["_structure_id"] == "ADT_A06"

    def test_adt_a06_to_json(self):
        msg = AdtA06()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "ADT_A06"
