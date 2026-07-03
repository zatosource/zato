from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import ADT_A39


class TestAdtA39:
    """Comprehensive tests for AdtA39 message."""

    def test_adt_a39_create(self):
        msg = ADT_A39()
        assert msg._structure_id == "ADT_A39"

    def test_adt_a39_segment_access(self):
        msg = ADT_A39()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.evn._segment_id == "EVN"

    def test_adt_a39_to_dict(self):
        msg = ADT_A39()

        result = msg.to_dict()

        assert result["_structure_id"] == "ADT_A39"

    def test_adt_a39_to_json(self):
        msg = ADT_A39()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "ADT_A39"
