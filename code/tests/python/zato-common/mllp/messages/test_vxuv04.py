from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import VXU_V04


class TestVxuV04:
    """Comprehensive tests for VxuV04 message."""

    def test_vxu_v04_create(self):
        msg = VXU_V04()
        assert msg._structure_id == "VXU_V04"

    def test_vxu_v04_segment_access(self):
        msg = VXU_V04()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.pid._segment_id == "PID"
        assert msg.pd1._segment_id == "PD1"
        assert msg.pv1._segment_id == "PV1"
        assert msg.pv2._segment_id == "PV2"
        assert msg.in1._segment_id == "IN1"
        assert msg.in2._segment_id == "IN2"
        assert msg.in3._segment_id == "IN3"
        assert msg.obx._segment_id == "OBX"
        assert msg.orc._segment_id == "ORC"
        assert msg.tq1._segment_id == "TQ1"
        assert msg.rxa._segment_id == "RXA"
        assert msg.rxr._segment_id == "RXR"
        assert msg.obx._segment_id == "OBX"

    def test_vxu_v04_to_dict(self):
        msg = VXU_V04()

        result = msg.to_dict()

        assert result["_structure_id"] == "VXU_V04"

    def test_vxu_v04_to_json(self):
        msg = VXU_V04()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "VXU_V04"
