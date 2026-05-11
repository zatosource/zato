from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import AdtA16
from zato.hl7v2.v2_9.segments import ACC, AUT, DRG, EVN, IN1, IN2, MSH, NK1, OBX, OH3, PD1, PID, PR1, PV1, PV2, RF1, UAC


class TestAdtA16:
    """Comprehensive tests for AdtA16 message."""

    def test_adt_a16_create(self):
        msg = AdtA16()
        assert msg._structure_id == "ADT_A16"

    def test_adt_a16_segment_access(self):
        msg = AdtA16()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.evn._segment_id == "EVN"
        assert msg.pid._segment_id == "PID"
        assert msg.pd1._segment_id == "PD1"
        assert msg.oh3._segment_id == "OH3"
        assert msg.nk1._segment_id == "NK1"
        assert msg.oh3._segment_id == "OH3"
        assert msg.pv1._segment_id == "PV1"
        assert msg.pv2._segment_id == "PV2"
        assert msg.obx._segment_id == "OBX"
        assert msg.drg._segment_id == "DRG"
        assert msg.pr1._segment_id == "PR1"
        assert msg.in1._segment_id == "IN1"
        assert msg.in2._segment_id == "IN2"
        assert msg.aut._segment_id == "AUT"
        assert msg.rf1._segment_id == "RF1"
        assert msg.acc._segment_id == "ACC"

    def test_adt_a16_to_dict(self):
        msg = AdtA16()

        result = msg.to_dict()

        assert result["_structure_id"] == "ADT_A16"

    def test_adt_a16_to_json(self):
        msg = AdtA16()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "ADT_A16"
