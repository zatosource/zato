from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import AdtA02
from zato.hl7v2.v2_9.segments import EVN, MSH, OBX, OH3, PD1, PDA, PID, PV1, PV2, UAC


class TestAdtA02:
    """Comprehensive tests for AdtA02 message."""

    def test_adt_a02_create(self):
        msg = AdtA02()
        assert msg._structure_id == "ADT_A02"

    def test_adt_a02_segment_access(self):
        msg = AdtA02()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.evn._segment_id == "EVN"
        assert msg.pid._segment_id == "PID"
        assert msg.pd1._segment_id == "PD1"
        assert msg.oh3._segment_id == "OH3"
        assert msg.pv1._segment_id == "PV1"
        assert msg.pv2._segment_id == "PV2"
        assert msg.obx._segment_id == "OBX"
        assert msg.pda._segment_id == "PDA"

    def test_adt_a02_to_dict(self):
        msg = AdtA02()

        result = msg.to_dict()

        assert result["_structure_id"] == "ADT_A02"

    def test_adt_a02_to_json(self):
        msg = AdtA02()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "ADT_A02"
