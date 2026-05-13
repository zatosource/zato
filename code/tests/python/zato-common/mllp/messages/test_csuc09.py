from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import CsuC09
from zato.hl7v2.v2_9.segments import CSP, CSR, CSS, MSH, OBR, OBX, ORC, PD1, PID, PV1, PV2, RXA, RXR, TQ1, UAC


class TestCsuC09:
    """Comprehensive tests for CsuC09 message."""

    def test_csu_c09_create(self):
        msg = CsuC09()
        assert msg._structure_id == "CSU_C09"

    def test_csu_c09_segment_access(self):
        msg = CsuC09()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.pid._segment_id == "PID"
        assert msg.pd1._segment_id == "PD1"
        assert msg.pv1._segment_id == "PV1"
        assert msg.pv2._segment_id == "PV2"
        assert msg.csr._segment_id == "CSR"
        assert msg.csp._segment_id == "CSP"
        assert msg.css._segment_id == "CSS"
        assert msg.orc._segment_id == "ORC"
        assert msg.obr._segment_id == "OBR"
        assert msg.tq1._segment_id == "TQ1"
        assert msg.obx._segment_id == "OBX"
        assert msg.orc._segment_id == "ORC"
        assert msg.rxa._segment_id == "RXA"
        assert msg.rxr._segment_id == "RXR"

    def test_csu_c09_to_dict(self):
        msg = CsuC09()

        result = msg.to_dict()

        assert result["_structure_id"] == "CSU_C09"

    def test_csu_c09_to_json(self):
        msg = CsuC09()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "CSU_C09"
