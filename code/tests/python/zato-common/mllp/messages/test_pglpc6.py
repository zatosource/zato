from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import PglPc6
from zato.hl7v2.v2_9.segments import GOL, MSH, OBR, OBX, ORC, PID, PRB, PRD, PRT, PTH, PV1, PV2, UAC


class TestPglPc6:
    """Comprehensive tests for PglPc6 message."""

    def test_pgl_pc6_create(self):
        msg = PglPc6()
        assert msg._structure_id == "PGL_PC6"

    def test_pgl_pc6_segment_access(self):
        msg = PglPc6()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.pid._segment_id == "PID"
        assert msg.prd._segment_id == "PRD"
        assert msg.pv1._segment_id == "PV1"
        assert msg.pv2._segment_id == "PV2"
        assert msg.gol._segment_id == "GOL"
        assert msg.prt._segment_id == "PRT"
        assert msg.pth._segment_id == "PTH"
        assert msg.obx._segment_id == "OBX"
        assert msg.prb._segment_id == "PRB"
        assert msg.prt._segment_id == "PRT"
        assert msg.obx._segment_id == "OBX"
        assert msg.orc._segment_id == "ORC"
        assert msg.obr._segment_id == "OBR"
        assert msg.obx._segment_id == "OBX"

    def test_pgl_pc6_to_dict(self):
        msg = PglPc6()

        result = msg.to_dict()

        assert result["_structure_id"] == "PGL_PC6"

    def test_pgl_pc6_to_json(self):
        msg = PglPc6()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "PGL_PC6"
