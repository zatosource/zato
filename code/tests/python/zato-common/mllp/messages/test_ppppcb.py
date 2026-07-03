from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import PPP_PCB


class TestPppPcb:
    """Comprehensive tests for PppPcb message."""

    def test_ppp_pcb_create(self):
        msg = PPP_PCB()
        assert msg._structure_id == "PPP_PCB"

    def test_ppp_pcb_segment_access(self):
        msg = PPP_PCB()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.pid._segment_id == "PID"
        assert msg.prd._segment_id == "PRD"
        assert msg.pv1._segment_id == "PV1"
        assert msg.pv2._segment_id == "PV2"
        assert msg.pth._segment_id == "PTH"
        assert msg.prt._segment_id == "PRT"
        assert msg.prb._segment_id == "PRB"
        assert msg.prt._segment_id == "PRT"
        assert msg.obx._segment_id == "OBX"
        assert msg.gol._segment_id == "GOL"
        assert msg.prt._segment_id == "PRT"
        assert msg.obx._segment_id == "OBX"
        assert msg.orc._segment_id == "ORC"
        assert msg.obr._segment_id == "OBR"
        assert msg.obx._segment_id == "OBX"

    def test_ppp_pcb_to_dict(self):
        msg = PPP_PCB()

        result = msg.to_dict()

        assert result["_structure_id"] == "PPP_PCB"

    def test_ppp_pcb_to_json(self):
        msg = PPP_PCB()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "PPP_PCB"
