from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import OmbO27
from zato.hl7v2.v2_9.segments import BLG, BPO, GT1, IN1, IN2, IN3, MSH, OBX, ORC, PD1, PID, PV1, PV2, SPM, TQ1, UAC


class TestOmbO27:
    """Comprehensive tests for OmbO27 message."""

    def test_omb_o27_create(self):
        msg = OmbO27()
        assert msg._structure_id == "OMB_O27"

    def test_omb_o27_segment_access(self):
        msg = OmbO27()

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
        assert msg.bpo._segment_id == "BPO"
        assert msg.spm._segment_id == "SPM"
        assert msg.obx._segment_id == "OBX"
        assert msg.blg._segment_id == "BLG"

    def test_omb_o27_to_dict(self):
        msg = OmbO27()

        result = msg.to_dict()

        assert result["_structure_id"] == "OMB_O27"

    def test_omb_o27_to_json(self):
        msg = OmbO27()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "OMB_O27"
