from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import ADT_A38


class TestAdtA38:
    """Comprehensive tests for AdtA38 message."""

    def test_adt_a38_create(self):
        msg = ADT_A38()
        assert msg._structure_id == "ADT_A38"

    def test_adt_a38_segment_access(self):
        msg = ADT_A38()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.evn._segment_id == "EVN"
        assert msg.pid._segment_id == "PID"
        assert msg.pd1._segment_id == "PD1"
        assert msg.pv1._segment_id == "PV1"
        assert msg.pv2._segment_id == "PV2"
        assert msg.drg._segment_id == "DRG"

    def test_adt_a38_to_dict(self):
        msg = ADT_A38()

        result = msg.to_dict()

        assert result["_structure_id"] == "ADT_A38"

    def test_adt_a38_to_json(self):
        msg = ADT_A38()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "ADT_A38"
