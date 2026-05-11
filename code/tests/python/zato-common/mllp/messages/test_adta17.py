from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import AdtA17
from zato.hl7v2.v2_9.segments import EVN, MSH, OBX, PD1, PID, PV1, PV2, UAC


class TestAdtA17:
    """Comprehensive tests for AdtA17 message."""

    def test_adt_a17_create(self):
        msg = AdtA17()
        assert msg._structure_id == "ADT_A17"

    def test_adt_a17_segment_access(self):
        msg = AdtA17()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.evn._segment_id == "EVN"
        assert msg.pid._segment_id == "PID"
        assert msg.pd1._segment_id == "PD1"
        assert msg.pv1._segment_id == "PV1"
        assert msg.pv2._segment_id == "PV2"
        assert msg.obx._segment_id == "OBX"
        assert msg.pid._segment_id == "PID"
        assert msg.pd1._segment_id == "PD1"
        assert msg.pv1._segment_id == "PV1"
        assert msg.pv2._segment_id == "PV2"
        assert msg.obx._segment_id == "OBX"

    def test_adt_a17_to_dict(self):
        msg = AdtA17()

        result = msg.to_dict()

        assert result["_structure_id"] == "ADT_A17"

    def test_adt_a17_to_json(self):
        msg = AdtA17()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "ADT_A17"
