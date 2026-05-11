from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import DftP11
from zato.hl7v2.v2_9.segments import ACC, DG1, DRG, EVN, FT1, IN1, IN2, MSH, OBR, OBX, ORC, PD1, PID, PR1, PV1, PV2, TQ1, UAC


class TestDftP11:
    """Comprehensive tests for DftP11 message."""

    def test_dft_p11_create(self):
        msg = DftP11()
        assert msg._structure_id == "DFT_P11"

    def test_dft_p11_segment_access(self):
        msg = DftP11()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.evn._segment_id == "EVN"
        assert msg.pid._segment_id == "PID"
        assert msg.pd1._segment_id == "PD1"
        assert msg.pv1._segment_id == "PV1"
        assert msg.pv2._segment_id == "PV2"
        assert msg.orc._segment_id == "ORC"
        assert msg.tq1._segment_id == "TQ1"
        assert msg.obr._segment_id == "OBR"
        assert msg.obx._segment_id == "OBX"
        assert msg.dg1._segment_id == "DG1"
        assert msg.drg._segment_id == "DRG"
        assert msg.in1._segment_id == "IN1"
        assert msg.in2._segment_id == "IN2"
        assert msg.acc._segment_id == "ACC"
        assert msg.ft1._segment_id == "FT1"
        assert msg.pr1._segment_id == "PR1"
        assert msg.orc._segment_id == "ORC"
        assert msg.obr._segment_id == "OBR"
        assert msg.obx._segment_id == "OBX"
        assert msg.orc._segment_id == "ORC"
        assert msg.tq1._segment_id == "TQ1"
        assert msg.obr._segment_id == "OBR"
        assert msg.obx._segment_id == "OBX"
        assert msg.dg1._segment_id == "DG1"
        assert msg.drg._segment_id == "DRG"
        assert msg.in1._segment_id == "IN1"
        assert msg.in2._segment_id == "IN2"

    def test_dft_p11_to_dict(self):
        msg = DftP11()

        result = msg.to_dict()

        assert result["_structure_id"] == "DFT_P11"

    def test_dft_p11_to_json(self):
        msg = DftP11()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "DFT_P11"
