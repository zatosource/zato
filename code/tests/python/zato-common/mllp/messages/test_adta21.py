from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import AdtA21
from zato.hl7v2.v2_9.segments import EVN, MSH, OBX, PD1, PID, PV1, PV2, UAC


class TestAdtA21:
    """Comprehensive tests for AdtA21 message."""

    def test_adt_a21_create(self):
        msg = AdtA21()
        assert msg._structure_id == "ADT_A21"

    def test_adt_a21_segment_access(self):
        msg = AdtA21()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.evn._segment_id == "EVN"
        assert msg.pid._segment_id == "PID"
        assert msg.pd1._segment_id == "PD1"
        assert msg.pv1._segment_id == "PV1"
        assert msg.pv2._segment_id == "PV2"
        assert msg.obx._segment_id == "OBX"

    def test_adt_a21_to_dict(self):
        msg = AdtA21()

        result = msg.to_dict()

        assert result["_structure_id"] == "ADT_A21"

    def test_adt_a21_to_json(self):
        msg = AdtA21()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "ADT_A21"
