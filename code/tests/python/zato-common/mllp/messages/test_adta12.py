from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import AdtA12
from zato.hl7v2.v2_9.segments import DG1, EVN, MSH, OBX, PD1, PID, PV1, PV2, UAC


class TestAdtA12:
    """Comprehensive tests for AdtA12 message."""

    def test_adt_a12_create(self):
        msg = AdtA12()
        assert msg._structure_id == "ADT_A12"

    def test_adt_a12_segment_access(self):
        msg = AdtA12()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.evn._segment_id == "EVN"
        assert msg.pid._segment_id == "PID"
        assert msg.pd1._segment_id == "PD1"
        assert msg.pv1._segment_id == "PV1"
        assert msg.pv2._segment_id == "PV2"
        assert msg.obx._segment_id == "OBX"
        assert msg.dg1._segment_id == "DG1"

    def test_adt_a12_to_dict(self):
        msg = AdtA12()

        result = msg.to_dict()

        assert result["_structure_id"] == "ADT_A12"

    def test_adt_a12_to_json(self):
        msg = AdtA12()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "ADT_A12"
