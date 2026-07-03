from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import ADT_A43


class TestAdtA43:
    """Comprehensive tests for AdtA43 message."""

    def test_adt_a43_create(self):
        msg = ADT_A43()
        assert msg._structure_id == "ADT_A43"

    def test_adt_a43_segment_access(self):
        msg = ADT_A43()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.evn._segment_id == "EVN"

    def test_adt_a43_to_dict(self):
        msg = ADT_A43()

        result = msg.to_dict()

        assert result["_structure_id"] == "ADT_A43"

    def test_adt_a43_to_json(self):
        msg = ADT_A43()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "ADT_A43"
