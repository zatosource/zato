from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import RDE_O11


class TestRdeO11:
    """Comprehensive tests for RdeO11 message."""

    def test_rde_o11_create(self):
        msg = RDE_O11()
        assert msg._structure_id == "RDE_O11"

    def test_rde_o11_segment_access(self):
        msg = RDE_O11()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"

    def test_rde_o11_to_dict(self):
        msg = RDE_O11()

        result = msg.to_dict()

        assert result["_structure_id"] == "RDE_O11"

    def test_rde_o11_to_json(self):
        msg = RDE_O11()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "RDE_O11"
