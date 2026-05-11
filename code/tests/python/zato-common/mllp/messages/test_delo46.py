from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import DelO46
from zato.hl7v2.v2_9.segments import DON, MSH, OBX, PD1, PID, PV1, UAC


class TestDelO46:
    """Comprehensive tests for DelO46 message."""

    def test_del_o46_create(self):
        msg = DelO46()
        assert msg._structure_id == "DEL_O46"

    def test_del_o46_segment_access(self):
        msg = DelO46()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.pid._segment_id == "PID"
        assert msg.pd1._segment_id == "PD1"
        assert msg.obx._segment_id == "OBX"
        assert msg.pv1._segment_id == "PV1"
        assert msg.don._segment_id == "DON"

    def test_del_o46_to_dict(self):
        msg = DelO46()

        result = msg.to_dict()

        assert result["_structure_id"] == "DEL_O46"

    def test_del_o46_to_json(self):
        msg = DelO46()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "DEL_O46"
