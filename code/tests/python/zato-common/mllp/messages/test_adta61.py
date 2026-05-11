from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import AdtA61
from zato.hl7v2.v2_9.segments import EVN, MSH, PD1, PID, PV1, PV2, UAC


class TestAdtA61:
    """Comprehensive tests for AdtA61 message."""

    def test_adt_a61_create(self):
        msg = AdtA61()
        assert msg._structure_id == "ADT_A61"

    def test_adt_a61_segment_access(self):
        msg = AdtA61()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.evn._segment_id == "EVN"
        assert msg.pid._segment_id == "PID"
        assert msg.pd1._segment_id == "PD1"
        assert msg.pv1._segment_id == "PV1"
        assert msg.pv2._segment_id == "PV2"

    def test_adt_a61_to_dict(self):
        msg = AdtA61()

        result = msg.to_dict()

        assert result["_structure_id"] == "ADT_A61"

    def test_adt_a61_to_json(self):
        msg = AdtA61()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "ADT_A61"
