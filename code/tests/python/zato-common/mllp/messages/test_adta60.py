from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import ADT_A60


class TestAdtA60:
    """Comprehensive tests for AdtA60 message."""

    def test_adt_a60_create(self):
        msg = ADT_A60()
        assert msg._structure_id == "ADT_A60"

    def test_adt_a60_segment_access(self):
        msg = ADT_A60()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.evn._segment_id == "EVN"
        assert msg.pid._segment_id == "PID"

    def test_adt_a60_to_dict(self):
        msg = ADT_A60()

        result = msg.to_dict()

        assert result["_structure_id"] == "ADT_A60"

    def test_adt_a60_to_json(self):
        msg = ADT_A60()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "ADT_A60"
