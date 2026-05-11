from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import AdtA44
from zato.hl7v2.v2_9.segments import EVN, MRG, MSH, PD1, PID, UAC


class TestAdtA44:
    """Comprehensive tests for AdtA44 message."""

    def test_adt_a44_create(self):
        msg = AdtA44()
        assert msg._structure_id == "ADT_A44"

    def test_adt_a44_segment_access(self):
        msg = AdtA44()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.evn._segment_id == "EVN"
        assert msg.pid._segment_id == "PID"
        assert msg.pd1._segment_id == "PD1"
        assert msg.mrg._segment_id == "MRG"

    def test_adt_a44_to_dict(self):
        msg = AdtA44()

        result = msg.to_dict()

        assert result["_structure_id"] == "ADT_A44"

    def test_adt_a44_to_json(self):
        msg = AdtA44()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "ADT_A44"
