from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import RDE_O49


class TestRdeO49:
    """Comprehensive tests for RdeO49 message."""

    def test_rde_o49_create(self):
        msg = RDE_O49()
        assert msg._structure_id == "RDE_O49"

    def test_rde_o49_segment_access(self):
        msg = RDE_O49()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"

    def test_rde_o49_to_dict(self):
        msg = RDE_O49()

        result = msg.to_dict()

        assert result["_structure_id"] == "RDE_O49"

    def test_rde_o49_to_json(self):
        msg = RDE_O49()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "RDE_O49"
