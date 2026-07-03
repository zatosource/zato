from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import PPR_PC1


class TestPprPc1:
    """Comprehensive tests for PprPc1 message."""

    def test_ppr_pc1_create(self):
        msg = PPR_PC1()
        assert msg._structure_id == "PPR_PC1"

    def test_ppr_pc1_segment_access(self):
        msg = PPR_PC1()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.pid._segment_id == "PID"

    def test_ppr_pc1_to_dict(self):
        msg = PPR_PC1()

        result = msg.to_dict()

        assert result["_structure_id"] == "PPR_PC1"

    def test_ppr_pc1_to_json(self):
        msg = PPR_PC1()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "PPR_PC1"
