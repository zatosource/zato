from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import PprPc1
from zato.hl7v2.v2_9.segments import GOL, MSH, OBR, OBX, ORC, PID, PRB, PRD, PRT, PTH, PV1, PV2, UAC


class TestPprPc1:
    """Comprehensive tests for PprPc1 message."""

    def test_ppr_pc1_create(self):
        msg = PprPc1()
        assert msg._structure_id == "PPR_PC1"

    def test_ppr_pc1_segment_access(self):
        msg = PprPc1()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.pid._segment_id == "PID"
        assert msg.prd._segment_id == "PRD"
        assert msg.pv1._segment_id == "PV1"
        assert msg.pv2._segment_id == "PV2"
        assert msg.prb._segment_id == "PRB"
        assert msg.prt._segment_id == "PRT"
        assert msg.pth._segment_id == "PTH"
        assert msg.obx._segment_id == "OBX"
        assert msg.gol._segment_id == "GOL"
        assert msg.prt._segment_id == "PRT"
        assert msg.obx._segment_id == "OBX"
        assert msg.orc._segment_id == "ORC"
        assert msg.obr._segment_id == "OBR"
        assert msg.obx._segment_id == "OBX"

    def test_ppr_pc1_to_dict(self):
        msg = PprPc1()

        result = msg.to_dict()

        assert result["_structure_id"] == "PPR_PC1"

    def test_ppr_pc1_to_json(self):
        msg = PprPc1()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "PPR_PC1"
