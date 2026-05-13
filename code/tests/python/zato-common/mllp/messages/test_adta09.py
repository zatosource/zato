from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import AdtA09
from zato.hl7v2.v2_9.segments import EVN, MSH, OBX, PD1, PID, PV1, PV2, UAC


class TestAdtA09:
    """Comprehensive tests for AdtA09 message."""

    def test_adt_a09_create(self):
        msg = AdtA09()
        assert msg._structure_id == "ADT_A09"

    def test_adt_a09_segment_access(self):
        msg = AdtA09()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.evn._segment_id == "EVN"
        assert msg.pid._segment_id == "PID"
        assert msg.pd1._segment_id == "PD1"
        assert msg.pv1._segment_id == "PV1"
        assert msg.pv2._segment_id == "PV2"
        assert msg.obx._segment_id == "OBX"

    def test_adt_a09_to_dict(self):
        msg = AdtA09()

        result = msg.to_dict()

        assert result["_structure_id"] == "ADT_A09"

    def test_adt_a09_to_json(self):
        msg = AdtA09()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "ADT_A09"
