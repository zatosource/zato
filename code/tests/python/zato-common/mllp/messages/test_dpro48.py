from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import DprO48
from zato.hl7v2.v2_9.segments import DON, MSH, OBR, OBX, PD1, PID, PV1, UAC


class TestDprO48:
    """Comprehensive tests for DprO48 message."""

    def test_dpr_o48_create(self):
        msg = DprO48()
        assert msg._structure_id == "DPR_O48"

    def test_dpr_o48_segment_access(self):
        msg = DprO48()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.pid._segment_id == "PID"
        assert msg.pd1._segment_id == "PD1"
        assert msg.obx._segment_id == "OBX"
        assert msg.pv1._segment_id == "PV1"
        assert msg.obr._segment_id == "OBR"
        assert msg.don._segment_id == "DON"
        assert msg.obx._segment_id == "OBX"

    def test_dpr_o48_to_dict(self):
        msg = DprO48()

        result = msg.to_dict()

        assert result["_structure_id"] == "DPR_O48"

    def test_dpr_o48_to_json(self):
        msg = DprO48()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "DPR_O48"
