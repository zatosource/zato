from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import AdtA37
from zato.hl7v2.v2_9.segments import EVN, MSH, PD1, PID, PV1, UAC


class TestAdtA37:
    """Comprehensive tests for AdtA37 message."""

    def test_adt_a37_create(self):
        msg = AdtA37()
        assert msg._structure_id == "ADT_A37"

    def test_adt_a37_segment_access(self):
        msg = AdtA37()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.evn._segment_id == "EVN"
        assert msg.pid._segment_id == "PID"
        assert msg.pd1._segment_id == "PD1"
        assert msg.pv1._segment_id == "PV1"
        assert msg.pid._segment_id == "PID"
        assert msg.pd1._segment_id == "PD1"
        assert msg.pv1._segment_id == "PV1"

    def test_adt_a37_to_dict(self):
        msg = AdtA37()

        result = msg.to_dict()

        assert result["_structure_id"] == "ADT_A37"

    def test_adt_a37_to_json(self):
        msg = AdtA37()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "ADT_A37"
