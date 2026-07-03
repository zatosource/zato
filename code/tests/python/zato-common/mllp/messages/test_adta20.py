from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import ADT_A20


class TestAdtA20:
    """Comprehensive tests for AdtA20 message."""

    def test_adt_a20_create(self):
        msg = ADT_A20()
        assert msg._structure_id == "ADT_A20"

    def test_adt_a20_segment_access(self):
        msg = ADT_A20()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.evn._segment_id == "EVN"
        assert msg.npu._segment_id == "NPU"

    def test_adt_a20_to_dict(self):
        msg = ADT_A20()

        result = msg.to_dict()

        assert result["_structure_id"] == "ADT_A20"

    def test_adt_a20_to_json(self):
        msg = ADT_A20()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "ADT_A20"
