from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import OulR23
from zato.hl7v2.v2_9.segments import DEV, DSC, INV, MSH, NTE, OBR, OBX, OH3, ORC, PD1, PID, PV1, PV2, SAC, SPM, TCD, TQ1, TXA, UAC


class TestOulR23:
    """Comprehensive tests for OulR23 message."""

    def test_oul_r23_create(self):
        msg = OulR23()
        assert msg._structure_id == "OUL_R23"

    def test_oul_r23_segment_access(self):
        msg = OulR23()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.nte._segment_id == "NTE"
        assert msg.pid._segment_id == "PID"
        assert msg.pd1._segment_id == "PD1"
        assert msg.oh3._segment_id == "OH3"
        assert msg.obx._segment_id == "OBX"
        assert msg.pv1._segment_id == "PV1"
        assert msg.pv2._segment_id == "PV2"
        assert msg.spm._segment_id == "SPM"
        assert msg.obx._segment_id == "OBX"
        assert msg.sac._segment_id == "SAC"
        assert msg.inv._segment_id == "INV"
        assert msg.obr._segment_id == "OBR"
        assert msg.orc._segment_id == "ORC"
        assert msg.obx._segment_id == "OBX"
        assert msg.txa._segment_id == "TXA"
        assert msg.tq1._segment_id == "TQ1"
        assert msg.obx._segment_id == "OBX"
        assert msg.tcd._segment_id == "TCD"
        assert msg.dev._segment_id == "DEV"
        assert msg.dsc._segment_id == "DSC"

    def test_oul_r23_to_dict(self):
        msg = OulR23()

        result = msg.to_dict()

        assert result["_structure_id"] == "OUL_R23"

    def test_oul_r23_to_json(self):
        msg = OulR23()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "OUL_R23"
