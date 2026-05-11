from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import OpuR25
from zato.hl7v2.v2_9.segments import INV, MSH, NTE, OBR, OBX, OH3, ORC, PD1, PID, PV1, PV2, SAC, SPM, TQ1, UAC


class TestOpuR25:
    """Comprehensive tests for OpuR25 message."""

    def test_opu_r25_create(self):
        msg = OpuR25()
        assert msg._structure_id == "OPU_R25"

    def test_opu_r25_segment_access(self):
        msg = OpuR25()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.nte._segment_id == "NTE"
        assert msg.pv1._segment_id == "PV1"
        assert msg.pv2._segment_id == "PV2"
        assert msg.obx._segment_id == "OBX"
        assert msg.pid._segment_id == "PID"
        assert msg.pd1._segment_id == "PD1"
        assert msg.oh3._segment_id == "OH3"
        assert msg.obx._segment_id == "OBX"
        assert msg.spm._segment_id == "SPM"
        assert msg.obx._segment_id == "OBX"
        assert msg.sac._segment_id == "SAC"
        assert msg.inv._segment_id == "INV"
        assert msg.obr._segment_id == "OBR"
        assert msg.orc._segment_id == "ORC"
        assert msg.tq1._segment_id == "TQ1"
        assert msg.obx._segment_id == "OBX"

    def test_opu_r25_to_dict(self):
        msg = OpuR25()

        result = msg.to_dict()

        assert result["_structure_id"] == "OPU_R25"

    def test_opu_r25_to_json(self):
        msg = OpuR25()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "OPU_R25"
