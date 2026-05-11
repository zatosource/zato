from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import OruR30
from zato.hl7v2.v2_9.segments import DEV, MSH, OBR, OBX, OH3, ORC, PD1, PID, PV1, PV2, TQ1, UAC


class TestOruR30:
    """Comprehensive tests for OruR30 message."""

    def test_oru_r30_create(self):
        msg = OruR30()
        assert msg._structure_id == "ORU_R30"

    def test_oru_r30_segment_access(self):
        msg = OruR30()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.pid._segment_id == "PID"
        assert msg.pd1._segment_id == "PD1"
        assert msg.oh3._segment_id == "OH3"
        assert msg.obx._segment_id == "OBX"
        assert msg.pv1._segment_id == "PV1"
        assert msg.pv2._segment_id == "PV2"
        assert msg.orc._segment_id == "ORC"
        assert msg.obr._segment_id == "OBR"
        assert msg.tq1._segment_id == "TQ1"
        assert msg.obx._segment_id == "OBX"
        assert msg.dev._segment_id == "DEV"

    def test_oru_r30_to_dict(self):
        msg = OruR30()

        result = msg.to_dict()

        assert result["_structure_id"] == "ORU_R30"

    def test_oru_r30_to_json(self):
        msg = OruR30()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "ORU_R30"
