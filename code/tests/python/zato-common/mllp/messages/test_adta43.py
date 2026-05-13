from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import AdtA43
from zato.hl7v2.v2_9.segments import EVN, MRG, MSH, PD1, PID, UAC


class TestAdtA43:
    """Comprehensive tests for AdtA43 message."""

    def test_adt_a43_create(self):
        msg = AdtA43()
        assert msg._structure_id == "ADT_A43"

    def test_adt_a43_segment_access(self):
        msg = AdtA43()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.evn._segment_id == "EVN"
        assert msg.pid._segment_id == "PID"
        assert msg.pd1._segment_id == "PD1"
        assert msg.mrg._segment_id == "MRG"

    def test_adt_a43_to_dict(self):
        msg = AdtA43()

        result = msg.to_dict()

        assert result["_structure_id"] == "ADT_A43"

    def test_adt_a43_to_json(self):
        msg = AdtA43()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "ADT_A43"
