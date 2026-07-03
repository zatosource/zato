from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import PPG_PCG


class TestPpgPcg:
    """Comprehensive tests for PpgPcg message."""

    def test_ppg_pcg_create(self):
        msg = PPG_PCG()
        assert msg._structure_id == "PPG_PCG"

    def test_ppg_pcg_segment_access(self):
        msg = PPG_PCG()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.pid._segment_id == "PID"
        assert msg.prd._segment_id == "PRD"
        assert msg.pv1._segment_id == "PV1"
        assert msg.pv2._segment_id == "PV2"
        assert msg.pth._segment_id == "PTH"
        assert msg.prt._segment_id == "PRT"
        assert msg.gol._segment_id == "GOL"
        assert msg.prt._segment_id == "PRT"
        assert msg.obx._segment_id == "OBX"
        assert msg.prb._segment_id == "PRB"
        assert msg.prt._segment_id == "PRT"
        assert msg.obx._segment_id == "OBX"
        assert msg.orc._segment_id == "ORC"
        assert msg.obr._segment_id == "OBR"
        assert msg.obx._segment_id == "OBX"

    def test_ppg_pcg_to_dict(self):
        msg = PPG_PCG()

        result = msg.to_dict()

        assert result["_structure_id"] == "PPG_PCG"

    def test_ppg_pcg_to_json(self):
        msg = PPG_PCG()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "PPG_PCG"
