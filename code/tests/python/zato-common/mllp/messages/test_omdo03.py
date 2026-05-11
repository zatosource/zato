from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import OmdO03
from zato.hl7v2.v2_9.segments import GT1, IN1, IN2, IN3, MSH, OBX, ORC, PD1, PID, PV1, PV2, TQ1, UAC


class TestOmdO03:
    """Comprehensive tests for OmdO03 message."""

    def test_omd_o03_create(self):
        msg = OmdO03()
        assert msg._structure_id == "OMD_O03"

    def test_omd_o03_segment_access(self):
        msg = OmdO03()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.pid._segment_id == "PID"
        assert msg.pd1._segment_id == "PD1"
        assert msg.pv1._segment_id == "PV1"
        assert msg.pv2._segment_id == "PV2"
        assert msg.in1._segment_id == "IN1"
        assert msg.in2._segment_id == "IN2"
        assert msg.in3._segment_id == "IN3"
        assert msg.gt1._segment_id == "GT1"
        assert msg.orc._segment_id == "ORC"
        assert msg.tq1._segment_id == "TQ1"
        assert msg.obx._segment_id == "OBX"
        assert msg.orc._segment_id == "ORC"
        assert msg.tq1._segment_id == "TQ1"

    def test_omd_o03_to_dict(self):
        msg = OmdO03()

        result = msg.to_dict()

        assert result["_structure_id"] == "OMD_O03"

    def test_omd_o03_to_json(self):
        msg = OmdO03()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "OMD_O03"
