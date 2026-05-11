from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import RgvO15
from zato.hl7v2.v2_9.segments import MSH, OBX, ORC, PID, PV1, PV2, RXC, RXE, RXG, RXO, TQ1, UAC


class TestRgvO15:
    """Comprehensive tests for RgvO15 message."""

    def test_rgv_o15_create(self):
        msg = RgvO15()
        assert msg._structure_id == "RGV_O15"

    def test_rgv_o15_segment_access(self):
        msg = RgvO15()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.pid._segment_id == "PID"
        assert msg.pv1._segment_id == "PV1"
        assert msg.pv2._segment_id == "PV2"
        assert msg.orc._segment_id == "ORC"
        assert msg.tq1._segment_id == "TQ1"
        assert msg.rxo._segment_id == "RXO"
        assert msg.rxc._segment_id == "RXC"
        assert msg.rxe._segment_id == "RXE"
        assert msg.tq1._segment_id == "TQ1"
        assert msg.rxg._segment_id == "RXG"
        assert msg.tq1._segment_id == "TQ1"
        assert msg.obx._segment_id == "OBX"

    def test_rgv_o15_to_dict(self):
        msg = RgvO15()

        result = msg.to_dict()

        assert result["_structure_id"] == "RGV_O15"

    def test_rgv_o15_to_json(self):
        msg = RgvO15()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "RGV_O15"
