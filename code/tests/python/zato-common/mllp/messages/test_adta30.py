from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import ADT_A30


class TestAdtA30:
    """Comprehensive tests for AdtA30 message."""

    def test_adt_a30_create(self):
        msg = ADT_A30()
        assert msg._structure_id == "ADT_A30"

    def test_adt_a30_segment_access(self):
        msg = ADT_A30()

        assert msg.msh._segment_id == "MSH"
        assert msg.evn._segment_id == "EVN"
        assert msg.pid._segment_id == "PID"
        assert msg.pd1._segment_id == "PD1"
        assert msg.mrg._segment_id == "MRG"

    def test_adt_a30_to_dict(self):
        msg = ADT_A30()

        result = msg.to_dict()

        assert result["_structure_id"] == "ADT_A30"

    def test_adt_a30_to_json(self):
        msg = ADT_A30()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "ADT_A30"
