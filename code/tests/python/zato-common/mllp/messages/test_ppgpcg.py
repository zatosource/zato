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

    def test_ppg_pcg_to_dict(self):
        msg = PPG_PCG()

        result = msg.to_dict()

        assert result["_structure_id"] == "PPG_PCG"

    def test_ppg_pcg_to_json(self):
        msg = PPG_PCG()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "PPG_PCG"
