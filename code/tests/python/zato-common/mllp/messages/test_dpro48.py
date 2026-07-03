from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import DPR_O48


class TestDprO48:
    """Comprehensive tests for DprO48 message."""

    def test_dpr_o48_create(self):
        msg = DPR_O48()
        assert msg._structure_id == "DPR_O48"

    def test_dpr_o48_segment_access(self):
        msg = DPR_O48()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"

    def test_dpr_o48_to_dict(self):
        msg = DPR_O48()

        result = msg.to_dict()

        assert result["_structure_id"] == "DPR_O48"

    def test_dpr_o48_to_json(self):
        msg = DPR_O48()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "DPR_O48"
