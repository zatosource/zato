from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import ADT_A44


class TestAdtA44:
    """Comprehensive tests for AdtA44 message."""

    def test_adt_a44_create(self):
        msg = ADT_A44()
        assert msg._structure_id == "ADT_A44"

    def test_adt_a44_segment_access(self):
        msg = ADT_A44()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.evn._segment_id == "EVN"
        assert msg.pid._segment_id == "PID"
        assert msg.pd1._segment_id == "PD1"
        assert msg.mrg._segment_id == "MRG"

    def test_adt_a44_to_dict(self):
        msg = ADT_A44()

        result = msg.to_dict()

        assert result["_structure_id"] == "ADT_A44"

    def test_adt_a44_to_json(self):
        msg = ADT_A44()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "ADT_A44"
