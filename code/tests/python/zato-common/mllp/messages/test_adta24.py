from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import AdtA24
from zato.hl7v2.v2_9.segments import EVN, MSH, PD1, PID, PV1, UAC


class TestAdtA24:
    """Comprehensive tests for AdtA24 message."""

    def test_adt_a24_create(self):
        msg = AdtA24()
        assert msg._structure_id == "ADT_A24"

    def test_adt_a24_segment_access(self):
        msg = AdtA24()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.evn._segment_id == "EVN"
        assert msg.pid._segment_id == "PID"
        assert msg.pd1._segment_id == "PD1"
        assert msg.pv1._segment_id == "PV1"
        assert msg.pid._segment_id == "PID"
        assert msg.pd1._segment_id == "PD1"
        assert msg.pv1._segment_id == "PV1"

    def test_adt_a24_to_dict(self):
        msg = AdtA24()

        result = msg.to_dict()

        assert result["_structure_id"] == "ADT_A24"

    def test_adt_a24_to_json(self):
        msg = AdtA24()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "ADT_A24"
