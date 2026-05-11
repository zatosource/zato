from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import OplO37
from zato.hl7v2.v2_9.segments import AL1, BLG, GT1, IN1, IN2, IN3, MSH, OBR, OBX, ORC, PD1, PID, PRT, PV1, PV2, SAC, SGH, SGT, SPM, TCD, TQ1, UAC


class TestOplO37:
    """Comprehensive tests for OplO37 message."""

    def test_opl_o37_create(self):
        msg = OplO37()
        assert msg._structure_id == "OPL_O37"

    def test_opl_o37_segment_access(self):
        msg = OplO37()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.gt1._segment_id == "GT1"
        assert msg.pid._segment_id == "PID"
        assert msg.pd1._segment_id == "PD1"
        assert msg.obx._segment_id == "OBX"
        assert msg.in1._segment_id == "IN1"
        assert msg.in2._segment_id == "IN2"
        assert msg.in3._segment_id == "IN3"
        assert msg.spm._segment_id == "SPM"
        assert msg.obx._segment_id == "OBX"
        assert msg.sac._segment_id == "SAC"
        assert msg.obx._segment_id == "OBX"
        assert msg.orc._segment_id == "ORC"
        assert msg.obr._segment_id == "OBR"
        assert msg.tq1._segment_id == "TQ1"
        assert msg.tcd._segment_id == "TCD"
        assert msg.obx._segment_id == "OBX"
        assert msg.sgh._segment_id == "SGH"
        assert msg.pid._segment_id == "PID"
        assert msg.pd1._segment_id == "PD1"
        assert msg.pv1._segment_id == "PV1"
        assert msg.pv2._segment_id == "PV2"
        assert msg.al1._segment_id == "AL1"
        assert msg.obr._segment_id == "OBR"
        assert msg.orc._segment_id == "ORC"
        assert msg.prt._segment_id == "PRT"
        assert msg.tq1._segment_id == "TQ1"
        assert msg.obx._segment_id == "OBX"
        assert msg.sgt._segment_id == "SGT"
        assert msg.blg._segment_id == "BLG"

    def test_opl_o37_to_dict(self):
        msg = OplO37()

        result = msg.to_dict()

        assert result["_structure_id"] == "OPL_O37"

    def test_opl_o37_to_json(self):
        msg = OplO37()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "OPL_O37"
