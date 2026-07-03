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

    def test_ppp_pcb_to_dict(self):
        msg = PPP_PCB()

        result = msg.to_dict()

        assert result["_structure_id"] == "PPP_PCB"

    def test_ppp_pcb_to_json(self):
        msg = PPP_PCB()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "PPP_PCB"
