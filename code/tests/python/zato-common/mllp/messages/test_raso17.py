from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import RAS_O17


class TestRasO17:
    """Comprehensive tests for RasO17 message."""

    def test_ras_o17_create(self):
        msg = RAS_O17()
        assert msg._structure_id == "RAS_O17"

    def test_ras_o17_segment_access(self):
        msg = RAS_O17()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"

    def test_ras_o17_to_dict(self):
        msg = RAS_O17()

        result = msg.to_dict()

        assert result["_structure_id"] == "RAS_O17"

    def test_ras_o17_to_json(self):
        msg = RAS_O17()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "RAS_O17"
