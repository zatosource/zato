from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import OruR01
from zato.hl7v2.v2_9.segments import CTD, DEV, DSC, IN1, IN2, IN3, MSH, NK1, OBR, OBX, OH3, ORC, PD1, PID, PRT, PV1, PV2, SPM, TQ1, TXA, UAC


class TestOruR01:
    """Comprehensive tests for OruR01 message."""

    def test_oru_r01_create(self):
        msg = OruR01()
        assert msg._structure_id == "ORU_R01"

    def test_oru_r01_segment_access(self):
        msg = OruR01()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.pid._segment_id == "PID"
        assert msg.pd1._segment_id == "PD1"
        assert msg.oh3._segment_id == "OH3"
        assert msg.nk1._segment_id == "NK1"
        assert msg.oh3._segment_id == "OH3"
        assert msg.obx._segment_id == "OBX"
        assert msg.pv1._segment_id == "PV1"
        assert msg.pv2._segment_id == "PV2"
        assert msg.in1._segment_id == "IN1"
        assert msg.in2._segment_id == "IN2"
        assert msg.in3._segment_id == "IN3"
        assert msg.orc._segment_id == "ORC"
        assert msg.obx._segment_id == "OBX"
        assert msg.txa._segment_id == "TXA"
        assert msg.obr._segment_id == "OBR"
        assert msg.prt._segment_id == "PRT"
        assert msg.tq1._segment_id == "TQ1"
        assert msg.ctd._segment_id == "CTD"
        assert msg.obx._segment_id == "OBX"
        assert msg.spm._segment_id == "SPM"
        assert msg.obx._segment_id == "OBX"
        assert msg.dev._segment_id == "DEV"
        assert msg.dsc._segment_id == "DSC"

    def test_oru_r01_to_dict(self):
        msg = OruR01()

        result = msg.to_dict()

        assert result["_structure_id"] == "ORU_R01"

    def test_oru_r01_to_json(self):
        msg = OruR01()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "ORU_R01"
